import unittest

import falcon

from gyma.vdv.Tests.Base.BaseTestCase import BaseTestCase
from gyma.vdv.Tests.Base.test_helpers import (
    TEST_ACCOUNT, create_request_uri_path_with_param
)


class GetMyUserTests(BaseTestCase):

    # setUp & tearDown

    def setUp(self):
        operation_id = 'getUser'
        self.check_operation_id_has_operation_handler(operation_id)
        self.base_request_uri_path = self.get_request_uri_path(operation_id)

        self.valid_request_params = {
            "params": {
                "userId": TEST_ACCOUNT['vdvid']
            }
        }
        self.non_existing_user_id_request_params = {
            "params": {
                "userId": "0"
            }
        }

    # Tests

    def test_get_user_given_valid_user_id_param(self):
        # Given
        request_uri_path_with_param = create_request_uri_path_with_param(
            self.base_request_uri_path,
            self.valid_request_params['params']['userId']
        )

        # When
        resp = self.client.simulate_get(
            request_uri_path_with_param, **self.valid_request_params
        )

        # Then
        self.assertEqual(resp.status, falcon.HTTP_200)
        self.check_dict1_in_dict2(resp.json, TEST_ACCOUNT)

    def test_get_user_given_non_existing_user_id_param(self):
        # Given
        request_uri_path_with_param = create_request_uri_path_with_param(
            self.base_request_uri_path,
            self.non_existing_user_id_request_params['params']['userId']
        )

        # When
        resp = self.client.simulate_get(
            request_uri_path_with_param,
            **self.non_existing_user_id_request_params
        )

        # Then
        self.assertEqual(resp.status, falcon.HTTP_404)


if __name__ == '__main__':
    unittest.main()