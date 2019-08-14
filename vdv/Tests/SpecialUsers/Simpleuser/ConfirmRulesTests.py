import unittest
import sys

import falcon

from gyma.vdv.Tests.SpecialUsers.Simpleuser.BaseSimpleuserTestCase import (
    BaseSimpleuserTestCase
)
from gyma.vdv.Tests.Base.test_helpers import load_from_json_file, TEST_ACCOUNT

from gyma.vdv.Entities.EntitySimpleuser import EntitySimpleuser


TEST_PARAMETERS_PATH = '{dir_path}/simpleuser.json'.format(dir_path=sys.path[0])


class ConfirmRulesTests(BaseSimpleuserTestCase):

    # MARK: - setUp & tearDown

    @classmethod
    def setUpClass(cls):
        super(ConfirmRulesTests, cls).setUpClass()

        operation_id = 'confirmRules'
        cls.check_operation_id_has_operation_handler(operation_id)
        cls.request_uri_path = cls.get_request_uri_path(operation_id)

        cls.valid_simpleuser_params = load_from_json_file(
            TEST_PARAMETERS_PATH)
        cls.valid_simpleuser_params['accountid'] = TEST_ACCOUNT['vdvid']

        cls.valid_request_params = {
            "params": {
                "specialuser": "simpleuser",
            }
        }

        cls.invalid_request_params = {
            "params": {
                "specialuser": "invalid due to non-existing option",
            }
        }

    def setUp(self):
        self.created_simpleuser_id = EntitySimpleuser.add_from_json(
            self.valid_simpleuser_params)

    def tearDown(self):
        EntitySimpleuser.delete(self.created_simpleuser_id)

    # MARK: - Tests

    def test_confirm_rules_given_valid_params(self):
        # When
        resp = self.client.simulate_post(
            self.request_uri_path, **self.valid_request_params
        )

        # Then
        self.assertEqual(resp.status, falcon.HTTP_200)
        self.assertTrue(
            self._get_property_isAgreeRules(self.valid_simpleuser_params)
        )

    def test_create_simpleuser_given_invalid_simpleuser_params(self):
        # When
        resp = self.client.simulate_post(
            self.request_uri_path, **self.invalid_request_params
        )

        # Then
        self.assertEqual(resp.status, falcon.HTTP_200)
        self.assertFalse(
            self._get_property_isAgreeRules(self.valid_simpleuser_params)
        )


if __name__ == '__main__':
    unittest.main()
