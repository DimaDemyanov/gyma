import unittest
import sys

import falcon

from gyma.vdv.Tests.SpecialUsers.Simpleuser.BaseSimpleuserTestCase import (
    BaseSimpleuserTestCase
)
from gyma.vdv.Tests.Base.test_helpers import (
    create_request_uri_path_with_param, load_from_json_file,
    convert_dict_bool_str_values_to_bool,
    TEST_ACCOUNT
)

from gyma.vdv.Entities.EntitySimpleuser import EntitySimpleuser

from gyma.vdv.db import DBConnection
from gyma.vdv.app import stringToBool


TEST_PARAMETERS_PATH = '{dir_path}/simpleuser.json'.format(dir_path=sys.path[0])


class GetSimpleuserTests(BaseSimpleuserTestCase):

    # setUp & tearDown

    @classmethod
    def setUpClass(cls):
        super(GetSimpleuserTests, cls).setUpClass()

        operation_id = 'getSimpleUser'
        cls.check_operation_id_has_operation_handler(operation_id)
        cls.base_request_uri_path = cls.get_request_uri_path(operation_id)

        cls.simpleuser_params = load_from_json_file(TEST_PARAMETERS_PATH)
        cls.simpleuser_params['accountid'] = TEST_ACCOUNT['vdvid']

    def setUp(self):

        self.created_simpleuser_id = EntitySimpleuser.add_from_json(
            self.simpleuser_params
        )
        self.simpleuser_params['vdvid'] = str(self.created_simpleuser_id)

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
        with DBConnection() as session:
            session.db.query(EntitySimpleuser).delete()
            session.db.commit()

    # Tests

    def test_get_simpleuser_given_valid_simpleuser_id_param(self):
        # Given
        request_uri_path_with_param = create_request_uri_path_with_param(
            self.base_request_uri_path,
            self.valid_request_params['params']['simpleuserId']
        )

        # When
        resp = self.client.simulate_get(
            request_uri_path_with_param, **self.valid_request_params
        )

        # Then
        self.assertEqual(resp.status, falcon.HTTP_200)

        self.assertFalse(
            self._get_property_isAgreeRules(self.simpleuser_params)
        )
        self.check_dict1_in_dict2(resp.json, self.simpleuser_params)

    def test_get_simpleuser_given_non_existing_simpleuser_id_param(self):
        # Given
        request_uri_path_with_param = create_request_uri_path_with_param(
            self.base_request_uri_path,
            self.non_existing_simpleuser_id_request_params['params']['simpleuserId']
        )

        # When
        resp = self.client.simulate_get(
            request_uri_path_with_param,
            **self.non_existing_simpleuser_id_request_params
        )

        # Then
        self.assertEqual(resp.status, falcon.HTTP_404)


if __name__ == '__main__':
    unittest.main()
