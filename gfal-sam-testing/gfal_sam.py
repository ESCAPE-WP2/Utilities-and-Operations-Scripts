import subprocess
import uuid
import os
import time
import requests
import json


class SAM_TEST():

    def __init__(self, endpoint, port, protocol, prefix):
        self.endpoint = endpoint
        self.port = port
        self.protocol = protocol
        self.prefix = prefix

    def upload(self, local_filename, remote_filename):
        target = "{protocol}://{hostname}:{port}{prefix}/{filename}".format(protocol=self.protocol, hostname=self.endpoint, port=self.port, prefix=self.prefix, filename=remote_filename)
        status = self._call(["gfal-copy", "-f", local_filename, target])
        return status

    def download(self, local_filename, remote_filename):
        target = "{protocol}://{hostname}:{port}{prefix}/{filename}".format(protocol=self.protocol, hostname=self.endpoint, port=self.port, prefix=self.prefix, filename=remote_filename)
        status = self._call(["gfal-copy", target, local_filename])
        return status

    def delete(self, remote_filename):
        target = "{protocol}://{hostname}:{port}{prefix}/{filename}".format(protocol=self.protocol, hostname=self.endpoint, port=self.port, prefix=self.prefix, filename=remote_filename)
        status = self._call(["gfal-rm", target])
        return status

    def generate_file(self, filepath):
        f = open(filepath, "w+")
        f.write("Gfal-copy,rm testing" + self.protocol)
        f.close

    def delete_local_file(self, filepath):
        os.remove(filepath)

    def _call(self, command_array):
        try:
            print(command_array)
            subprocess.check_call(command_array)
            return "SUCCESS"
        except Exception as e:
            print(str(e))
            return "FAILED"


LOCALPATH = "/afs/cern.ch/user/a/afkiaras/gfal_sam/"
CRIC_URL = "http://escape-cric.cern.ch/api/doma/rse/query/?json&preset=doma"


def get_protocols():
    data = requests.get(CRIC_URL).json()
    protocols = []
    for rse in data['rses']:
        for protocol in data['rses'][rse]['protocols']:
            protocol_json = {'site':rse, 'hostname': protocol['hostname'], 'port': protocol['port'], 'scheme':protocol['scheme'], 'prefix': protocol['prefix']}
            protocols.append(protocol_json)
    return protocols


def check_protocol(site, hostname, port, protocol, path):

    filename = "sam_gfal_test" + str(uuid.uuid4())
    sam = SAM_TEST(hostname, port, protocol, path)
    sam.generate_file(filename)
    upload_status = sam.upload(LOCALPATH + filename, filename)
    upload_json = {
        "site": site,
        "endpoint": hostname,
        "port": port,
        "protocol": protocol,
        "path": path,
        "operation": 'UPLOAD',
        "status": upload_status,
        "timestamp": int(time.time()),
        "vo": "ESCAPE",
        "producer": "escape_wp2",
        "type": "sam_gfal"
    }

    if upload_status == "SUCCESS":
        sam.delete_local_file(LOCALPATH + filename)
        download_status = sam.download(remote_filename=filename, local_filename=LOCALPATH + filename)
    else:
        download_status = "SKIPPED"

    download_json = {
        "site": site,
        "endpoint": hostname,
        "port": port,
        "protocol": protocol,
        "path": path,
        "operation": 'DOWNLOAD',
        "status": download_status,
        "timestamp": int(time.time()),
        "vo": "ESCAPE",
        "producer": "escape_wp2",
        "type": "sam_gfal"
    }
    if download_status == "SUCCESS":
        delete_status = sam.delete(filename)
    else:
        delete_status = "SKIPPED"

    delete_json = {
        "site": site,
        "endpoint": hostname,
        "port": port,
        "protocol": protocol,
        "path": path,
        "operation": 'DELETE',
        "status": delete_status,
        "timestamp": int(time.time()),
        "vo": "ESCAPE",
        "producer": "escape_wp2",
        "type": "sam_gfal"
    }

    sam.delete_local_file(LOCALPATH + filename)
    return [upload_json, download_json, delete_json]


if __name__ == "__main__":
    protocols = get_protocols()
    for protocol in protocols:
        result = check_protocol(protocol['site'], protocol['hostname'], protocol['port'], protocol['scheme'], protocol['prefix'] + '/gfal_sam/testing')
        requests.post('http://monit-metrics:10012/', data=json.dumps(result), headers={ "Content-Type": "application/json; charset=UTF-8"})
