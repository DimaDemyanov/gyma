import unittest

import falcon

from gyma.vdv.Tests.Court.BaseCourtTestCase import BaseCourtTestCase
from gyma.vdv.Tests.Base.test_helpers import (
    create_request_uri_path_with_param, load_from_json_file
)

from gyma.vdv.Entities.EntityCourt import EntityCourt
from gyma.vdv.Entities.EntityLocation import EntityLocation


COURT_PARAMETERS_PATH = './court_with_location_prop.json'
LOCATION_PARAMETERS_PATH = './location.json'


class GetCourtByLocationIdTests(BaseCourtTestCase):

    # setUp & tearDown

    @classmethod
    def setUpClass(cls):
        super(GetCourtByLocationIdTests, cls).setUpClass()

        operation_id = 'getCourtByLocationId'
        cls.check_operation_id_has_operation_handler(operation_id)
        cls.base_request_uri_path = cls.get_request_uri_path(operation_id)

        cls.created_location_id = cls._create_location()
        cls.valid_court_params = cls._create_valid_court_params()
        cls.created_court_id = cls._create_court(cls.valid_court_params)

        cls.valid_request_params = {
            "params": {
                "locationId": cls.created_location_id,
            }
        }

        cls.non_existing_location_id_request_params = {
            "params": {
                "locationId": "-1",
            }
        }

    @classmethod
    def tearDownClass(cls):
        EntityCourt.delete_wide_object(cls.created_court_id)
        EntityLocation.delete(cls.created_location_id)
        EntityCourt.delete(cls.created_court_id)
        super(GetCourtByLocationIdTests, cls).tearDownClass()

    # Tests

    def test_get_court_given_valid_location_id_param(self):
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
        self._check_if_response_returned_expected_court(
            resp, self.valid_court_params,
        )

    def test_get_court_given_non_existing_location_id_param(self):
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

    # MARK: - Overrides

    @classmethod
    def _create_valid_court_params(cls, court_params_path=COURT_PARAMETERS_PATH):
        valid_court_params = load_from_json_file(court_params_path)
        valid_court_params['ownerid'] = str(cls.created_landlord_id)
        valid_court_params['prop']['location'] = cls.created_location_id
        return valid_court_params

    # MARK: - Private class methods

    @classmethod
    def _create_location(self, location_params_path=LOCATION_PARAMETERS_PATH):
        location_params = load_from_json_file(location_params_path)
        location = EntityLocation(
            location_params['name'],
            location_params['latitude'],
            location_params['longitude'],
        )
        created_location_id = location.add()
        return created_location_id

    # MARK: - Private methods

    def _check_if_response_returned_expected_court(self, resp, court_params):
        courts = resp.json

        # Should be only one court
        self.assertEqual(len(courts), 1)

        returned_court = courts[0]
        self.check_dict1_in_dict2(court_params, returned_court)


if __name__ == '__main__':
    unittest.main()
