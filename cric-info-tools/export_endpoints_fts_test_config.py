#!/usr/bin/env python

import argparse
import requests
import logging
import json
import os

CRIC_RSES_URL = 'http://escape-cric.cern.ch/api/doma/rse/query/?json'

config_map = {
    "protocols": {},
    "testing_folder": "fts-testing",
    "num_of_jobs": 1,
    "num_of_files": [4],
    "filesizes": [1],
    "checksum": "none",
    "overwrite": False,
    "metadata": {
        "activity": "functional-testing"
    }
}


def main():

    parser = argparse.ArgumentParser(
        description="Export datalake rses for fts-analysis.")

    parser.add_argument("-o", required=True, dest="export_file", help="")
    parser.add_argument("-i", required=False, dest="input_file", help="")

    arg = parser.parse_args()
    export_file = str(arg.export_file)
    input_file = str(arg.input_file)

    logging.basicConfig(format='%(asctime)s %(message)s',
                        datefmt='%d/%m/%Y %I:%M:%S %p',
                        level=logging.INFO)
    logger = logging.getLogger()

    disabled_rses = []
    if input_file != 'None':
        with open(input_file) as f:
            content = f.readlines()
        disabled_rses = [x.strip() for x in content]

    with open(export_file, 'w') as fp:
        cric_rse_data = requests.get(CRIC_RSES_URL).json()
        for rse in cric_rse_data:
            if rse in disabled_rses:
                continue
            logger.info("Exporting {}".format(rse))
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
                    config_map['protocols'][protocol_name].append(endpoint_url)

        fp.write(json.dumps(config_map, indent=4))


if __name__ == '__main__':
    main()
