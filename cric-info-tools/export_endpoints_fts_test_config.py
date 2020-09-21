#!/usr/bin/env python

import argparse
import requests
import logging
import json
import os

CRIC_RSES_URL = 'http://escape-cric.cern.ch/api/doma/rse/query/?json'

config_map = {}
config_map['protocols'] = {}
config_map['input_testing_folder'] = "fts-tests"
config_map['output_testing_folder'] = "fts-tests-dest"
config_map['num_of_jobs'] = 1
config_map['num_of_files'] = [4]
config_map['filesizes'] = [10]
config_map['checksum'] = "none"
config_map['overwrite'] = False


def main():

    parser = argparse.ArgumentParser(
        description="Export datalake rses for bash.")

    parser.add_argument("-o",
                        required=True,
                        dest="export_file",
                        help="")

    arg = parser.parse_args()
    export_file = str(arg.export_file)

    logging.basicConfig(format='%(asctime)s %(message)s',
                        datefmt='%d/%m/%Y %I:%M:%S %p', level=logging.INFO)
    logger = logging.getLogger()

    with open(export_file, 'w') as fp:
        cric_rse_data = requests.get(CRIC_RSES_URL).json()
        for rse in cric_rse_data:

            rse_label = rse.replace("-", "_").lower()

            protocols = cric_rse_data[rse]['protocols']
            for protocol_label in protocols:
                protocol = protocols[protocol_label]
                protocol_name = protocol['flavour']
                endpoint = protocol['endpoint']
                path = protocol['path']
                endpoint_url = "{}{}".format(endpoint, path)

                if protocol_name in config_map['protocols']:
                    config_map['protocols'][protocol_name].append(endpoint_url)
                else:
                    config_map['protocols'][protocol_name] = []

        fp.write(json.dumps(config_map, indent=4))


if __name__ == '__main__':
    main()
