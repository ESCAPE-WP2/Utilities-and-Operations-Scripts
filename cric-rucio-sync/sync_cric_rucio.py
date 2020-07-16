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
#
# Import CRIC data into rucio
#
# PY3K COMPATIBLE

import requests
from rucio.core.importer import import_rses, import_distances, import_accounts
from rucio.common.types import InternalAccount

CRIC_URL = 'http://escape-cric.cern.ch/api/doma/rse/query/?json&preset=doma'
CRIC_URL_ACCOUNTS = 'http://escape-cric.cern.ch/api/accounts/user/query/?json'


def format_protocols(protocols, impl):
    new_protocols = []
    for protocol in protocols:
        cric_prot = protocol
        if len(cric_prot["ext_attrs"]) < 1:
            ext_attrs = None
        else:
            ext_attrs = cric_prot["ext_attrs"]
        protocol = {
            "extended_attributes": ext_attrs,
            "hostname": cric_prot["hostname"],
            "prefix": cric_prot["prefix"],
            "domains": cric_prot["domains"],
            "scheme": cric_prot["scheme"],
            "port": long(cric_prot["port"]),
            "impl": impl
        }
        new_protocols.append(protocol)
    return new_protocols


def format_rses(rses):
    new_rses = {}
    for rse in rses:
        rse_name = rse
        cric_data = rses[rse]
        data = {
            "MaxBeingDeletedFiles": cric_data["MaxBeingDeletedFiles"],
            "MinFreeSpace": cric_data["MinFreeSpace"],
            "availability_delete": cric_data["availability_delete"],
            "availability_read": cric_data["availability_read"],
            "availability_write": cric_data["availability_write"],
            "country_name": cric_data["country_name"],
            "deterministic": cric_data["deterministic"],
            "fts": cric_data["fts"],
            "impl": cric_data["impl"],
            "latitude": cric_data["latitude"],
            "lfn2pfn_algorithm": cric_data["lfn2pfn_algorithm"],
            "longitude": cric_data["longitude"],
            "region_code": cric_data["region_code"],
            "rse": rse_name,
            "rse_type": cric_data["rse_type"],
            "staging_area": cric_data["staging_area"],
            "timezone": cric_data["timezone"],
            "updated_at": cric_data["updated_at"],
            "volatile": cric_data["volatile"],

            # Data visible on CRIC but not on Rucio
            # "id": 8, Might need to do get_rse_id("Name") or assign new one
            # "site": cric_data["site"],
            # "space_usage_method": "",
            # "state": "ACTIVE",

            # Missing from CRIC
            "city": "Missing from CRIC",
            "availability": "7",
            "credentials": "null",
            "created_at": "",
            "verify_checksum": "True",
            "attributes": {
                rse_name: "true",
                "fts": cric_data["fts"],
                "verify_checksum": "True",
                "lfn2pfn_algorithm": cric_data["lfn2pfn_algorithm"]
            },

            # Protocols
            "protocols": format_protocols(cric_data["protocols"], cric_data["impl"])
        }
        new_rses[rse_name] = data
    return new_rses


def format_identities(identities):
    new_identities = []
    for identity in identities:
        if 'dn' in identity:
            if len(identity['dn']) > 0:
                new_id = {
                    "identity": identity['dn'],
                    "type": "X509",
                    "email": identity['email']
                }
                new_identities.append(new_id)
    return new_identities


def format_accounts(accounts):
    new_accounts = []
    for account in accounts:
        account_dic = {}
        account_dic['account'] = InternalAccount(account)
        account_dic['email'] = accounts[account]['email']
        account_dic['identities'] = format_identities(accounts[account]['profiles'])
        new_accounts.append(account_dic)
    return new_accounts


if __name__ == '__main__':
    data = requests.get(CRIC_URL).json()
    rses = data['rses']
    new_rses = format_rses(rses)
    import_rses(new_rses)

    distances = data["distances"]
    import_distances(distances)

    cric_accounts = requests.get(CRIC_URL_ACCOUNTS).json()
    new_accounts = format_accounts(cric_accounts)
    # import_accounts(new_accounts)
