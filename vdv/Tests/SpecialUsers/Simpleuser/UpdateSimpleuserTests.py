import unittest
from json.decoder import JSONDecodeError

import falcon

from gyma.vdv.Tests.Base.BaseTestCase import BaseTestCase
from gyma.vdv.Tests.Base.test_helpers import load_from_json_file, TEST_ACCOUNT

from gyma.vdv.Entities.EntitySimpleuser import EntitySimpleuser

from gyma.vdv.db import DBConnection


TEST_PARAMETERS_PATH = './simpleuser.json'


class UpdateSimpleuserTests(BaseTestCase):

    # setUp & tearDown

    def setUp(self):
        operation_id = 'updateSimpleUser'
        self.check_operation_id_has_operation_handler(operation_id)
        self.request_uri_path = self.get_request_uri_path(operation_id)

        self.old_simpleuser_params = load_from_json_file(TEST_PARAMETERS_PATH)
        self.old_simpleuser_params['accountid'] = TEST_ACCOUNT['vdvid']
        self.created_simpleuser_id = EntitySimpleuser.add_from_json(
            self.old_simpleuser_params
        )

        self.new_valid_simpleuser_params = {
            "vdvid": str(self.created_simpleuser_id),
            "isagreerules": "True",
        }
        self.valid_request_params = {"json": self.new_valid_simpleuser_params}

        self.non_existing_simpleuser_params = {
            'vdvid': -1,
            'company': 'True',
        }
        self.non_existing_simpleuser_request_params = {
            "json": self.non_existing_simpleuser_params
        }

    def tearDown(self):
        EntitySimpleuser.delete(self.created_simpleuser_id)

    # Tests

    def test_update_isagreerules_given_valid_params(self):
        # When
        resp = self.client.simulate_put(
            self.request_uri_path, **self.valid_request_params
        )

        # Then
        self.assertEqual(resp.status, falcon.HTTP_200)
        self.check_dict1_in_dict2(self.new_valid_simpleuser_params, resp.json)

    def test_update_not_existing_simpleuser(self):
        # When
        resp = self.client.simulate_put(
            self.request_uri_path, **self.non_existing_simpleuser_request_params
        )

        # Then
        self.assertEqual(resp.status, falcon.HTTP_404)
        self.assertFalse(self._is_resp_returned_json(resp))

    # MARK: - Private methods

    def _is_resp_returned_json(self, resp):
        with self.assertRaises(JSONDecodeError):
            resp.json


if __name__ == '__main__':
    unittest.main()
