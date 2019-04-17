import unittest

import falcon

from gyma.vdv.Tests.Base.BaseTestCase import BaseTestCase
from gyma.vdv.Tests.Base.test_helpers import load_from_json_file, TEST_ACCOUNT

# from gyma.vdv.Entities.EntityAccount import EntityAccount
from gyma.vdv.Entities.EntityLandlord import EntityLandlord

from gyma.vdv.db import DBConnection


TEST_PARAMETERS_PATH = './landlord.json'


class CreateAccountTests(BaseTestCase):

    # MARK: - setUp & tearDown

    def setUp(self):
        operation_id = 'createLandlord'
        self.check_operation_id_has_operation_handler(operation_id)
        self.request_uri_path = self.get_request_uri_path(operation_id)

        self.valid_account_params = load_from_json_file(TEST_PARAMETERS_PATH)
        self.valid_request_params = {"json": self.valid_account_params}

        # Invalid because request hasn't "name" param
        self.invalid_account_params = {"accountid": -1}
        self.invalid_request_params = {"json":  self.invalid_account_params}

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
        self.assertTrue(self._is_account_in_db(self.valid_account_params))

    def test_create_account_given_invalid_account_params(self):
        # When
        resp = self.client.simulate_post(
            self.request_uri_path, **self.invalid_request_params
        )

        # Then
        self.assertEqual(resp.status, falcon.HTTP_501)
        self.assertFalse(self._is_account_in_db(self.invalid_account_params))

    def test_create_account_given_not_json_file(self):
        # When
        resp = self.client.simulate_post(
            self.request_uri_path, **{"json": ""}
        )

        # Then
        self.assertEqual(resp.status, falcon.HTTP_405)
        self.assertFalse(self._is_account_in_db(self.invalid_account_params))

    def test_create_landlord_when_same_accountid_already_exists(self):
        # When
        for i in range(2):
            resp = self.client.simulate_post(
                self.request_uri_path, **self.valid_request_params
            )

        # Then
        self.assertEqual(resp.status, falcon.HTTP_412)
        self.assertFalse(
            self._is_account_objects_increased_by_value(
                2, self.valid_account_params)
        )

    # MARK: - Private methods:

    def _is_account_in_db(self, account_params):
        created_account = EntityLandlord.get().filter_by(
            accountid=account_params['accountid']
        ).all()
        return len(created_account) == 1

    def _is_account_objects_increased_by_value(self, value, account_params):
        account_objects_count = EntityLandlord.get().filter(
            EntityLandlord.accountid == account_params["accountid"]
        ).count()
        return account_objects_count == value


if __name__ == '__main__':
    unittest.main()
