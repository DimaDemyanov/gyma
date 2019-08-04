import unittest

import falcon

from gyma.vdv.Tests.Sport.BaseSportTestCase import BaseSportTestCase
from gyma.vdv.Tests.Base.test_helpers import (
    create_request_uri_path_with_param, load_from_json_file,
)

from gyma.vdv.Entities.EntitySport import EntitySport

from gyma.vdv.db import DBConnection


TEST_PARAMETERS_PATH = './sport.json'


class DeleteSportTests(BaseSportTestCase):

    # MARK: - setUp & tearDown

    @classmethod
    def setUpClass(cls):
        super(DeleteSportTests, cls).setUpClass()

        operation_id = 'deleteSport'
        cls.check_operation_id_has_operation_handler(operation_id)
        cls.base_request_uri_path = cls.get_request_uri_path(operation_id)

        cls.new_sport_params = load_from_json_file(TEST_PARAMETERS_PATH)

    def setUp(self):
        self.created_sport_id = EntitySport.add_from_json(
            self.new_sport_params
        )
        self.valid_request_params = {
            "params": {
                "sportId": self.created_sport_id
            }
        }
        self.non_existing_sport_id_request_params = {
            "params": {
                "sportId": "0"
            }
        }
        self.invalid_sport_id_request_params = {
            "params": {
                "sportId": "invalid because not 'int'"
            }
        }

    def tearDown(self):
        if self._is_sport_in_db(self.valid_request_params):
            EntitySport.delete(self.created_sport_id)

    # MARK: - Tests

    def test_delete_sport_given_valid_sport_id_param(self):
        # Given
        request_uri_path_with_param = create_request_uri_path_with_param(
            self.base_request_uri_path,
            self.valid_request_params['params']['sportId']
        )

        # When
        resp = self.client.simulate_delete(
            request_uri_path_with_param, **self.valid_request_params
        )

        # Then
        self.assertEqual(resp.status, falcon.HTTP_200)
        self.assertFalse(self._is_sport_in_db(self.valid_request_params))

    def test_delete_sport_given_non_existing_sport_id_param(self):
        # Given
        request_uri_path_with_param = create_request_uri_path_with_param(
            self.base_request_uri_path,
            self.non_existing_sport_id_request_params['params']['sportId']
        )

        # When
        resp = self.client.simulate_delete(
            request_uri_path_with_param,
            **self.non_existing_sport_id_request_params
        )

        # Then
        self.assertEqual(resp.status, falcon.HTTP_404)

    def test_delete_sport_given_invalid_sport_id_param(self):
        # Given
        request_uri_path_with_param = create_request_uri_path_with_param(
            self.base_request_uri_path,
            self.invalid_sport_id_request_params['params']['sportId']
        )

        # When
        resp = self.client.simulate_delete(
            request_uri_path_with_param,
            **self.non_existing_sport_id_request_params
        )

        # Then
        self.assertEqual(resp.status, falcon.HTTP_400)


if __name__ == '__main__':
    unittest.main()
