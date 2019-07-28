import unittest

import falcon

from gyma.vdv.Tests.Base.BaseTestCase import BaseTestCase
from gyma.vdv.Tests.Base.test_helpers import TEST_ACCOUNT


class CreateAccountTests(BaseTestCase):

    # MARK: - setUp & tearDown

    def setUp(self):
        operation_id = 'getAllUsers'
        self.check_operation_id_has_operation_handler(operation_id)
        self.request_uri_path = self.get_request_uri_path(operation_id)

    # MARK: - Tests

    def test_get_all_users_return_only_test_account(self):
        # When
        resp = self.client.simulate_get(self.request_uri_path)

        # Then
        self.assertEqual(resp.status, falcon.HTTP_200)
        self.assertEqual(resp.json, [TEST_ACCOUNT])


if __name__ == '__main__':
    unittest.main()
