import unittest
import sys

import falcon

from gyma.vdv.Tests.Location.BaseLocationTestCase import BaseLocationTestCase
from gyma.vdv.Tests.Base.test_helpers import (
    create_request_uri_path_with_param, load_from_json_file,
)

from gyma.vdv.Entities.EntityLocation import EntityLocation


TEST_PARAMETERS_PATH = '{dir_path}/location.json'.format(dir_path=sys.path[0])


class DeleteLocationTests(BaseLocationTestCase):

    # MARK: - setUp & tearDown

    @classmethod
    def setUpClass(cls):
        super(DeleteLocationTests, cls).setUpClass()

        operation_id = 'deleteLocation'
        cls.check_operation_id_has_operation_handler(operation_id)
        cls.base_request_uri_path = cls.get_request_uri_path(operation_id)

        cls.new_location_params = load_from_json_file(TEST_PARAMETERS_PATH)

    def setUp(self):
        self.created_location_id = EntityLocation.add_from_json(
            self.new_location_params
        )
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
        self.invalid_location_id_request_params = {
            "params": {
                "locationId": "invalid because not 'int'"
            }
        }

    def tearDown(self):
        self._delete_created_locations()

    # MARK: - Tests

    def test_delete_location_given_valid_location_id_param(self):
        # Given
        request_uri_path_with_param = create_request_uri_path_with_param(
            self.base_request_uri_path,
            self.valid_request_params['params']['locationId']
        )

        # When
        resp = self.client.simulate_delete(
            request_uri_path_with_param, **self.valid_request_params
        )

        # Then
        self.assertEqual(resp.status, falcon.HTTP_200)
        self.assertFalse(self._is_location_in_db(self.valid_request_params))

    def test_delete_location_given_non_existing_location_id_param(self):
        # Given
        request_uri_path_with_param = create_request_uri_path_with_param(
            self.base_request_uri_path,
            self.non_existing_location_id_request_params['params']['locationId']
        )

        # When
        resp = self.client.simulate_delete(
            request_uri_path_with_param,
            **self.non_existing_location_id_request_params
        )

        # Then
        self.assertEqual(resp.status, falcon.HTTP_404)

    def test_delete_location_given_invalid_location_id_param(self):
        # Given
        request_uri_path_with_param = create_request_uri_path_with_param(
            self.base_request_uri_path,
            self.invalid_location_id_request_params['params']['locationId']
        )

        # When
        resp = self.client.simulate_delete(
            request_uri_path_with_param,
            **self.non_existing_location_id_request_params
        )

        # Then
        self.assertEqual(resp.status, falcon.HTTP_400)


if __name__ == '__main__':
    unittest.main()
