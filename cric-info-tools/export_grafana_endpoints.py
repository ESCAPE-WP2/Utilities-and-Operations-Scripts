#!/usr/bin/env python

import argparse
import requests
import logging
import os

CRIC_RSES_URL = 'http://escape-cric.cern.ch/api/doma/rse/query/?json'


def main():

    parser = argparse.ArgumentParser(
        description="Export datalake rse endpoints for Grafana dashboards.")

    parser.add_argument("-i", required=False, dest="input_file", help="")

    arg = parser.parse_args()
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

    endpoints = []
    cric_rse_data = requests.get(CRIC_RSES_URL).json()
    for rse in cric_rse_data:
        if rse in disabled_rses:
            continue
        logger.info("Exporting {}".format(rse))
        protocols = cric_rse_data[rse]['protocols']
        for protocol_label in protocols:
            protocol = protocols[protocol_label]
            endpoint = protocol['endpoint'].split(":", 1)[0]
            if endpoint not in endpoints:
                endpoints.append(endpoint)

    endpnt_string = ''
    for endpoint in endpoints:
        endpnt_string += endpoint + ','
    endpnt_string = endpnt_string[:-1]
    print(endpnt_string)


if __name__ == '__main__':
    main()
