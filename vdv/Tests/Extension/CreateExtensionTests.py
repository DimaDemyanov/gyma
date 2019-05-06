import unittest

import falcon

from gyma.vdv.Tests.Extension.BaseExtensionTestCase import (
    BaseExtensionTestCase
)


class CreateExtensionTests(BaseExtensionTestCase):

    # MARK: - Tests

    def test_create_extension_given_valid_params(self):
        # When
        resp = self.client.simulate_post(
            self.request_uri_path, **self.valid_request_params
        )

        # Then
        self.assertEqual(resp.status, falcon.HTTP_200)
        self.assertTrue(self._is_extension_in_db(self.valid_extension_params))

    def test_create_extension_given_invalid_extension_params(self):
        # When
        resp = self.client.simulate_post(
            self.request_uri_path, **self.invalid_request_params
        )

        # Then
        self.assertEqual(resp.status, falcon.HTTP_412)
        self.assertFalse(
            self._is_extension_in_db(self.invalid_extension_params)
        )


if __name__ == '__main__':
    unittest.main()
