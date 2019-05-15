import unittest

import falcon

from gyma.vdv.Tests.Court.BaseCourtTestCase import BaseCourtTestCase
from gyma.vdv.Tests.Base.test_helpers import (
    create_request_uri_path_with_param
)

from gyma.vdv.Entities.EntityCourt import EntityCourt


class GetCourtByLandlordIdTests(BaseCourtTestCase):

    # setUp & tearDown

    @classmethod
    def setUpClass(cls):
        super(GetCourtByLandlordIdTests, cls).setUpClass()

        operation_id = 'getCourtByLandlordId'
        cls.check_operation_id_has_operation_handler(operation_id)
        cls.base_request_uri_path = cls.get_request_uri_path(operation_id)

        cls.valid_court_params = cls._create_valid_court_params()
        cls.created_court_id = cls._create_court(cls.valid_court_params)

        cls.valid_request_params_isPublished = {
            "params": {
                "landlordId": str(cls.created_landlord_id),
                "ispublished": "published"
            }
        }
        cls.valid_request_params_isNotPublished = {
            "params": {
                "landlordId": str(cls.created_landlord_id),
                "ispublished": "notpublished"
            }
        }

        cls.non_existing_landlord_id_request_params = {
            "params": {
                "landlordId": "-1",
                "ispublished": "notpublished"
            }
        }

    @classmethod
    def tearDownClass(cls):
        EntityCourt.delete(cls.created_court_id)
        super(GetCourtByLandlordIdTests, cls).tearDownClass()

    # Tests

    def test_get_court_given_valid_landlord_id_param_isPublished(self):
        # Given
        EntityCourt.confirm(self.created_court_id)
        request_uri_path_with_param = create_request_uri_path_with_param(
            self.base_request_uri_path,
            self.valid_request_params_isPublished['params']['landlordId']
        )

        # When
        resp = self.client.simulate_get(
            request_uri_path_with_param,
            **self.valid_request_params_isPublished
        )

        # Then
        self.assertEqual(resp.status, falcon.HTTP_200)
        self._check_if_response_returned_expected_court(
            resp, self.valid_court_params
        )

    def test_get_court_given_valid_landlord_id_param_isNotPublished(self):
        # Given
        request_uri_path_with_param = create_request_uri_path_with_param(
            self.base_request_uri_path,
            self.valid_request_params_isNotPublished['params']['landlordId']
        )

        # When
        resp = self.client.simulate_get(
            request_uri_path_with_param,
            **self.valid_request_params_isNotPublished
        )

        # Then
        self.assertEqual(resp.status, falcon.HTTP_200)
        self._check_if_response_returned_expected_court(
            resp, self.valid_court_params
        )

    def test_get_court_given_non_existing_landlord_id_param(self):
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

    # MARK: - Private methods

    def _check_if_response_returned_expected_court(self, resp, court_params):
        courts = resp.json

        # Should be only one court
        self.assertEqual(len(courts), 1)

        returned_court = courts[0]
        self.check_dict1_in_dict2(court_params, returned_court)


if __name__ == '__main__':
    unittest.main()
