import unittest

import falcon

from gyma.vdv.Tests.Base.BaseTestCase import BaseTestCase
from gyma.vdv.Tests.Base.test_helpers import (
    load_from_json_file, create_request_uri_path_with_param, TEST_ACCOUNT
)

from gyma.vdv.Entities.EntitySimpleuser import EntitySimpleuser

from gyma.vdv.db import DBConnection


TEST_PARAMETERS_PATH = './simpleuser.json'


class DeleteSimpleuserTests(BaseTestCase):

    # MARK: - setUp & tearDown

    @classmethod
    def setUpClass(cls):
        super(DeleteSimpleuserTests, cls).setUpClass()

        operation_id = 'deleteSimpleUser'
        cls.check_operation_id_has_operation_handler(operation_id)
        cls.base_request_uri_path = cls.get_request_uri_path(operation_id)

        cls.new_simpleuser_params = load_from_json_file(TEST_PARAMETERS_PATH)
        cls.new_simpleuser_params['accountid'] = TEST_ACCOUNT['vdvid']

    def setUp(self):
        self.created_simpleuser_id = EntitySimpleuser.add_from_json(
            self.new_simpleuser_params
        )
        self.valid_request_params = {
            "params": {
                "simpleuserId": self.created_simpleuser_id
            }
        }
        self.non_existing_simpleuser_id_request_params = {
            "params": {
                "simpleuserId": "0"
            }
        }

    def tearDown(self):
        if self._is_simpleuser_in_db(self.created_simpleuser_id):
            EntitySimpleuser.delete(self.created_simpleuser_id)

    # MARK: - Tests

    def test_delete_simpleuser_given_valid_simpleuser_id_param(self):
        # Given
        request_uri_path_with_param = create_request_uri_path_with_param(
            self.base_request_uri_path,
            self.valid_request_params['params']['simpleuserId']
        )

        # When
        resp = self.client.simulate_delete(
            request_uri_path_with_param, **self.valid_request_params
        )

        # Then
        self.assertEqual(resp.status, falcon.HTTP_200)
        self.assertFalse(self._is_simpleuser_in_db(self.created_simpleuser_id))

    def test_delete_simpleuser_given_non_existing_simpleuser_id_param(self):
        # Given
        request_uri_path_with_param = create_request_uri_path_with_param(
            self.base_request_uri_path,
            self.non_existing_simpleuser_id_request_params['params']['simpleuserId']
        )

        # When
        resp = self.client.simulate_delete(
            request_uri_path_with_param,
            **self.non_existing_simpleuser_id_request_params
        )

        # Then
        self.assertEqual(resp.status, falcon.HTTP_404)

    # MARK: - Private methods:

    def _is_simpleuser_in_db(self, created_simpleuser_id):
        created_simpleuser = EntitySimpleuser.get().filter_by(
            vdvid=created_simpleuser_id
        ).all()
        return len(created_simpleuser) == 1


if __name__ == '__main__':
    unittest.main()
