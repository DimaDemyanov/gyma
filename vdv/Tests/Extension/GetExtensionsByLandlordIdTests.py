import unittest

import falcon

from gyma.vdv.Tests.Extension.BaseExtensionTestCase import (
    BaseExtensionTestCase, EXTENSION_PARAMETERS_PATH
)

from gyma.vdv.Tests.Base.test_helpers import (
    create_request_uri_path_with_param, load_from_json_file
)

from gyma.vdv.Entities.EntityExtension import EntityExtension

from gyma.vdv.db import DBConnection


TEST_PARAMETERS_PATH = './extension.json'


class GetExtensionsByLandlordId(BaseExtensionTestCase):

    # setUp & tearDown

    @classmethod
    def setUpClass(cls):
        super(GetExtensionsByLandlordId, cls).setUpClass()

        operation_id = 'getExtensionsByLandlordId'
        cls.check_operation_id_has_operation_handler(operation_id)
        cls.base_request_uri_path = cls.get_request_uri_path(operation_id)

        cls.valid_extension_params = cls._create_valid_extension_params()
        cls.created_extension_id = EntityExtension.add_from_json(
            cls.valid_extension_params
        )

    def setUp(self):
        self.valid_request_params_isConfirmed = {
            "params": {
                "landlordId": str(self.created_landlord_id),
                "isconfirmed": "confirmed"
            }
        }
        self.valid_request_params_isNotConfirmed = {
            "params": {
                "landlordId": str(self.created_landlord_id),
                "isconfirmed": "notconfirmed"
            }
        }
        self.non_existing_landlord_id_request_params = {
            "params": {
                "landlordId": "0",
                "isconfirmed": "notconfirmed"
            }
        }
        self.invalid_landlord_id_request_params = {
            "params": {
                "landlordId": None,
                "isconfirmed": "notconfirmed"
            }
        }

    @classmethod
    def tearDownClass(cls):
        super(GetExtensionsByLandlordId, cls).tearDownClass()
        cls._delete_created_extension(cls.created_extension_id)

    # Tests

    def test_get_extensions_given_valid_landlord_id_param(self):
        # Given
        request_uri_path_with_param = create_request_uri_path_with_param(
            self.base_request_uri_path,
            self.valid_request_params_isNotConfirmed['params']['landlordId']
        )

        # When
        resp = self.client.simulate_get(
            request_uri_path_with_param,
            **self.valid_request_params_isNotConfirmed
        )

        # Then
        self.assertEqual(resp.status, falcon.HTTP_200)

        # request should return list of extensions whith 1 extension
        resp_list = resp.json
        self.assertEqual(len(resp_list), 1)
        self.check_dict1_in_dict2(self.valid_extension_params, resp_list[0])

    def test_get_extensions_given_non_existing_landlord_id_param(self):
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

    def test_get_extensions_given_invalid_landlord_id_param(self):
        # Given
        request_uri_path_with_param = create_request_uri_path_with_param(
            self.base_request_uri_path,
            self.invalid_landlord_id_request_params
        )

        # When
        resp = self.client.simulate_get(
            request_uri_path_with_param,
            **self.invalid_landlord_id_request_params
        )

        # Then
        self.assertEqual(resp.status, falcon.HTTP_400)


if __name__ == '__main__':
    unittest.main()
