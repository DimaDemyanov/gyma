import unittest

import falcon

from gyma.vdv.Tests.SpecialUsers.Landlord.BaseLandlordTestCase import (
    BaseLandlordTestCase
)
from gyma.vdv.Tests.Base.test_helpers import (
    create_request_uri_path_with_param, load_from_json_file,
    convert_dict_bool_str_values_to_bool,
    TEST_ACCOUNT
)

from gyma.vdv.Entities.EntityLandlord import EntityLandlord

from gyma.vdv.db import DBConnection
from gyma.vdv.app import stringToBool


TEST_PARAMETERS_PATH = './landlord.json'


class GetLandlordTests(BaseLandlordTestCase):

    # setUp & tearDown

    @classmethod
    def setUpClass(cls):
        super(GetLandlordTests, cls).setUpClass()

        operation_id = 'getLandlord'
        cls.check_operation_id_has_operation_handler(operation_id)
        cls.base_request_uri_path = cls.get_request_uri_path(operation_id)

        cls.valid_landlord_params = load_from_json_file(TEST_PARAMETERS_PATH)
        cls.valid_landlord_params['accountid'] = TEST_ACCOUNT['vdvid']

    def setUp(self):
        self.created_landlord_id = EntityLandlord.add_from_json(
            self.valid_landlord_params
        )
        self.valid_landlord_params['vdvid'] = str(self.created_landlord_id)

        self.valid_request_params = {
            "params": {
                "landlordId": self.created_landlord_id
            }
        }
        self.non_existing_landlord_id_request_params = {
            "params": {
                "landlordId": "0"
            }
        }

    def tearDown(self):
        with DBConnection() as session:
            session.db.query(EntityLandlord).delete()
            session.db.commit()

    # Tests

    def test_get_landlord_given_valid_landlord_id_param(self):
        # Given
        request_uri_path_with_param = create_request_uri_path_with_param(
            self.base_request_uri_path,
            self.valid_request_params['params']['landlordId']
        )

        # When
        resp = self.client.simulate_get(
            request_uri_path_with_param, **self.valid_request_params
        )

        # Then
        self.assertEqual(resp.status, falcon.HTTP_200)

        self.assertFalse(
            self._get_property_isAgreeRules(self.valid_landlord_params)
        )

        with self.assertRaises(AssertionError):
            self.check_dict1_in_dict2(resp.json, self.valid_landlord_params)

    def test_get_landlord_given_non_existing_landlord_id_param(self):
        # Given
        request_uri_path_with_param = create_request_uri_path_with_param(
            self.base_request_uri_path,
            self.non_existing_landlord_id_request_params['params']['landlordId']
        )

        # When
        resp = self.client.simulate_get(
            request_uri_path_with_param,
            **self.non_existing_landlord_id_request_params
        )

        # Then
        self.assertEqual(resp.status, falcon.HTTP_404)


if __name__ == '__main__':
    unittest.main()
