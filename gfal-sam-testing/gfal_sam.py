import subprocess
import colorama
import requests
import argparse
import uuid
import time
import json
import os
from colorama import Fore
from datetime import datetime

CRIC_URL = os.getenv(
    "CRIC_URL",
    "http://escape-cric.cern.ch/api/doma/rse/query/?json&preset=doma")
GFAL_LOCALPATH = os.getenv("GFAL_LOCALPATH", "./")


class SAM_TEST():

    def __init__(self, endpoint, port, protocol, prefix):
        self.endpoint = endpoint
        self.port = port
        self.protocol = protocol
        self.prefix = prefix
        self.timeout = "120"  # 2 minutes

    def upload(self, local_filename, remote_filename):
        target = "{protocol}://{hostname}:{port}{prefix}/{filename}".format(
            protocol=self.protocol,
            hostname=self.endpoint,
            port=self.port,
            prefix=self.prefix,
            filename=remote_filename)
        status, error_code = self._call([
            "gfal-copy", "--force", "--checksum-mode", "both", "--timeout",
            self.timeout, local_filename, target
        ])
        return status, error_code

    def download(self, local_filename, remote_filename):
        target = "{protocol}://{hostname}:{port}{prefix}/{filename}".format(
            protocol=self.protocol,
            hostname=self.endpoint,
            port=self.port,
            prefix=self.prefix,
            filename=remote_filename)
        status, error_code = self._call([
            "gfal-copy", "--checksum-mode", "both", "--timeout", self.timeout,
            target, local_filename
        ])
        return status, error_code

    def delete(self, remote_filename):
        target = "{protocol}://{hostname}:{port}{prefix}/{filename}".format(
            protocol=self.protocol,
            hostname=self.endpoint,
            port=self.port,
            prefix=self.prefix,
            filename=remote_filename)
        status, error_code = self._call(["gfal-rm", target])
        return status, error_code

    def generate_file(self, filepath):
        f = open(filepath, "w+")
        f.write("Gfal-copy,rm testing" + self.protocol)
        f.close

    def delete_local_file(self, filepath):
        os.remove(filepath)

    def _call(self, command_array):
        try:
            print("CALL: {}".format(command_array), flush=True)
            process = subprocess.Popen(command_array,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
            out, err = process.communicate()
            out = out.decode("utf-8")
            err = err.decode("utf-8")
            if err:
                print(Fore.RED + "FAILED : {}".format(err), flush=True)
                return "FAILED", err
            else:
                print(Fore.GREEN + "SUCCESS", flush=True)
                return "SUCCESS", "None"
        except Exception as e:
            print(Fore.RED + "FAILED [Exception]", e, flush=True)
            return "FAILED", e


def get_protocols():
    data = requests.get(CRIC_URL).json()
    protocols = []
    for rse in data['rses']:
        for protocol in data['rses'][rse]['protocols']:
            protocol_json = {
                'site': rse,
                'hostname': protocol['hostname'],
                'port': protocol['port'],
                'scheme': protocol['scheme'],
                'prefix': protocol['prefix']
            }
            protocols.append(protocol_json)
    return protocols


def check_protocol(site, hostname, port, protocol, path, auth):

    print("{}:{}".format(site, protocol), flush=True)

    filename = "sam_gfal_test" + str(uuid.uuid4())
    sam = SAM_TEST(hostname, port, protocol, path)
    sam.generate_file(GFAL_LOCALPATH + filename)
    print("UPLOAD : ", end='', flush=True)
    upload_status, error_code = sam.upload(GFAL_LOCALPATH + filename, filename)
    upload_json = {
        "site": site,
        "endpoint": hostname,
        "port": port,
        "protocol": protocol,
        "path": path,
        "operation": 'UPLOAD',
        "status": upload_status,
        "error_code": error_code,
        "auth_method": auth,
        "str_datetime": str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        "timestamp": int(time.time()),
        "vo": "ESCAPE",
        "producer": "escape_wp2",
        "type": "sam_gfal"
    }

    if upload_status == "SUCCESS":
        sam.delete_local_file(GFAL_LOCALPATH + filename)
        print("DOWNLOAD : ", end='', flush=True)
        download_status, error_code = sam.download(
            remote_filename=filename, local_filename=GFAL_LOCALPATH + filename)
    else:
        download_status, error_code = "SKIPPED", "None"

    download_json = {
        "site": site,
        "endpoint": hostname,
        "port": port,
        "protocol": protocol,
        "path": path,
        "operation": 'DOWNLOAD',
        "status": download_status,
        "error_code": error_code,
        "auth_method": auth,
        "str_datetime": str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        "timestamp": int(time.time()),
        "vo": "ESCAPE",
        "producer": "escape_wp2",
        "type": "sam_gfal"
    }
    if download_status == "SUCCESS":
        print("DELETE : ", end='', flush=True)
        delete_status, error_code = sam.delete(filename)
    else:
        delete_status, error_code = "SKIPPED", "None"

    delete_json = {
        "site": site,
        "endpoint": hostname,
        "port": port,
        "protocol": protocol,
        "path": path,
        "operation": 'DELETE',
        "status": delete_status,
        "error_code": error_code,
        "auth_method": auth,
        "str_datetime": str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        "timestamp": int(time.time()),
        "vo": "ESCAPE",
        "producer": "escape_wp2",
        "type": "sam_gfal"
    }

    sam.delete_local_file(GFAL_LOCALPATH + filename)
    return [upload_json, download_json, delete_json]


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("-i",
                        required=False,
                        dest="input_file",
                        help="List of RSEs that are not to be tested")
    parser.add_argument("-auth",
                        required=False,
                        dest="auth_type",
                        default="x509",
                        help="Auth type to use [x509(default)|oidc]")

    arg = parser.parse_args()
    input_file = str(arg.input_file)
    auth_type = str(arg.auth_type)

    disabled_rses = []
    if input_file != 'None':
        with open(input_file) as f:
            content = f.readlines()
        disabled_rses = [x.strip() for x in content]

    colorama.init(autoreset=True)
    print("Fetching data from CRIC..", flush=True)
    protocols = get_protocols()
    for protocol in protocols:
        if protocol['site'] in disabled_rses:
            continue
        if protocol['scheme'] != "davs" and auth_type == 'oidc':
            continue
        print("<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>", flush=True)
        result = check_protocol(protocol['site'], protocol['hostname'],
                                protocol['port'], protocol['scheme'],
                                protocol['prefix'] + '/gfal_sam/testing',
                                auth_type)
        code = requests.post(
            'http://monit-metrics:10012/',
            data=json.dumps(result),
            headers={"Content-Type": "application/json; charset=UTF-8"})
        print("Pushing to ES [http:{}]".format(code.status_code), flush=True)
