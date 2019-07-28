import unittest

import falcon

from gyma.vdv.Tests.Base.BaseTestCase import BaseTestCase
from gyma.vdv.Tests.Base.test_helpers import load_from_json_file, TEST_ACCOUNT

from gyma.vdv.Entities.EntityAccount import EntityAccount

from gyma.vdv.db import DBConnection


TEST_PARAMETERS_PATH = './account.json'


class UpdateUserTests(BaseTestCase):

    # setUp & tearDown

    def setUp(self):
        operation_id = 'updateUser'
        self.check_operation_id_has_operation_handler(operation_id)
        self.request_uri_path = self.get_request_uri_path(operation_id)

        self.old_account_params = load_from_json_file(TEST_PARAMETERS_PATH)
        self.created_account_id = EntityAccount.add_from_json(
            self.old_account_params
        )

        self.new_valid_account_params = {
            'vdvid': str(self.created_account_id),
            'name': 'new valid username',
        }
        self.valid_request_params = {"json": self.new_valid_account_params}

    def tearDown(self):
        EntityAccount.delete(self.created_account_id)

    # Tests

    def test_update_username_given_valid_params(self):
        # When
        resp = self.client.simulate_put(
            self.request_uri_path, **self.valid_request_params
        )

        # Then
        self.assertEqual(resp.status, falcon.HTTP_200)
        self.check_dict1_in_dict2(self.new_valid_account_params, resp.json)

    def test_update_username_given_invalid_params(self):
        pass
        # Can't simulate invalid JSON

    def test_update_not_existing_user(self):
        pass


if __name__ == '__main__':
    unittest.main()
