import os
import requests
import json
from configparser import ConfigParser
from rucio.db.sqla.session import get_session
from rucio.core.rse import list_rses, get_rse_protocols

import logging
logging.basicConfig(level=logging.DEBUG)

CONFIG_PATH = "./xcache-sync.conf"


class XCache_Authfile_Generator():

    def __init__(self, config_path):
        self.config_path = config_path
        self.configure()

    def generate(self):
        prefixes = self.get_authfile_prefixes()
        outfile = self.get_template_authfile_from_prefixes(prefixes)

        with open(self.output_path, 'w') as output:
            output.write(outfile)

    def configure(self):
        self.template_name = 'datalakepaths'
        self.permission = 'lr'
        self.output_path = None

        config = ConfigParser()
        files_read = config.read(self.config_path)
        if len(files_read) > 0:
            self.template_name = config.get('xcache', 'template_name')
            self.permission = config.get('xcache', 'permission')
            self.output_path = config.get('xcache', 'output_path')

        # Overwrite config with ENV variables
        self.template_name = os.getenv('TEMPLATE_NAME', self.template_name)
        self.permission = os.getenv('PERMISSION', self.permission)
        self.output_path = os.getenv('OUTPUT_PATH', self.output_path)

    def get_authfile_prefixes(self):
        session = get_session()
        session.connection()

        prefixes = set()
        for rse in list_rses():
            rse_name = rse['rse']
            protocols = get_rse_protocols(rse_name)
            for protocol in protocols:
                scheme = protocol['scheme']
                hostname = protocol['hostname']
                port = protocol['port']
                prefix = protocol['prefix']
                authfile_prefix = f"/{scheme}:/{hostname}:{port}{prefix}"
                prefixes.add(authfile_prefix)
        return list(prefixes)

    def get_template_authfile_from_prefixes(self, prefixes):
        out = f"t {self.template_name}"
        left_pad = len(out) + 2
        for i in range(len(prefixes)):
            prefix = prefixes[i]
            if i > 0:
                out += ' ' * left_pad
            else:
                out += ' ' * 2

            out += f"{prefix} {self.permission}"
            if i < len(prefixes) - 1:
                out += " \\"
            out += "\n"
        return out


if __name__ == '__main__':
    logging.info(
        "* Sync to XCache (Authfile) * Initializing Rucio RSE-XCache Authfile synchronization script."
    )
    generator = XCache_Authfile_Generator(CONFIG_PATH)
    generator.generate()

    logging.info("* Sync to XCache (Authfile) * Successfully completed.")
