import unittest

import falcon

from gyma.vdv.Tests.Base.BaseTestCase import BaseTestCase
from gyma.vdv.Tests.Base.test_helpers import load_from_json_file, TEST_ACCOUNT

from gyma.vdv.Entities.EntityAccount import EntityAccount

from gyma.vdv.db import DBConnection


TEST_PARAMETERS_PATH = './account.json'


class CreateAccountTests(BaseTestCase):

    # MARK: - setUp & tearDown

    def setUp(self):
        operation_id = 'createAccount'
        self.check_operation_id_has_operation_handler(operation_id)
        self.request_uri_path = self.get_request_uri_path(operation_id)

        self.valid_account_params = load_from_json_file(TEST_PARAMETERS_PATH)
        self.valid_request_params = {"json": self.valid_account_params}

        # Invalid because request hasn't "name" param
        self.invalid_account_params = {"phone": "None"}
        self.invalid_request_params = {"json":  self.invalid_account_params}

    def tearDown(self):
        with DBConnection() as session:
            session.db.query(EntityAccount).filter(
                EntityAccount.vdvid != TEST_ACCOUNT["vdvid"]
            ).delete()
            session.db.commit()

    # MARK: - Tests

    def test_create_account_given_valid_params(self):
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

    def test_create_account_when_account_with_same_phone_already_exists(self):
        # When
        for i in range(2):
            resp = self.client.simulate_post(
                self.request_uri_path, **self.valid_request_params
            )

        # Then
        self.assertEqual(resp.status, falcon.HTTP_412)
        self.assertFalse(self._is_account_objects_increased_by_value(2))

    # MARK: - Private methods:

    def _is_account_in_db(self, account_params):
        try:
            created_account = EntityAccount.get().filter_by(
                phone=account_params['phone']
            ).all()[0].to_dict()
        except IndexError:
            return False

        all_account_objects = EntityAccount.get().all()
        all_accounts = [o.to_dict() for o in all_account_objects]

        return created_account in all_accounts

    def _is_account_objects_increased_by_value(self, value):
        with DBConnection() as session:
            account_objects_count = session.db.query(EntityAccount).filter(
                EntityAccount.vdvid != TEST_ACCOUNT["vdvid"]
            ).count()
        return account_objects_count == value


if __name__ == '__main__':
    unittest.main()
