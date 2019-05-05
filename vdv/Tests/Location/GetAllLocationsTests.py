import unittest

import falcon

from gyma.vdv.Tests.Base.BaseTestCase import BaseTestCase
from gyma.vdv.Tests.Base.test_helpers import load_from_json_file

from gyma.vdv.Entities.EntityLocation import EntityLocation


TEST_PARAMETERS_PATH = './location.json'


class GetAllLocationsTests(BaseTestCase):

    # MARK: - setUp & tearDown

    @classmethod
    def setUpClass(cls):
        super(GetAllLocationsTests, cls).setUpClass()

        operation_id = 'getAllLocations'
        cls.check_operation_id_has_operation_handler(operation_id)
        cls.request_uri_path = cls.get_request_uri_path(operation_id)

        valid_location_params = load_from_json_file(TEST_PARAMETERS_PATH)
        cls.created_location_id = EntityLocation(
            valid_location_params.get('name'),
            valid_location_params.get('latitude'),
            valid_location_params.get('longitude'),
        ).add()

    def tearDown(self):
        if self._is_location_in_db(self.created_location_id):
            EntityLocation.delete(self.created_location_id)

    # MARK: - Tests

    def test_get_all_users_return_only_created_location(self):
        # When
        resp = self.client.simulate_get(self.request_uri_path)
        expected_result = [self._get_created_location()]

        # Then
        self.assertEqual(resp.status, falcon.HTTP_200)
        self.assertEqual(resp.json, expected_result)

    # MARK: - Private methods

    def _is_location_in_db(self, created_landlord_id):
        created_locations = self._get_created_locations()
        return len(created_locations) == 1

    def _get_created_location(self):
        created_locations = self._get_created_locations()
        try:
            created_location = created_locations[0].to_dict()
        except IndexError:
            return None
        return created_location

    def _get_created_locations(self):
        return EntityLocation.get().filter_by(
            vdvid=self.created_location_id).all()


if __name__ == '__main__':
    unittest.main()