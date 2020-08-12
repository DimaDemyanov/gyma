import unittest

import falcon

from gyma.vdv.Tests.Base.BaseTestCase import BaseTestCase
from gyma.vdv.Tests.Base.test_helpers import (
    create_request_uri_path_with_param, load_from_json_file,
    convert_json_response_str_values_to_bool
)

from gyma.vdv.Entities.EntityLandlord import EntityLandlord

from gyma.vdv.db import DBConnection
from gyma.vdv.app import stringToBool


TEST_PARAMETERS_PATH = './landlord.json'


class GetMylandlordTests(BaseTestCase):

    # setUp & tearDown

    def setUp(self):
        operation_id = 'getLandlord'
        self.check_operation_id_has_operation_handler(operation_id)
        self.base_request_uri_path = self.get_request_uri_path(operation_id)

        self.landlord_params = load_from_json_file(TEST_PARAMETERS_PATH)
        self.created_landlord_id = EntityLandlord.add_from_json(
            self.landlord_params
        )
        self.landlord_params['vdvid'] = str(self.created_landlord_id)

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

        # Error!!!!!: CreateLandlord always set isAgreeRules = false
        resp_as_dict = convert_json_response_str_values_to_bool(resp.json)
        self.check_dict1_in_dict2(resp_as_dict, self.landlord_params)

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
