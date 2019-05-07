import unittest

import falcon

from gyma.vdv.Tests.Equipment.BaseEquipmentTestCase import BaseEquipmentTestCase
from gyma.vdv.Tests.Base.test_helpers import (
    create_request_uri_path_with_param, load_from_json_file,
)

from gyma.vdv.Entities.EntityEquipment import EntityEquipment


TEST_PARAMETERS_PATH = './equipment.json'


class DeleteEquipmentTests(BaseEquipmentTestCase):

    # MARK: - setUp & tearDown

    @classmethod
    def setUpClass(cls):
        super(DeleteEquipmentTests, cls).setUpClass()

        operation_id = 'deleteEquipment'
        cls.check_operation_id_has_operation_handler(operation_id)
        cls.base_request_uri_path = cls.get_request_uri_path(operation_id)

        cls.new_equipment_params = load_from_json_file(TEST_PARAMETERS_PATH)

    def setUp(self):
        self.created_equipment_id = EntityEquipment.add_from_json(
            self.new_equipment_params
        )
        self.valid_request_params = {
            "params": {
                "equipmentId": self.created_equipment_id
            }
        }
        self.non_existing_equipment_id_request_params = {
            "params": {
                "equipmentId": "0"
            }
        }
        self.invalid_equipment_id_request_params = {
            "params": {
                "equipmentId": "invalid because not 'int'"
            }
        }

    def tearDown(self):
        self._delete_created_equipments()

    # MARK: - Tests

    def test_delete_equipment_given_valid_equipment_id_param(self):
        # Given
        request_uri_path_with_param = create_request_uri_path_with_param(
            self.base_request_uri_path,
            self.valid_request_params['params']['equipmentId']
        )

        # When
        resp = self.client.simulate_delete(
            request_uri_path_with_param, **self.valid_request_params
        )

        # Then
        self.assertEqual(resp.status, falcon.HTTP_200)
        self.assertFalse(self._is_equipment_in_db(self.valid_request_params))

    def test_delete_equipment_given_non_existing_equipment_id_param(self):
        # Given
        request_uri_path_with_param = create_request_uri_path_with_param(
            self.base_request_uri_path,
            self.non_existing_equipment_id_request_params['params']['equipmentId']
        )

        # When
        resp = self.client.simulate_delete(
            request_uri_path_with_param,
            **self.non_existing_equipment_id_request_params
        )

        # Then
        self.assertEqual(resp.status, falcon.HTTP_404)

    def test_delete_equipment_given_invalid_equipment_id_param(self):
        # Given
        request_uri_path_with_param = create_request_uri_path_with_param(
            self.base_request_uri_path,
            self.invalid_equipment_id_request_params['params']['equipmentId']
        )

        # When
        resp = self.client.simulate_delete(
            request_uri_path_with_param,
            **self.non_existing_equipment_id_request_params
        )

        # Then
        self.assertEqual(resp.status, falcon.HTTP_400)


if __name__ == '__main__':
    unittest.main()
