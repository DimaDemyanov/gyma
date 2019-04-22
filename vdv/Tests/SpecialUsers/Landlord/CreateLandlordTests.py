import unittest
from collections import OrderedDict

import falcon

from gyma.vdv.Tests.Base.BaseTestCase import BaseTestCase
from gyma.vdv.Tests.Base.test_helpers import load_from_json_file, TEST_ACCOUNT

from gyma.vdv.Entities.EntityLandlord import EntityLandlord

from gyma.vdv.db import DBConnection


TEST_PARAMETERS_PATH = './landlord.json'


class CreateAccountTests(BaseTestCase):

    # MARK: - setUp & tearDown

    def setUp(self):
        operation_id = 'createLandlord'
        self.check_operation_id_has_operation_handler(operation_id)
        self.request_uri_path = self.get_request_uri_path(operation_id)

        self.valid_landlord_params = load_from_json_file(TEST_PARAMETERS_PATH)
        self.valid_landlord_params['accountid'] = TEST_ACCOUNT['vdvid']

        self.valid_request_params = {"json": self.valid_landlord_params}

        self.invalid_landlord_params = {"accountid": -1}
        self.invalid_request_params = {"json":  self.invalid_landlord_params}

    def tearDown(self):
        with DBConnection() as session:
            session.db.query(EntityLandlord).delete()
            session.db.commit()

    # MARK: - Tests

    def test_create_landlord_given_valid_params(self):
        # When
        resp = self.client.simulate_post(
            self.request_uri_path, **self.valid_request_params
        )

        # Then
        self.assertEqual(resp.status, falcon.HTTP_200)
        self.assertTrue(self._is_landlord_in_db(self.valid_landlord_params))

    def test_create_landlord_given_invalid_landlord_params(self):
        # When
        resp = self.client.simulate_post(
            self.request_uri_path, **self.invalid_request_params
        )

        # Then
        self.assertEqual(resp.status, falcon.HTTP_501)
        self.assertFalse(self._is_landlord_in_db(self.invalid_landlord_params))

    def test_create_landlord_given_not_json_file(self):
        # When
        resp = self.client.simulate_post(
            self.request_uri_path, **{"json": ""}
        )

        # Then
        self.assertEqual(resp.status, falcon.HTTP_405)
        self.assertFalse(self._is_landlord_in_db(self.invalid_landlord_params))

    def test_create_landlord_when_same_landlordid_already_exists(self):
        # When
        for i in range(2):
            resp = self.client.simulate_post(
                self.request_uri_path, **self.valid_request_params
            )

        # Then
        self.assertEqual(resp.status, falcon.HTTP_412)
        self.assertFalse(
            self._is_landlord_objects_increased_by_value(
                2, self.valid_landlord_params)
        )

    # MARK: - Private methods:

    def _is_landlord_in_db(self, landlord_params):
        created_landlord = EntityLandlord.get().filter_by(
            accountid=landlord_params['accountid']
        ).all()

        if len(created_landlord) != 1:
            return False

        created_landlord = created_landlord[0].to_dict()
        self.check_dict1_in_dict2(
            OrderedDict(landlord_params), created_landlord
        )
        return True

    def _is_landlord_objects_increased_by_value(self, value, landlord_params):
        landlord_objects_count = EntityLandlord.get().filter(
            EntityLandlord.accountid == landlord_params["accountid"]
        ).count()
        return landlord_objects_count == value


if __name__ == '__main__':
    unittest.main()
