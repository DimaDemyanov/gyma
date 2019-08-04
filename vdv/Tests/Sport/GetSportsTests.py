import unittest
from collections import OrderedDict
import sys

import falcon

from gyma.vdv.Tests.Base.test_helpers import load_from_json_file, TEST_ACCOUNT
from gyma.vdv.Tests.Sport.BaseSportTestCase import BaseSportTestCase

from gyma.vdv.Entities.EntitySport import EntitySport

from gyma.vdv.db import DBConnection


TEST_PARAMETERS_PATH = '{dir_path}/sport.json'.format(dir_path=sys.path[0])


class GetSportsTests(BaseSportTestCase):

    # MARK: - setUp & tearDown

    @classmethod
    def setUpClass(cls):
        super(GetSportsTests, cls).setUpClass()

        operation_id = 'getSports'
        cls.check_operation_id_has_operation_handler(operation_id)
        cls.request_uri_path = cls.get_request_uri_path(operation_id)

        cls.valid_sport_params = load_from_json_file(TEST_PARAMETERS_PATH)
        cls.created_sport_id = EntitySport.add_from_json(
            cls.valid_sport_params
        )
        cls.valid_sport_params['vdvid'] = str(cls.created_sport_id)

    def tearDown(self):
        self._delete_created_sports()

    # MARK: - Tests

    def test_get_sports_returns_only_created_sport(self):
        # When
        resp = self.client.simulate_get(self.request_uri_path)

        expected_result = [self.valid_sport_params]

        # Then
        self.assertEqual(resp.status, falcon.HTTP_200)
        self.assertEqual(resp.json, expected_result)
        self.assertTrue(self._is_sport_in_db(self.valid_sport_params))


if __name__ == '__main__':
    unittest.main()
