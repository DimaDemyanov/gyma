import unittest

import falcon

from gyma.vdv.Tests.Court.BaseCourtTestCase import BaseCourtTestCase
from gyma.vdv.Tests.Base.test_helpers import (
    create_request_uri_path_with_param
)

from gyma.vdv.Entities.EntityCourt import EntityCourt


class DeleteCourtTests(BaseCourtTestCase):

    # MARK: - setUp & tearDown

    @classmethod
    def setUpClass(cls):
        super(DeleteCourtTests, cls).setUpClass()

        operation_id = 'deleteCourt'
        cls.check_operation_id_has_operation_handler(operation_id)
        cls.base_request_uri_path = cls.get_request_uri_path(operation_id)

        cls.new_court_params = cls._create_valid_court_params()

    def setUp(self):
        self.created_court_id = EntityCourt.add_from_json(
            self.new_court_params
        )
        self.valid_request_params = {
            "params": {
                "courtId": str(self.created_court_id)
            }
        }
        self.non_existing_court_id_request_params = {
            "params": {
                "courtId": "0"
            }
        }
        self.invalid_court_id_request_params = {
            "params": {
                "courtId": "invalid because not 'int'"
            }
        }

    def tearDown(self):
        self._delete_created_court_if_needed(self.created_court_id)

    # MARK: - Tests

    def test_delete_court_given_valid_court_id_param(self):
        # Given
        request_uri_path_with_param = create_request_uri_path_with_param(
            self.base_request_uri_path,
            self.valid_request_params['params']['courtId']
        )

        # When
        resp = self.client.simulate_delete(
            request_uri_path_with_param, **self.valid_request_params
        )

        # Then
        self.assertEqual(resp.status, falcon.HTTP_200)
        self.assertFalse(self._is_court_in_db(self.valid_request_params))

    def test_delete_court_given_non_existing_court_id_param(self):
        # Given
        request_uri_path_with_param = create_request_uri_path_with_param(
            self.base_request_uri_path,
            self.non_existing_court_id_request_params['params']['courtId']
        )

        # When
        resp = self.client.simulate_delete(
            request_uri_path_with_param,
            **self.non_existing_court_id_request_params
        )

        # Then
        self.assertEqual(resp.status, falcon.HTTP_404)

    def test_delete_court_given_invalid_court_id_param(self):
        # Given
        request_uri_path_with_param = create_request_uri_path_with_param(
            self.base_request_uri_path,
            self.invalid_court_id_request_params['params']['courtId']
        )

        # When
        resp = self.client.simulate_delete(
            request_uri_path_with_param,
            **self.invalid_court_id_request_params
        )

        # Then
        self.assertEqual(resp.status, falcon.HTTP_400)

    # TODO:
    # def test_delete_court_when_court_param_violates_foreign_key(self):

    # MARK: - Private methods

    def _delete_created_court_if_needed(self, created_court_id):
        try:
            EntityCourt.delete(self.created_court_id)
        except FileNotFoundError:
            pass


if __name__ == '__main__':
    unittest.main()
