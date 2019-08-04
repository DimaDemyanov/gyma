import unittest
from json.decoder import JSONDecodeError

import falcon

from gyma.vdv.Tests.Extension.BaseExtensionTestCase import (
    BaseExtensionTestCase, EXTENSION_PARAMETERS_PATH, DIR_PATH
)

from gyma.vdv.Entities.EntityExtension import EntityExtension
from gyma.vdv.Entities.EntityTariff import EntityTariff


TARIFF_PARAMETERS_PATH = '{}/tariff1.json'.format(DIR_PATH)


class UpdateExtensionTests(BaseExtensionTestCase):

    # setUp & tearDown

    @classmethod
    def setUpClass(cls):
        super(UpdateExtensionTests, cls).setUpClass()

        operation_id = 'updateExtension'
        cls.check_operation_id_has_operation_handler(operation_id)
        cls.request_uri_path = cls.get_request_uri_path(operation_id)

        cls.old_extension_params = cls._create_valid_extension_params()
        cls.new_tariff_id = cls._create_tariff(TARIFF_PARAMETERS_PATH)

    def setUp(self):
        self.created_extension_id = EntityExtension.add_from_json(
            self.old_extension_params
        )

        self.new_valid_extension_params = {
            'vdvid': str(self.created_extension_id),
            'tariffid': str(self.new_tariff_id)
        }
        self.valid_request_params = {"json": self.new_valid_extension_params}

        self.non_existing_extension_params = {
            'vdvid': -1,
            'tariffid': str(self.new_tariff_id)
        }
        self.non_existing_extension_request_params = {
            "json": self.non_existing_extension_params
        }

    def tearDown(self):
        EntityExtension.delete(self.created_extension_id)

    @classmethod
    def tearDownClass(cls):
        super(UpdateExtensionTests, cls).tearDownClass()
        EntityTariff.delete(cls.new_tariff_id)

    # Tests

    def test_update_extension_tariff_id_given_valid_params(self):
        # When
        resp = self.client.simulate_put(
            self.request_uri_path, **self.valid_request_params
        )

        # Then
        self.assertEqual(resp.status, falcon.HTTP_200)
        self.check_dict1_in_dict2(self.new_valid_extension_params, resp.json)

    def test_update_not_existing_extension(self):
        # When
        resp = self.client.simulate_put(
            self.request_uri_path, **self.non_existing_extension_request_params
        )

        # Then
        self.assertEqual(resp.status, falcon.HTTP_404)


if __name__ == '__main__':
    unittest.main()
