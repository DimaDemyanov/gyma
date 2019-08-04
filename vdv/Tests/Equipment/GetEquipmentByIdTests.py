import unittest
import sys

import falcon

from gyma.vdv.Tests.Equipment.BaseEquipmentTestCase import (
    BaseEquipmentTestCase
)
from gyma.vdv.Tests.Base.test_helpers import (
    create_request_uri_path_with_param, load_from_json_file,
)

from gyma.vdv.Entities.EntityEquipment import EntityEquipment

from gyma.vdv.db import DBConnection


TEST_PARAMETERS_PATH = '{dir_path}/equipment.json'.format(dir_path=sys.path[0])


class GetEquipmentByIdTests(BaseEquipmentTestCase):

    # setUp & tearDown

    @classmethod
    def setUpClass(cls):
        super(GetEquipmentByIdTests, cls).setUpClass()

        operation_id = 'getEquipmentById'
        cls.check_operation_id_has_operation_handler(operation_id)
        cls.base_request_uri_path = cls.get_request_uri_path(operation_id)

        cls.valid_equipment_params = load_from_json_file(TEST_PARAMETERS_PATH)

    def setUp(self):
        self.created_equipment_id = EntityEquipment.add_from_json(
            self.valid_equipment_params
        )
        self.valid_equipment_params['vdvid'] = str(self.created_equipment_id)

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

    def tearDown(self):
        with DBConnection() as session:
            session.db.query(EntityEquipment).delete()
            session.db.commit()

    # Tests

    def test_get_equipment_given_valid_equipment_id_param(self):
        # Given
        request_uri_path_with_param = create_request_uri_path_with_param(
            self.base_request_uri_path,
            self.valid_request_params['params']['equipmentId']
        )

        # When
        resp = self.client.simulate_get(
            request_uri_path_with_param, **self.valid_request_params
        )

        # Then
        self.assertEqual(resp.status, falcon.HTTP_200)
        self.check_dict1_in_dict2(resp.json, self.valid_equipment_params)

    def test_get_equipment_given_non_existing_equipment_id_param(self):
        # Given
        request_uri_path_with_param = create_request_uri_path_with_param(
            self.base_request_uri_path,
            self.non_existing_equipment_id_request_params.get('params').get(
                'equipmentId'
            )
        )

        # When
        resp = self.client.simulate_get(
            request_uri_path_with_param,
            **self.non_existing_equipment_id_request_params
        )

        # Then
        self.assertEqual(resp.status, falcon.HTTP_404)


if __name__ == '__main__':
    unittest.main()
