import unittest
from collections import OrderedDict
import sys

import falcon

from gyma.vdv.Tests.Base.test_helpers import load_from_json_file, TEST_ACCOUNT
from gyma.vdv.Tests.Tariff.BaseTariffTestCase import (
    BaseTariffTestCase
)

from gyma.vdv.Entities.EntityTariff import EntityTariff

from gyma.vdv.db import DBConnection


TEST_PARAMETERS_PATH = '{dir_path}/tariff.json'.format(dir_path=sys.path[0])


class CreateTariffTests(BaseTariffTestCase):

    # MARK: - setUp & tearDown

    @classmethod
    def setUpClass(cls):
        super(CreateTariffTests, cls).setUpClass()

        operation_id = 'createTariff'
        cls.check_operation_id_has_operation_handler(operation_id)
        cls.request_uri_path = cls.get_request_uri_path(operation_id)

        cls.valid_tariff_params = load_from_json_file(TEST_PARAMETERS_PATH)
        cls.valid_request_params = {"json": cls.valid_tariff_params}

        cls.invalid_tariff_params = {}
        cls.invalid_request_params = {"json": cls.invalid_tariff_params}

    def tearDown(self):
        self._delete_created_tariffs()

    # MARK: - Tests

    def test_create_tariff_given_valid_params(self):
        # When
        resp = self.client.simulate_post(
            self.request_uri_path, **self.valid_request_params
        )

        # Then
        self.assertEqual(resp.status, falcon.HTTP_200)
        self.assertTrue(self._is_tariff_in_db(self.valid_tariff_params))

    def test_create_tariff_given_invalid_tariff_params(self):
        # When
        resp = self.client.simulate_post(
            self.request_uri_path, **self.invalid_request_params
        )

        # Then
        self.assertEqual(resp.status, falcon.HTTP_412)
        self.assertFalse(
            self._is_tariff_in_db(self.invalid_tariff_params)
        )


if __name__ == '__main__':
    unittest.main()
