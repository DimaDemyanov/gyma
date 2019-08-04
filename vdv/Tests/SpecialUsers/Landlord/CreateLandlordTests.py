import unittest
from collections import OrderedDict
import sys

import falcon

from gyma.vdv.Tests.Base.test_helpers import load_from_json_file, TEST_ACCOUNT
from gyma.vdv.Tests.SpecialUsers.Landlord.BaseLandlordTestCase import (
    BaseLandlordTestCase
)

from gyma.vdv.Entities.EntityLandlord import EntityLandlord

from gyma.vdv.db import DBConnection


TEST_PARAMETERS_PATH = '{dir_path}/landlord.json'.format(dir_path=sys.path[0])


class CreateAccountTests(BaseLandlordTestCase):

    # MARK: - setUp & tearDown

    @classmethod
    def setUpClass(cls):
        super(CreateAccountTests, cls).setUpClass()

        operation_id = 'createLandlord'
        cls.check_operation_id_has_operation_handler(operation_id)
        cls.request_uri_path = cls.get_request_uri_path(operation_id)

        # Property 'isagreerules' should be set to False in json
        # for tests passing.
        # If it is True, tests wouldn't pass but everything will work.
        # Need TOFIX maybe
        cls.valid_landlord_params = load_from_json_file(TEST_PARAMETERS_PATH)
        cls.valid_landlord_params['accountid'] = TEST_ACCOUNT['vdvid']
        cls.valid_request_params = {"json": cls.valid_landlord_params}

        cls.invalid_landlord_params = {"accountid": -1}
        cls.invalid_request_params = {"json":  cls.invalid_landlord_params}

    def tearDown(self):
        with DBConnection() as session:
            session.db.query(EntityLandlord).delete()
            session.db.commit()

    # MARK: - Tests

    def test_create_landlord_given_valid_params(self):
        # When
        resp = self.client.simulate_post(
            self.request_uri_path, **self.valid_request_params
        )

        # Then
        self.assertEqual(resp.status, falcon.HTTP_200)

        self.assertFalse(
            self._get_property_isAgreeRules(self.valid_landlord_params)
        )
        self.assertTrue(self._is_landlord_in_db(self.valid_landlord_params))

    def test_create_landlord_given_invalid_landlord_params(self):
        # When
        resp = self.client.simulate_post(
            self.request_uri_path, **self.invalid_request_params
        )

        # Then
        self.assertEqual(resp.status, falcon.HTTP_501)
        self.assertFalse(self._is_landlord_in_db(self.invalid_landlord_params))

    def test_create_landlord_given_not_json_file(self):
        # When
        resp = self.client.simulate_post(
            self.request_uri_path, **{"json": ""}
        )

        # Then
        self.assertEqual(resp.status, falcon.HTTP_405)
        self.assertFalse(self._is_landlord_in_db(self.invalid_landlord_params))

    def test_create_landlord_when_same_landlordid_already_exists(self):
        # When
        for i in range(2):
            resp = self.client.simulate_post(
                self.request_uri_path, **self.valid_request_params
            )

        # Then
        self.assertEqual(resp.status, falcon.HTTP_412)
        self.assertFalse(
            self._is_landlord_objects_increased_by_value(
                2, self.valid_landlord_params)
        )

    # MARK: - Private methods:

    def _is_landlord_in_db(self, landlord_params):
        created_landlords = EntityLandlord.get().filter_by(
            accountid=landlord_params['accountid']
        ).all()

        if len(created_landlords) != 1:
            return False

        created_landlord = created_landlords[0].to_dict()
        self.check_dict1_in_dict2(
            OrderedDict(landlord_params), created_landlord
        )
        return True

    def _is_landlord_objects_increased_by_value(self, value, landlord_params):
        landlord_objects_count = EntityLandlord.get().filter(
            EntityLandlord.accountid == landlord_params["accountid"]
        ).count()
        return landlord_objects_count == value


if __name__ == '__main__':
    unittest.main()
