import unittest
from collections import OrderedDict

import falcon

from gyma.vdv.Tests.Base.BaseTestCase import BaseTestCase
from gyma.vdv.Tests.Base.test_helpers import (
    load_from_json_file, TEST_ACCOUNT, convert_dict_bool_str_values_to_bool
)

from gyma.vdv.Entities.EntityLocation import EntityLocation

from gyma.vdv.db import DBConnection


TEST_PARAMETERS_PATH = './location.json'


class LoactionTestCase(BaseTestCase):
    @classmethod
    def setUpClass(cls):
        super(LoactionTestCase, cls).setUpClass()

        operation_id = 'createLocation'
        cls.check_operation_id_has_operation_handler(operation_id)
        cls.request_uri_path = cls.get_request_uri_path(operation_id)

        cls.valid_location_params = load_from_json_file(TEST_PARAMETERS_PATH)
        cls.valid_request_params = {"json": cls.valid_location_params}

        # Invalid because request hasn't "name" param
        # cls.invalid_location_params = {"longitude": "40.9823", "latitude": "2"}
        cls.invalid_location_params = {"latitude": "2"}
        cls.invalid_request_params = {"json":  cls.invalid_location_params}

    def check_dict1_in_dict2(self, dict1, dict2):
        convert_dict_bool_str_values_to_bool(dict1)
        convert_dict_bool_str_values_to_bool(dict2)

        for dict1_key, dict1_value in dict1.items():
            if dict1_key == 'vdvid':
                continue
            try:
                dict1_value = round(float(dict1_value), 4)
            except ValueError:
                continue
            dict2_value = dict2[dict1_key]
            if type(dict1_value) is dict:
                self.check_dict1_in_dict2(dict2_value, dict1_value)
            else:
                self.assertEqual(dict2_value, dict1_value)


class CreateLocationTests(LoactionTestCase):

    # MARK: - setUp & tearDown

    def tearDown(self):
        with DBConnection() as session:
            session.db.query(EntityLocation).delete()
            session.db.commit()

    # MARK: - Tests

    def test_create_location_given_valid_params(self):
        # When
        resp = self.client.simulate_post(
            self.request_uri_path, **self.valid_request_params
        )

        # Then
        self.assertEqual(resp.status, falcon.HTTP_200)
        self.assertTrue(self._is_location_in_db(self.valid_location_params))

    def test_create_location_given_invalid_location_params(self):
        # When
        resp = self.client.simulate_post(
            self.request_uri_path, **self.invalid_request_params
        )

        # Then
        self.assertEqual(resp.status, falcon.HTTP_405)
        self.assertFalse(self._is_location_in_db(self.invalid_location_params))

    def test_create_location_given_not_json_file(self):
        # When
        resp = self.client.simulate_post(
            self.request_uri_path, **{"json": {}}
        )

        # Then
        self.assertEqual(resp.status, falcon.HTTP_405)
        self.assertFalse(self._is_location_in_db(self.invalid_location_params))

    def test_create_location_when_location_with_same_name_already_exists(self):
        # When
        for i in range(2):
            resp = self.client.simulate_post(
                self.request_uri_path, **self.valid_request_params
            )

        # Then
        self.assertEqual(resp.status, falcon.HTTP_412)
        self.assertFalse(self._is_location_objects_increased_by_value(2))

    # MARK: - Private methods:

    def _is_location_in_db(self, location_params):
        created_locations = EntityLocation.get().filter_by(
            name=location_params.get('name')
        ).all()

        if len(created_locations) != 1:
            return False

        created_location = created_locations[0].to_dict()
        self.check_dict1_in_dict2(
            OrderedDict(location_params), created_location
        )
        return True

    def _is_location_objects_increased_by_value(self, value):
        location_objects_count = EntityLocation.get().count()
        return location_objects_count == value


if __name__ == '__main__':
    unittest.main()
