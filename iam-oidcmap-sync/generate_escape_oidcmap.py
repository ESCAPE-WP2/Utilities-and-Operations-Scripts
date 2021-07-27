import os
import requests
import json
from configparser import ConfigParser

import logging
logging.basicConfig(level=logging.DEBUG)

CONFIG_PATH = "./iam-oidcmap.conf"


class IAM_OIDC_Map_Generator():

    TOKEN_URL = "/token"
    GET_USERS_URL = "/scim/Users"

    def __init__(self, config_path):
        self.config_path = config_path
        self.configure()

    def generate(self):
        access_token = self.get_token()
        users = self.get_list_of_users(access_token)
        user_ids = self.extract_user_ids(users)
        self.write_mapfile(user_ids, self.default_role, self.output_path)

    def configure(self):
        self.iam_server = None
        self.default_role = 'ops001'
        self.client_id = None
        self.client_secret = None
        self.token_server = None
        self.output_path = None

        config = ConfigParser()
        files_read = config.read(self.config_path)
        if len(files_read) > 0:
            self.iam_server = config.get('IAM', 'iam-server')
            self.default_role = config.get('IAM', 'default-role')
            self.client_id = config.get('IAM', 'client-id')
            self.output_path = config.get('IAM', 'output_path')

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
        self.output_path = os.getenv('IAM_OUTPUT_PATH', self.output_path)
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
        r = requests.post(self.token_server +
                          self.TOKEN_URL, data=request_data)
        
        responce = json.loads(r.text)

        if 'access_token' not in responce:
            raise BaseException("Authentication Failed")

        return responce['access_token']

    def get_list_of_users(self, access_token):
        """
        Queries the server for all users belonging to the VO.
        """

        startIndex = 1
        count = 100
        header = {"Authorization": "Bearer %s" % access_token}

        iam_users = []
        users_so_far = 0

        while True:
            params_d = {"startIndex": startIndex, "count": count}
            response = requests.get("%s/scim/Users" % self.iam_server,
                                    headers=header,
                                    params=params_d)
            response = json.loads(response.text)

            iam_users += response['Resources']
            users_so_far += response['itemsPerPage']

            if users_so_far < response['totalResults']:
                startIndex += count
            else:
                break

        # TODO: Handle exceptions, error codes
        return iam_users

    def extract_user_ids(self, users):
        user_ids = []
        for user in users:
            user_ids.append(user['id'])
        return user_ids

    def write_mapfile(self, user_ids, role, path):
        with open(path, 'w') as output:
            for user_id in user_ids:
                line = '%s %s\n' % (user_id, role)
                output.write(line)


if __name__ == '__main__':
    logging.info(
        "* Sync to IAM (OIDC Mapping) * Initializing IAM-OIDC Map synchronization script."
    )
    grid_test = IAM_OIDC_Map_Generator(CONFIG_PATH)
    grid_test.generate()

    logging.info("* Sync to IAM (OIDC Mapping) * Successfully completed.")
