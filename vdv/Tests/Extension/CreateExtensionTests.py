import unittest

import falcon

from gyma.vdv.Tests.Extension.BaseExtensionTestCase import (
    BaseExtensionTestCase, EXTENSION_PARAMETERS_PATH
)

from gyma.vdv.Tests.Base.test_helpers import load_from_json_file


class CreateExtensionTests(BaseExtensionTestCase):

    # MARK: - setUp & tearDown

    @classmethod
    def setUpClass(cls):
        super(CreateExtensionTests, cls).setUpClass()

        operation_id = 'createExtension'
        cls.check_operation_id_has_operation_handler(operation_id)
        cls.request_uri_path = cls.get_request_uri_path(operation_id)

        cls.valid_extension_params = cls._create_valid_extension_params()
        cls.valid_request_params = {"json": cls.valid_extension_params}

        cls.invalid_extension_params = {}
        cls.invalid_request_params = {"json":  cls.invalid_extension_params}

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

    # MARK: - Private class methods

    @classmethod
    def _create_valid_extension_params(cls):
        valid_extension_params = load_from_json_file(EXTENSION_PARAMETERS_PATH)
        valid_extension_params['courtid'] = str(cls.created_court_id)
        valid_extension_params['tariffid'] = str(cls.created_tariff_id)
        return valid_extension_params


if __name__ == '__main__':
    unittest.main()
