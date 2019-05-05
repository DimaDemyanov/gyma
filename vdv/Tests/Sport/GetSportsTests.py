import unittest
from collections import OrderedDict

import falcon

from gyma.vdv.Tests.Base.test_helpers import load_from_json_file, TEST_ACCOUNT
from gyma.vdv.Tests.Sport.SportTestCase import SportTestCase

from gyma.vdv.Entities.EntitySport import EntitySport

from gyma.vdv.db import DBConnection


TEST_PARAMETERS_PATH = './sport.json'


class GetSportsTests(SportTestCase):

    # MARK: - setUp & tearDown

    @classmethod
    def setUpClass(cls):
        super(GetSportsTests, cls).setUpClass()

        cls.valid_sport_params = load_from_json_file(TEST_PARAMETERS_PATH)
        cls.created_sport_id = EntitySport.add_from_json(
            cls.valid_sport_params
        )
        cls.valid_sport_params['vdvid'] = str(cls.created_sport_id)

    def tearDown(self):
        with DBConnection() as session:
            session.db.query(EntitySport).delete()
            session.db.commit()

    # MARK: - Tests

    def test_get_sports_returns_only_created_sport(self):
        # When
        resp = self.client.simulate_get(self.request_uri_path)

        expected_result = [self.valid_sport_params]

        # Then
        self.assertEqual(resp.status, falcon.HTTP_200)
        self.assertEqual(resp.json, expected_result)
        self.assertTrue(self._is_sport_in_db(self.valid_sport_params))

    # MARK: - Private methods:

    # TODO: Create SportTestCase with method below for reuse
    def _is_sport_in_db(self, sport_params):
        created_sports = EntitySport.get().filter_by(
            name=sport_params.get('name')
        ).all()

        if len(created_sports) != 1:
            return False

        created_sport = created_sports[0].to_dict()
        self.check_dict1_in_dict2(
            OrderedDict(sport_params), created_sport
        )
        return True


if __name__ == '__main__':
    unittest.main()
