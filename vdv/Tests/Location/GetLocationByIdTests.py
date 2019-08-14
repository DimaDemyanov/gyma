import unittest
import sys

import falcon

from gyma.vdv.Tests.Location.BaseLocationTestCase import BaseLocationTestCase
from gyma.vdv.Tests.Base.test_helpers import (
    create_request_uri_path_with_param, load_from_json_file,
)

from gyma.vdv.Entities.EntityLocation import EntityLocation


TEST_PARAMETERS_PATH = '{dir_path}/location.json'.format(dir_path=sys.path[0])


class GetLocationByIdTests(BaseLocationTestCase):

    # setUp & tearDown

    @classmethod
    def setUpClass(cls):
        super(GetLocationByIdTests, cls).setUpClass()

        operation_id = 'getLocationById'
        cls.check_operation_id_has_operation_handler(operation_id)
        cls.base_request_uri_path = cls.get_request_uri_path(operation_id)

        cls.valid_location_params = load_from_json_file(TEST_PARAMETERS_PATH)

    def setUp(self):
        self.created_location_id = EntityLocation.add_from_json(
            self.valid_location_params
        )
        self.valid_location_params['vdvid'] = str(self.created_location_id)

        self.valid_request_params = {
            "params": {
                "locationId": self.created_location_id
            }
        }
        self.non_existing_location_id_request_params = {
            "params": {
                "locationId": "0"
            }
        }

    def tearDown(self):
        self._delete_created_locations()

    # Tests

    def test_get_location_given_valid_location_id_param(self):
        # Given
        request_uri_path_with_param = create_request_uri_path_with_param(
            self.base_request_uri_path,
            self.valid_request_params['params']['locationId']
        )

        # When
        resp = self.client.simulate_get(
            request_uri_path_with_param, **self.valid_request_params
        )

        # Then
        self.assertEqual(resp.status, falcon.HTTP_200)
        self.check_dict1_in_dict2(resp.json, self.valid_location_params)

    def test_get_location_given_non_existing_location_id_param(self):
        # Given
        request_uri_path_with_param = create_request_uri_path_with_param(
            self.base_request_uri_path,
            self.non_existing_location_id_request_params['params']['locationId']
        )

        # When
        resp = self.client.simulate_get(
            request_uri_path_with_param,
            **self.non_existing_location_id_request_params
        )

        # Then
        self.assertEqual(resp.status, falcon.HTTP_404)


if __name__ == '__main__':
    unittest.main()
