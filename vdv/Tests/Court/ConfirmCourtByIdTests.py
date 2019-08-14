import unittest

import falcon

from gyma.vdv.Tests.Court.BaseCourtTestCase import BaseCourtTestCase
from gyma.vdv.Tests.Base.test_helpers import (
    create_request_uri_path_with_param
)

from gyma.vdv.Entities.EntityCourt import EntityCourt

from gyma.vdv.db import DBConnection


class ConfirmCourtByIdTests(BaseCourtTestCase):

    # MARK: - setUp & tearDown

    @classmethod
    def setUpClass(cls):
        super(ConfirmCourtByIdTests, cls).setUpClass()

        operation_id = 'confirmCourtById'
        cls.check_operation_id_has_operation_handler(operation_id)
        cls.base_request_uri_path = cls.get_request_uri_path(operation_id)

        cls.valid_court_params = cls._create_valid_court_params()
        cls.created_court_id = cls._create_court(cls.valid_court_params)

        cls.valid_request_params = {
            "params": {
                "courtId": str(cls.created_court_id)
            }
        }
        cls.non_existing_court_id_request_params = {
            "params": {
                "courtId": "-1"
            }
        }

    @classmethod
    def tearDownClass(cls):
        EntityCourt.delete(cls.created_court_id)
        super(ConfirmCourtByIdTests, cls).tearDownClass()

    # MARK: - Tests

    def test_confirm_court_given_valid_court_id_param(self):
        # Given
        request_uri_path_with_param = create_request_uri_path_with_param(
            self.base_request_uri_path,
            self.valid_request_params['params']['courtId']
        )

        # When
        resp = self.client.simulate_post(
            request_uri_path_with_param, **self.valid_request_params
        )

        # Then
        self.assertEqual(resp.status, falcon.HTTP_200)
        self.assertTrue(
            self._get_property_isPublished(self.valid_court_params)
        )

    def test_confirm_court_given_non_existing_court_id_param(self):
        # Given
        request_uri_path_with_param = create_request_uri_path_with_param(
            self.base_request_uri_path,
            self.non_existing_court_id_request_params['params']['courtId']
        )

        # When
        resp = self.client.simulate_post(
            request_uri_path_with_param,
            **self.non_existing_court_id_request_params
        )

        # Then
        self.assertEqual(resp.status, falcon.HTTP_404)


if __name__ == '__main__':
    unittest.main()
