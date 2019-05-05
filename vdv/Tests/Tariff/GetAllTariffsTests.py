import unittest
from collections import OrderedDict

import falcon

from gyma.vdv.Tests.Base.test_helpers import load_from_json_file, TEST_ACCOUNT
from gyma.vdv.Tests.Tariff.BaseTariffTestCase import BaseTariffTestCase

from gyma.vdv.Entities.EntityTariff import EntityTariff

from gyma.vdv.db import DBConnection


TEST_PARAMETERS_PATH = './tariff.json'


class GetTariffsTests(BaseTariffTestCase):

    # MARK: - setUp & tearDown

    @classmethod
    def setUpClass(cls):
        super(GetTariffsTests, cls).setUpClass()

        operation_id = 'getAllTariffs'
        cls.check_operation_id_has_operation_handler(operation_id)
        cls.request_uri_path = cls.get_request_uri_path(operation_id)

        cls.valid_tariff_params = load_from_json_file(TEST_PARAMETERS_PATH)
        cls.created_tariff_id = EntityTariff.add_from_json(
            cls.valid_tariff_params
        )
        cls.valid_tariff_params['vdvid'] = str(cls.created_tariff_id)

    def tearDown(self):
        with DBConnection() as session:
            session.db.query(EntityTariff).delete()
            session.db.commit()

    # MARK: - Tests

    def test_get_tariffs_returns_only_created_tariff(self):
        # When
        resp = self.client.simulate_get(self.request_uri_path)

        expected_result = [self.valid_tariff_params]

        # Then
        self.assertEqual(resp.status, falcon.HTTP_200)
        self.assertEqual(resp.json, expected_result)
        self.assertTrue(self._is_tariff_in_db(self.valid_tariff_params))


if __name__ == '__main__':
    unittest.main()
