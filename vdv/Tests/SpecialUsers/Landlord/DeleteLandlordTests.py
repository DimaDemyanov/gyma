import unittest
import sys

import falcon

from gyma.vdv.Tests.Base.BaseTestCase import BaseTestCase
from gyma.vdv.Tests.Base.test_helpers import (
    load_from_json_file, create_request_uri_path_with_param, TEST_ACCOUNT
)

from gyma.vdv.Entities.EntityLandlord import EntityLandlord

from gyma.vdv.db import DBConnection


TEST_PARAMETERS_PATH = '{dir_path}/landlord.json'.format(dir_path=sys.path[0])


class DeleteLandlordTests(BaseTestCase):

    # MARK: - setUp & tearDown

    @classmethod
    def setUpClass(cls):
        super(DeleteLandlordTests, cls).setUpClass()

        operation_id = 'deleteLandlord'
        cls.check_operation_id_has_operation_handler(operation_id)
        cls.base_request_uri_path = cls.get_request_uri_path(operation_id)

        cls.new_landlord_params = load_from_json_file(TEST_PARAMETERS_PATH)
        cls.new_landlord_params['accountid'] = TEST_ACCOUNT['vdvid']

    def setUp(self):
        self.created_landlord_id = EntityLandlord.add_from_json(
            self.new_landlord_params
        )
        self.valid_request_params = {
            "params": {
                "landlordId": self.created_landlord_id
            }
        }
        self.non_existing_landlord_id_request_params = {
            "params": {
                "landlordId": "0"
            }
        }

    def tearDown(self):
        if self._is_landlord_in_db(self.created_landlord_id):
            EntityLandlord.delete(self.created_landlord_id)

    # MARK: - Tests

    def test_delete_landlord_given_valid_landlord_id_param(self):
        # Given
        request_uri_path_with_param = create_request_uri_path_with_param(
            self.base_request_uri_path,
            self.valid_request_params['params']['landlordId']
        )

        # When
        resp = self.client.simulate_delete(
            request_uri_path_with_param, **self.valid_request_params
        )

        # Then
        self.assertEqual(resp.status, falcon.HTTP_200)
        self.assertFalse(self._is_landlord_in_db(self.created_landlord_id))

    def test_delete_landlord_given_non_existing_landlord_id_param(self):
        # Given
        request_uri_path_with_param = create_request_uri_path_with_param(
            self.base_request_uri_path,
            self.non_existing_landlord_id_request_params['params']['landlordId']
        )

        # When
        resp = self.client.simulate_delete(
            request_uri_path_with_param,
            **self.non_existing_landlord_id_request_params
        )

        # Then
        self.assertEqual(resp.status, falcon.HTTP_404)

    # MARK: - Private methods:

    def _is_landlord_in_db(self, created_landlord_id):
        created_landlord = EntityLandlord.get().filter_by(
            vdvid=created_landlord_id
        ).all()
        return len(created_landlord) == 1


if __name__ == '__main__':
    unittest.main()
