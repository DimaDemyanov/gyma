import unittest
from collections import OrderedDict
import sys

import falcon

from gyma.vdv.Tests.Base.test_helpers import load_from_json_file, TEST_ACCOUNT
from gyma.vdv.Tests.Equipment.BaseEquipmentTestCase import (
    BaseEquipmentTestCase
)

from gyma.vdv.Entities.EntityEquipment import EntityEquipment

from gyma.vdv.db import DBConnection


TEST_PARAMETERS_PATH = '{dir_path}/equipment.json'.format(dir_path=sys.path[0])



class CreateEquipmentTests(BaseEquipmentTestCase):

    # MARK: - setUp & tearDown

    @classmethod
    def setUpClass(cls):
        super(CreateEquipmentTests, cls).setUpClass()

        operation_id = 'createEquipment'
        cls.check_operation_id_has_operation_handler(operation_id)
        cls.request_uri_path = cls.get_request_uri_path(operation_id)

        cls.valid_equipment_params = load_from_json_file(TEST_PARAMETERS_PATH)
        cls.valid_request_params = {"json": cls.valid_equipment_params}

        cls.invalid_equipment_params = {}
        cls.invalid_request_params = {"json":  {}}

    def tearDown(self):
        self._delete_created_equipments()

    # MARK: - Tests

    def test_create_equipment_given_valid_params(self):
        # When
        resp = self.client.simulate_post(
            self.request_uri_path, **self.valid_request_params
        )

        # Then
        self.assertEqual(resp.status, falcon.HTTP_200)
        self.assertTrue(self._is_equipment_in_db(self.valid_equipment_params))

    def test_create_equipment_given_invalid_equipment_params(self):
        # When
        resp = self.client.simulate_post(
            self.request_uri_path, **self.invalid_request_params
        )

        # Then
        self.assertEqual(resp.status, falcon.HTTP_501)
        self.assertFalse(
            self._is_equipment_in_db(self.invalid_equipment_params)
        )

    def test_create_equipment_when_same_equipment_already_exists(self):
        # When
        for i in range(2):
            resp = self.client.simulate_post(
                self.request_uri_path, **self.valid_request_params
            )

        # Then
        self.assertEqual(resp.status, falcon.HTTP_412)
        self.assertFalse(
            self._is_equipment_objects_increased_by_value(
                2, self.valid_equipment_params)
        )

    # MARK: - Private methods:

    def _is_equipment_objects_increased_by_value(self, value, equipment_params):
        equipment_objects_count = EntityEquipment.get().filter_by(
            name=equipment_params.get("name")
        ).count()
        return equipment_objects_count == value


if __name__ == '__main__':
    unittest.main()
