import unittest
from collections import OrderedDict

import falcon

from gyma.vdv.Tests.Base.test_helpers import load_from_json_file, TEST_ACCOUNT
from gyma.vdv.Tests.Equipment.BaseEquipmentTestCase import BaseEquipmentTestCase

from gyma.vdv.Entities.EntityEquipment import EntityEquipment

from gyma.vdv.db import DBConnection


TEST_PARAMETERS_PATH = './equipment.json'


class GetEquipmentsTests(BaseEquipmentTestCase):

    # MARK: - setUp & tearDown

    @classmethod
    def setUpClass(cls):
        super(GetEquipmentsTests, cls).setUpClass()

        operation_id = 'getEquipments'
        cls.check_operation_id_has_operation_handler(operation_id)
        cls.request_uri_path = cls.get_request_uri_path(operation_id)

        cls.valid_equipment_params = load_from_json_file(TEST_PARAMETERS_PATH)
        cls.created_equipment_id = EntityEquipment.add_from_json(
            cls.valid_equipment_params
        )
        cls.valid_equipment_params['vdvid'] = str(cls.created_equipment_id)

    def tearDown(self):
        self._delete_created_equipments()

    # MARK: - Tests

    def test_get_equipments_returns_only_created_equipment(self):
        # When
        resp = self.client.simulate_get(self.request_uri_path)

        expected_result = [self.valid_equipment_params]

        # Then
        self.assertEqual(resp.status, falcon.HTTP_200)
        self.assertEqual(resp.json, expected_result)
        self.assertTrue(self._is_equipment_in_db(self.valid_equipment_params))


if __name__ == '__main__':
    unittest.main()
