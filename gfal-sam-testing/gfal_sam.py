import subprocess
import uuid
import os
import time
import requests
import json
from datetime import datetime


class SAM_TEST():

    def __init__(self, endpoint, port, protocol, prefix):
        self.endpoint = endpoint
        self.port = port
        self.protocol = protocol
        self.prefix = prefix
        self.timeout = "300"

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
            print("CALL:", command_array)
            process = subprocess.Popen(command_array,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
            out, err = process.communicate()
            out = out.decode("utf-8")
            err = err.decode("utf-8")
            if err:
                print("FAILED", err)
                return "FAILED", err
            else:
                print("SUCCESS")
                return "SUCCESS", "None"
        except Exception as e:
            print("FAILED [Exception]", e)
            return "FAILED", e


CRIC_URL = os.getenv(
    "CRIC_URL",
    "http://escape-cric.cern.ch/api/doma/rse/query/?json&preset=doma")
GFAL_LOCALPATH = os.getenv("GFAL_LOCALPATH", "./")


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


def check_protocol(site, hostname, port, protocol, path):

    filename = "sam_gfal_test" + str(uuid.uuid4())
    sam = SAM_TEST(hostname, port, protocol, path)
    sam.generate_file(GFAL_LOCALPATH + filename)
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
        "str_datetime": str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        "timestamp": int(time.time()),
        "vo": "ESCAPE",
        "producer": "escape_wp2",
        "type": "sam_gfal"
    }

    if upload_status == "SUCCESS":
        sam.delete_local_file(GFAL_LOCALPATH + filename)
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
        "str_datetime": str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        "timestamp": int(time.time()),
        "vo": "ESCAPE",
        "producer": "escape_wp2",
        "type": "sam_gfal"
    }
    if download_status == "SUCCESS":
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
        "str_datetime": str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        "timestamp": int(time.time()),
        "vo": "ESCAPE",
        "producer": "escape_wp2",
        "type": "sam_gfal"
    }

    sam.delete_local_file(GFAL_LOCALPATH + filename)
    return [upload_json, download_json, delete_json]


if __name__ == "__main__":
    protocols = get_protocols()
    for protocol in protocols:
        result = check_protocol(protocol['site'], protocol['hostname'],
                                protocol['port'], protocol['scheme'],
                                protocol['prefix'] + '/gfal_sam/testing')
        code = requests.post(
            'http://monit-metrics:10012/',
            data=json.dumps(result),
            headers={"Content-Type": "application/json; charset=UTF-8"})
        print("Pushing to ES [http:{}]".format(code.status_code))
        print("<<<<<<<<<<<<<<<<<<<<<<<")
