#!/usr/bin/env python

import argparse
import requests
import logging
import os

CRIC_RSES_URL = 'http://escape-cric.cern.ch/api/doma/rse/query/?json'


def main():

    parser = argparse.ArgumentParser(
        description="Export datalake sites for bash list.")

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

    with open(export_file, 'w+') as fp:
        cric_rse_data = requests.get(CRIC_RSES_URL).json()
        for rse in cric_rse_data:
            # logger.info("Exporting {}".format(rse))
            if rse in disabled_rses:
                continue
            fp.write(rse + "\n")


if __name__ == '__main__':
    main()
