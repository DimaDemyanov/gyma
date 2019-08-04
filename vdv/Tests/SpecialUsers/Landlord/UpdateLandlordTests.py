import unittest
import sys
from json.decoder import JSONDecodeError

import falcon

from gyma.vdv.Tests.Base.BaseTestCase import BaseTestCase
from gyma.vdv.Tests.Base.test_helpers import load_from_json_file, TEST_ACCOUNT

from gyma.vdv.Entities.EntityLandlord import EntityLandlord

from gyma.vdv.db import DBConnection


TEST_PARAMETERS_PATH = '{dir_path}/landlord.json'.format(dir_path=sys.path[0])


class UpdateLandlordTests(BaseTestCase):

    # setUp & tearDown

    @classmethod
    def setUpClass(cls):
        super(UpdateLandlordTests, cls).setUpClass()

        operation_id = 'updateLandlord'
        cls.check_operation_id_has_operation_handler(operation_id)
        cls.request_uri_path = cls.get_request_uri_path(operation_id)

        cls.old_account_params = load_from_json_file(TEST_PARAMETERS_PATH)
        cls.old_account_params['accountid'] = TEST_ACCOUNT['vdvid']

    def setUp(self):
        self.created_account_id = EntityLandlord.add_from_json(
            self.old_account_params
        )

        self.new_valid_account_params = {
            'vdvid': str(self.created_account_id),
            'company': 'new valid company name',
        }
        self.valid_request_params = {"json": self.new_valid_account_params}

        self.non_existing_account_params = {
            'vdvid': -1,
            'company': 'new company name',
        }
        self.non_existing_account_request_params = {
            "json": self.non_existing_account_params
        }

    def tearDown(self):
        EntityLandlord.delete(self.created_account_id)

    # Tests

    def test_update_company_given_valid_params(self):
        # When
        resp = self.client.simulate_put(
            self.request_uri_path, **self.valid_request_params
        )

        # Then
        self.assertEqual(resp.status, falcon.HTTP_200)
        self.check_dict1_in_dict2(self.new_valid_account_params, resp.json)

    def test_update_not_existing_landlord(self):
        # When
        resp = self.client.simulate_put(
            self.request_uri_path, **self.non_existing_account_request_params
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
