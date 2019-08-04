import unittest

import falcon

from gyma.vdv.Tests.Base.BaseTestCase import BaseTestCase
from gyma.vdv.Tests.Base.test_helpers import TEST_ACCOUNT


class GetMyUserTests(BaseTestCase):

    # setUp & tearDown

    @classmethod
    def setUpClass(cls):
        super(GetMyUserTests, cls).setUpClass()

        operation_id = 'getMyUser'
        cls.check_operation_id_has_operation_handler(operation_id)
        cls.request_uri_path = cls.get_request_uri_path(operation_id)

    # Tests

    def test_get_my_user_with_valid_phone(self):
        """Logged in as Test User from BaseTestCase Auth middleware.
        So request should return TEST_ACCOUNT params"""

        # When
        resp = self.client.simulate_get(self.request_uri_path)

        # Then
        self.assertEqual(resp.status, falcon.HTTP_200)
        self.check_dict1_in_dict2(resp.json, TEST_ACCOUNT)


if __name__ == '__main__':
    unittest.main()