import sys
import unittest
from collections import OrderedDict

import falcon

from gyma.vdv.Tests.Base.BaseTestCase import BaseTestCase
from gyma.vdv.Tests.Base.test_helpers import load_from_json_file, TEST_ACCOUNT

from gyma.vdv.Entities.EntityAccount import EntityAccount

from gyma.vdv.db import DBConnection


TEST_PARAMETERS_PATH = '{dir_path}/account.json'.format(dir_path=sys.path[0])


class CreateAccountTests(BaseTestCase):

    # MARK: - setUp & tearDown

    @classmethod
    def setUpClass(cls):
        super(CreateAccountTests, cls).setUpClass()

        operation_id = 'createAccount'
        cls.check_operation_id_has_operation_handler(operation_id)
        cls.request_uri_path = cls.get_request_uri_path(operation_id)

        cls.valid_account_params = load_from_json_file(TEST_PARAMETERS_PATH)
        cls.valid_request_params = {"json": cls.valid_account_params}

        # Invalid because request hasn't "name" param
        cls.invalid_account_params = {"phone": "None"}
        cls.invalid_request_params = {"json":  cls.invalid_account_params}

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
        created_accounts = EntityAccount.get().filter_by(
            phone=account_params['phone']
        ).all()

        if len(created_accounts) != 1:
            return False

        created_account = created_accounts[0].to_dict()
        self.check_dict1_in_dict2(
            OrderedDict(account_params), created_account
        )
        return True

    def _is_account_objects_increased_by_value(self, value):
        account_objects_count = EntityAccount.get().filter(
            EntityAccount.vdvid != TEST_ACCOUNT["vdvid"]
        ).count()
        return account_objects_count == value


if __name__ == '__main__':
    unittest.main()
