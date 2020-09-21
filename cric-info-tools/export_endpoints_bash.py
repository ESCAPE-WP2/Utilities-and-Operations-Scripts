#!/usr/bin/env python

import argparse
import requests
import logging
import os

CRIC_RSES_URL = 'http://escape-cric.cern.ch/api/doma/rse/query/?json'
EXPORT_PREFIX = "escape"


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

    with open(export_file, 'w+') as fp:
        fp.write("#!/bin/bash\n\n")
        # export bash info
        cric_rse_data = requests.get(CRIC_RSES_URL).json()
        for rse in cric_rse_data:
            logger.info("Exporting {}".format(rse))
            rse_label = rse.replace("-", "_").lower()
            fp.write("# {}\n".format(rse))
            protocols = cric_rse_data[rse]['protocols']
            for protocol_label in protocols:
                protocol = protocols[protocol_label]
                protocol_name = protocol['flavour']
                endpoint = protocol['endpoint']
                path = protocol['path']
                endpoint_url = "{}://{}{}".format(protocol_name,
                                                  endpoint, path)
                fp.write("export {}_{}_{}='{}'\n".format(
                    EXPORT_PREFIX, rse_label, protocol_name, endpoint_url))

            fp.write("\n")


if __name__ == '__main__':
    main()
