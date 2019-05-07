import unittest

import falcon

from gyma.vdv.Tests.Sport.BaseSportTestCase import BaseSportTestCase
from gyma.vdv.Tests.Base.test_helpers import (
    create_request_uri_path_with_param, load_from_json_file,
)

from gyma.vdv.Entities.EntitySport import EntitySport


TEST_PARAMETERS_PATH = './sport.json'


class GetSportByIdTests(BaseSportTestCase):

    # setUp & tearDown

    @classmethod
    def setUpClass(cls):
        super(GetSportByIdTests, cls).setUpClass()

        operation_id = 'getSportById'
        cls.check_operation_id_has_operation_handler(operation_id)
        cls.base_request_uri_path = cls.get_request_uri_path(operation_id)

        cls.valid_sport_params = load_from_json_file(TEST_PARAMETERS_PATH)

    def setUp(self):
        self.created_sport_id = EntitySport.add_from_json(
            self.valid_sport_params
        )
        self.valid_sport_params['vdvid'] = str(self.created_sport_id)

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

    def tearDown(self):
        self._delete_created_sports()

    # Tests

    def test_get_sport_given_valid_sport_id_param(self):
        # Given
        request_uri_path_with_param = create_request_uri_path_with_param(
            self.base_request_uri_path,
            self.valid_request_params['params']['sportId']
        )

        # When
        resp = self.client.simulate_get(
            request_uri_path_with_param, **self.valid_request_params
        )

        # Then
        self.assertEqual(resp.status, falcon.HTTP_200)
        self.check_dict1_in_dict2(resp.json, self.valid_sport_params)

    def test_get_sport_given_non_existing_sport_id_param(self):
        # Given
        request_uri_path_with_param = create_request_uri_path_with_param(
            self.base_request_uri_path,
            self.non_existing_sport_id_request_params['params']['sportId']
        )

        # When
        resp = self.client.simulate_get(
            request_uri_path_with_param,
            **self.non_existing_sport_id_request_params
        )

        # Then
        self.assertEqual(resp.status, falcon.HTTP_404)


if __name__ == '__main__':
    unittest.main()
