import unittest

import falcon

from gyma.vdv.Tests.Base.BaseTestCase import BaseTestCase
from gyma.vdv.Tests.Base.test_helpers import load_from_json_file, TEST_ACCOUNT

from gyma.vdv.Entities.EntityAccount import EntityAccount

from gyma.vdv.db import DBConnection


TEST_PARAMETERS_PATH = './account.json'


class CreateAccountTests(BaseTestCase):

    # MARK: - setUp & tearDown

    def setUp(self):
        operation_id = 'deleteUser'
        self.check_operation_id_has_operation_handler(operation_id)
        self.base_request_uri_path = self.get_request_uri_path(operation_id)

        self.new_account_params = load_from_json_file(TEST_PARAMETERS_PATH)
        self.created_account_id = EntityAccount.add_from_json(
            self.new_account_params
        )

        self.valid_request_params = {
            "params": {
                "userId": self.created_account_id
            }
        }
        self.non_existing_user_id_request_params = {
            "params": {
                "userId": "0"
            }
        }

        # TODO:
        # Add Props: private, post, avatar to account &
        # assert their deletion with account

    def tearDown(self):
        if self._is_account_in_db(self.created_account_id):
            EntityAccount.delete(self.created_account_id)

    # MARK: - Tests

    def test_delete_account_given_valid_user_id_param(self):
        # Given
        request_uri_path_with_param = self.create_request_uri_path_with_param(
            self.base_request_uri_path,
            self.valid_request_params['params']['userId']
        )

        # When
        resp = self.client.simulate_delete(
            request_uri_path_with_param, **self.valid_request_params
        )

        # Then
        self.assertEqual(resp.status, falcon.HTTP_200)
        self.assertFalse(self._is_account_in_db(self.created_account_id))

    def test_delete_account_given_non_existing_user_id_param(self):
        # Given
        request_uri_path_with_param = self.create_request_uri_path_with_param(
            self.base_request_uri_path,
            self.non_existing_user_id_request_params['params']['userId']
        )

        # When
        resp = self.client.simulate_delete(
            request_uri_path_with_param,
            **self.non_existing_user_id_request_params
        )

        # Then
        self.assertEqual(resp.status, falcon.HTTP_404)

    # MARK: - Private methods:

    def _is_account_in_db(self, created_account_id):
        created_account = EntityAccount.get().filter_by(
            vdvid=created_account_id
        ).all()
        return len(created_account) == 1


if __name__ == '__main__':
    unittest.main()
