import os
import requests
import json
from configparser import ConfigParser
from rucio.common.types import InternalAccount
from rucio.core import identity, account, rse
from rucio.db.sqla.constants import IdentityType
from rucio.db.sqla.session import get_session
from rucio.db.sqla.constants import AccountType
from rucio.core.account_limit import set_local_account_limit
from rucio.core.account import add_account_attribute

import logging

logging.basicConfig(level=logging.DEBUG)

CONFIG_PATH = "./iam-sync.conf"


class IAM_RUCIO_SYNC():

    TOKEN_URL = "/token"
    GET_USERS_URL = "/scim/Users"

    def __init__(self, config_path):
        self.config_path = config_path
        self.configure()

    def generate(self):
        access_token = self.get_token()
        users = self.get_list_of_users(access_token)
        # DEBUG output to file
        # with open("get_list_of_users.json", "w") as outfile:
        #     json.dump(users, outfile, indent=4)
        self.user_details = self.extract_certificates(users)

    def configure(self):
        self.iam_server = None
        self.client_id = None
        self.client_secret = None
        self.token_server = None

        config = ConfigParser()
        files_read = config.read(self.config_path)
        if len(files_read) > 0:
            self.iam_server = config.get('IAM', 'iam-server')
            self.client_id = config.get('IAM', 'client-id')

            if config.has_option('IAM', 'client-secret'):
                self.client_secret = config.get('IAM', 'client-secret')
            else:
                client_secret_path = config.get('IAM', 'client-secret-path')
                with open(client_secret_path, 'r') as client_secret_file:
                    self.client_secret = client_secret_file.read().rstrip()

            if config.has_option('IAM', 'token-server'):
                self.token_server = config.get('IAM', 'token-server')
            else:
                self.token_server = self.iam_server

        # Overwrite config with ENV variables
        self.iam_server = os.getenv('IAM_SERVER', self.iam_server)
        self.client_id = os.getenv('IAM_CLIENT_ID', self.client_id)
        self.client_secret = os.getenv('IAM_CLIENT_SECRET', self.client_secret)
        self.token_server = os.getenv('IAM_TOKEN_SERVER', self.token_server)
        if self.token_server is None:
            self.token_server = self.iam_server

        # Validate all required settings are set or throw exception
        # TODO

    def get_token(self):
        """
        Authenticates with the iam server and returns the access token.
        """
        request_data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials",
            "username": "not_needed",
            "password": "not_needed",
            "scope": "scim:read"
        }
        r = requests.post(self.token_server + self.TOKEN_URL, data=request_data)
        response = json.loads(r.text)

        if 'access_token' not in response:
            raise BaseException("Authentication Failed")

        return response['access_token']

    def get_list_of_users(self, access_token):
        """
        Queries the server for all users belonging to the VO.
        """
        header = {"Authorization": "Bearer %s" % access_token}
        r = requests.get("%s/scim/Users" % self.iam_server, headers=header)
        # TODO: Handle exceptions, error codes
        return json.loads(r.text)

    def make_gridmap_compatible(self, certificate):
        """
        Take a certificate and make it compatible with the gridmap format.
        Basically reverse it and replace ',' with '/'
        """
        certificate = certificate.split(',')
        certificate.reverse()
        certificate = '/'.join(certificate)
        certificate = '/' + certificate
        return certificate

    def extract_certificates(self, users):
        grid_certificates = []
        for user in users['Resources']:
            if 'urn:indigo-dc:scim:schemas:IndigoUser' in user:
                indigo_user = user['urn:indigo-dc:scim:schemas:IndigoUser']
                if 'certificates' in indigo_user:
                    for certificate in indigo_user['certificates']:
                        if 'subjectDn' in certificate:
                            grid_certificate = self.make_gridmap_compatible(
                                certificate['subjectDn'])
                            grid_certificates.append([
                                user['userName'], user['emails'][0]['value'],
                                grid_certificate, user['id']
                            ])
        return grid_certificates

    def sync(self):
        session = get_session()
        session.connection()
        for user in self.user_details:
            username = user[0]
            email = user[1]
            dn = user[2]
            user_subject = user[3]
            if not account.account_exists(InternalAccount(username)):
                account.add_account(InternalAccount(username),
                                    AccountType.SERVICE, email)
                logging.debug('Created account for User ***')

            try:
                identity.add_account_identity(dn, IdentityType.X509,
                                              InternalAccount(username), email)
                logging.debug(
                    'Added X509 identity for User {} ***'.format(username))
            except:
                logging.debug(
                    'Did not add X509 identify for User {} ***'.format(
                        username))

            try:
                user_identity = "SUB={}, ISS={}".format(user_subject,
                                                        self.iam_server)
                identity.add_account_identity(user_identity, IdentityType.OIDC,
                                              InternalAccount(username), email)
                logging.debug(
                    'Added OIDC identity for User {} ***'.format(username))
            except:
                logging.debug(
                    'Did not add OIDC identify for User {} ***'.format(
                        username))

            # Give account quota for all RSEs
            for rse_obj in rse.list_rses():
                set_local_account_limit(InternalAccount(username),
                                        rse_obj['id'], 1000000000000)

            # Make the user an admin
            try:
                add_account_attribute(InternalAccount(username), 'admin',
                                      'True')
            except:
                pass


if __name__ == '__main__':
    logging.info(
        "* Sync to IAM * Initializing IAM-RUCIO synchronization script.")
    syncer = IAM_RUCIO_SYNC(CONFIG_PATH)
    syncer.generate()

    syncer.sync()
    logging.info("* Sync to IAM * Successfully completed.")
