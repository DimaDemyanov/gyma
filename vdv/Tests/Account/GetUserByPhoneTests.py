import unittest

import falcon

from gyma.vdv.Tests.Base.BaseTestCase import BaseTestCase
from gyma.vdv.Tests.Base.test_helpers import TEST_ACCOUNT


class GetUserByPhoneTests(BaseTestCase):

    # setUp & tearDown

    @classmethod
    def setUpClass(cls):
        super(GetUserByPhoneTests, cls).setUpClass()

        operation_id = 'getUserByPhone'
        cls.check_operation_id_has_operation_handler(operation_id)
        cls.request_uri_path = cls.get_request_uri_path(operation_id)

        cls.valid_request_params = {
            "params": {
                "phone": TEST_ACCOUNT['phone']
            }
        }
        cls.non_existing_phone_request_params = {
            "params": {
                "phone": "0"
            }
        }

    # Tests

    def test_get_user_given_valid_phone_param(self):
        # When
        resp = self.client.simulate_get(
            self.request_uri_path, **self.valid_request_params
        )

        # Then
        self.assertEqual(resp.status, falcon.HTTP_200)
        self.check_dict1_in_dict2(resp.json, TEST_ACCOUNT)

    def test_get_user_not_given_phone_param(self):
        # When
        resp = self.client.simulate_get(self.request_uri_path)

        # Then
        self.assertEqual(resp.status, falcon.HTTP_407)

    def test_get_user_given_non_existing_phone_param(self):
        # When
        resp = self.client.simulate_get(
            self.request_uri_path, **self.non_existing_phone_request_params
        )

        # Then
        self.assertEqual(resp.status, falcon.HTTP_404)


if __name__ == '__main__':
    unittest.main()
