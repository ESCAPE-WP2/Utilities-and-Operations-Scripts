#!/usr/bin/env python
#
# Copyright European Organization for Nuclear Research (CERN)

# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#                       http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Hannes Hansen, <hannes.jakob.hansen@cern.ch>, 2019
# - Aristeidis Fkiaras <aristeidis.fkiaras@cern.ch>, 2019
# - Rizart Dona <rizart.dona@cern.ch>, 2020-2021
#
# Import CRIC data into rucio
#
# PY3K COMPATIBLE

import requests
from rucio.core.importer import import_rses, import_distances
from rucio.core import rse as rse_module
from rucio.common.exception import RSENotFound

CRIC_URL = 'https://escape-cric.cern.ch/api/doma/rse/query/?json'
CRIC_URL_D = 'https://escape-cric.cern.ch/api/doma/rse/query/?json&preset=doma'


def format_protocols(protocols, impl):
    new_protocols = []
    for protocol in protocols:
        cric_prot = protocol
        if len(cric_prot["ext_attrs"]) < 1:
            ext_attrs = None
        else:
            ext_attrs = cric_prot["ext_attrs"]
        
        cric_prot['domains']['wan']['third_party_copy_read'] = cric_prot['domains']['third_party_copy'].get("read", 0)
        cric_prot['domains']['wan']['third_party_copy_write'] = cric_prot['domains']['third_party_copy'].get("write", 0)
        cric_prot['domains'].pop('third_party_copy', None)

        protocol = {
            "extended_attributes": ext_attrs,
            "hostname": cric_prot["hostname"],
            "prefix": cric_prot["prefix"],
            "domains": cric_prot["domains"],
            "scheme": cric_prot["scheme"],
            "port": int(cric_prot["port"]),
            "impl": impl
        }
        new_protocols.append(protocol)
    return new_protocols


def format_rses(rses_d, rses):
    new_rses = {}

    for rse in rses_d:
        rse_name = rse
        cric_data = rses_d[rse]

        attributes_map = {
            rse_name: "true",
            "source_for_used_space": "rucio",
            "fts": cric_data["fts"],
            "verify_checksum": rses[rse]['verify_checksum'],
            "lfn2pfn_algorithm": cric_data["lfn2pfn_algorithm"]
        }

        # add custom CRIC parameters for RSE
        custom_params = cric_data['params']
        for k, v in custom_params.items():
            attributes_map[k] = v

        # set default rse_type to DISK if not provided
        if not cric_data["rse_type"]:
            cric_data["rse_type"] = "DISK"

        try:
            rse_id = rse_module.get_rse_id(rse=rse_name)
            total_space = cric_data["space"]

            if total_space > 0:
                rse_module.set_rse_usage(rse_id,
                                         "storage",
                                         -1,
                                         total_space,
                                         files=None)
                rse_module.set_rse_usage(rse_id,
                                         "obsolete",
                                         0,
                                         None,
                                         files=None)
        except RSENotFound:
            # this means that the rse usage metrics will be updated in the next
            # run for this RSE
            pass

        data = {
            "MaxBeingDeletedFiles":
                cric_data["MaxBeingDeletedFiles"],
            "MinFreeSpace":
                cric_data["MinFreeSpace"],
            "availability_delete":
                cric_data["availability_delete"],
            "availability_read":
                cric_data["availability_read"],
            "availability_write":
                cric_data["availability_write"],
            "country_name":
                cric_data["country_name"],
            "deterministic":
                cric_data["deterministic"],
            "fts":
                cric_data["fts"],
            "impl":
                cric_data["impl"],
            "latitude":
                cric_data["latitude"],
            "lfn2pfn_algorithm":
                cric_data["lfn2pfn_algorithm"],
            "longitude":
                cric_data["longitude"],
            "region_code":
                cric_data["region_code"],
            "rse":
                rse_name,
            "rse_type":
                cric_data["rse_type"],
            "staging_area":
                cric_data["staging_area"],
            "timezone":
                cric_data["timezone"],
            "updated_at":
                cric_data["updated_at"],
            "volatile":
                cric_data["volatile"],

            # Missing from CRIC
            "city":
                "Missing from CRIC",
            "availability":
                "7",
            "credentials":
                "null",
            "created_at":
                "",
            "verify_checksum":
                rses[rse]['verify_checksum'],
            "attributes":
                attributes_map,

            # Protocols
            "protocols":
                format_protocols(cric_data["protocols"], cric_data["impl"])
        }
        new_rses[rse_name] = data
    return new_rses


if __name__ == '__main__':

    # fetch the data via the REST API
    cric_verification_cert = "/etc/grid-security/certificates/CERN-Root-2.pem"
    rses_d = requests.get(CRIC_URL_D,
                          verify=cric_verification_cert).json()['rses']
    rses = requests.get(CRIC_URL, verify=cric_verification_cert).json()
    distances = requests.get(CRIC_URL_D,
                             verify=cric_verification_cert).json()['distances']

    # format rses and make the importable
    new_rses = format_rses(rses_d, rses)
    import_rses(new_rses)

    # distances do not need formatting
    import_distances(distances)
