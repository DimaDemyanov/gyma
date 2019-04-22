import unittest

import falcon

from gyma.vdv.Tests.Base.BaseTestCase import BaseTestCase
from gyma.vdv.Tests.Base.test_helpers import load_from_json_file, TEST_ACCOUNT

from gyma.vdv.Entities.EntitySimpleuser import EntitySimpleuser

from gyma.vdv.db import DBConnection


TEST_PARAMETERS_PATH = './simpleuser.json'


class CreateAccountTests(BaseTestCase):

    # MARK: - setUp & tearDown

    def setUp(self):
        operation_id = 'createSimpleUser'
        self.check_operation_id_has_operation_handler(operation_id)
        self.request_uri_path = self.get_request_uri_path(operation_id)

        self.valid_simpleuser_params = load_from_json_file(
            TEST_PARAMETERS_PATH)
        self.valid_simpleuser_params['accountid'] = TEST_ACCOUNT['vdvid']
        self.valid_request_params = {"json": self.valid_simpleuser_params}

        self.invalid_simpleuser_params = {"accountid": -1}
        self.invalid_request_params = {"json":  self.invalid_simpleuser_params}

    def tearDown(self):
        with DBConnection() as session:
            session.db.query(EntitySimpleuser).delete()
            session.db.commit()

    # MARK: - Tests

    def test_create_simpleuser_given_valid_params(self):
        # When
        resp = self.client.simulate_post(
            self.request_uri_path, **self.valid_request_params
        )

        # Then
        self.assertEqual(resp.status, falcon.HTTP_200)
        self.assertTrue(self._is_simpleuser_in_db(
            self.valid_simpleuser_params)
        )

    def test_create_simpleuser_given_invalid_simpleuser_params(self):
        # When
        with self.assertRaises(Exception):
            resp = self.client.simulate_post(
                self.request_uri_path, **self.invalid_request_params
            )

    def test_create_simpleuser_when_same_simpleuserid_already_exists(self):
        # When
        for i in range(2):
            resp = self.client.simulate_post(
                self.request_uri_path, **self.valid_request_params
            )

        # Then
        self.assertEqual(resp.status, falcon.HTTP_412)
        self.assertFalse(
            self._is_simpleuser_objects_increased_by_value(
                2, self.valid_simpleuser_params)
        )

    # MARK: - Private methods:

    def _is_simpleuser_in_db(self, simpleuser_params):
        created_simpleuser = EntitySimpleuser.get().filter_by(
            accountid=simpleuser_params['accountid']
        ).all()
        return len(created_simpleuser) == 1

    def _is_simpleuser_objects_increased_by_value(self, value, simpleuser_params):
        simpleuser_objects_count = EntitySimpleuser.get().filter(
            EntitySimpleuser.accountid == simpleuser_params["accountid"]
        ).count()
        return simpleuser_objects_count == value


if __name__ == '__main__':
    unittest.main()
