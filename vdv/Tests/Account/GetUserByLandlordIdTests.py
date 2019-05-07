import unittest

import falcon

from gyma.vdv.Tests.Base.BaseTestCase import BaseTestCase
from gyma.vdv.Tests.Base.test_helpers import (
    TEST_ACCOUNT, create_request_uri_path_with_param, load_from_json_file
)

from gyma.vdv.Entities.EntityLandlord import EntityLandlord

from gyma.vdv.db import DBConnection


TEST_PARAMETERS_PATH = './landlord.json'


class GetUserByIdTests(BaseTestCase):

    # setUp & tearDown

    @classmethod
    def setUpClass(cls):
        super(GetUserByIdTests, cls).setUpClass()

        operation_id = 'getUserByLandlord'
        cls.check_operation_id_has_operation_handler(operation_id)
        cls.base_request_uri_path = cls.get_request_uri_path(operation_id)

        cls.new_landlord_params = load_from_json_file(TEST_PARAMETERS_PATH)
        cls.new_landlord_params['accountid'] = TEST_ACCOUNT['vdvid']

        cls.created_landlord_id = EntityLandlord.add_from_json(
            cls.new_landlord_params)

        # Due to request above 'landlord' property will be added
        # to TEST_ACCOUNT
        TEST_ACCOUNT['landlord'] = cls.new_landlord_params
        TEST_ACCOUNT['landlord']['vdvid'] = cls.created_landlord_id

        cls.new_landlord_params['vdvid'] = str(cls.created_landlord_id)

        cls.valid_request_params = {
            "params": {
                "landlordId": cls.created_landlord_id
            }
        }
        cls.non_existing_landlord_id_request_params = {
            "params": {
                "landlordId": "0"
            }
        }

    @classmethod
    def tearDownClass(cls):
        with DBConnection() as session:
            session.db.query(EntityLandlord).filter_by(
                vdvid=cls.created_landlord_id).delete()
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
        self.check_dict1_in_dict2(resp.json, TEST_ACCOUNT)

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
