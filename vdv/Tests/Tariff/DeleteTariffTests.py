import unittest

import falcon

from gyma.vdv.Tests.Tariff.BaseTariffTestCase import BaseTariffTestCase
from gyma.vdv.Tests.Base.test_helpers import (
    create_request_uri_path_with_param, load_from_json_file,
)

from gyma.vdv.Entities.EntityTariff import EntityTariff

from gyma.vdv.db import DBConnection


TEST_PARAMETERS_PATH = './tariff.json'


class DeleteTariffTests(BaseTariffTestCase):

    # MARK: - setUp & tearDown

    @classmethod
    def setUpClass(cls):
        super(DeleteTariffTests, cls).setUpClass()

        operation_id = 'deleteTariff'
        cls.check_operation_id_has_operation_handler(operation_id)
        cls.base_request_uri_path = cls.get_request_uri_path(operation_id)

        cls.new_tariff_params = load_from_json_file(TEST_PARAMETERS_PATH)

    def setUp(self):
        self.created_tariff_id = EntityTariff.add_from_json(
            self.new_tariff_params
        )
        self.valid_request_params = {
            "params": {
                "tariffId": self.created_tariff_id
            }
        }
        self.non_existing_tariff_id_request_params = {
            "params": {
                "tariffId": "0"
            }
        }
        self.invalid_tariff_id_request_params = {
            "params": {
                "tariffId": "invalid because not 'int'"
            }
        }

    def tearDown(self):
        if self._is_tariff_in_db(self.valid_request_params):
            EntityTariff.delete(self.created_tariff_id)

    # MARK: - Tests

    def test_delete_tariff_given_valid_tariff_id_param(self):
        # Given
        request_uri_path_with_param = create_request_uri_path_with_param(
            self.base_request_uri_path,
            self.valid_request_params['params']['tariffId']
        )

        # When
        resp = self.client.simulate_delete(
            request_uri_path_with_param, **self.valid_request_params
        )

        # Then
        self.assertEqual(resp.status, falcon.HTTP_200)
        self.assertFalse(self._is_tariff_in_db(self.valid_request_params))

    def test_delete_tariff_given_non_existing_tariff_id_param(self):
        # Given
        request_uri_path_with_param = create_request_uri_path_with_param(
            self.base_request_uri_path,
            self.non_existing_tariff_id_request_params['params']['tariffId']
        )

        # When
        resp = self.client.simulate_delete(
            request_uri_path_with_param,
            **self.non_existing_tariff_id_request_params
        )

        # Then
        self.assertEqual(resp.status, falcon.HTTP_404)

    def test_delete_tariff_given_invalid_tariff_id_param(self):
        # Given
        request_uri_path_with_param = create_request_uri_path_with_param(
            self.base_request_uri_path,
            self.invalid_tariff_id_request_params['params']['tariffId']
        )

        # When
        resp = self.client.simulate_delete(
            request_uri_path_with_param,
            **self.non_existing_tariff_id_request_params
        )

        # Then
        self.assertEqual(resp.status, falcon.HTTP_400)


if __name__ == '__main__':
    unittest.main()
