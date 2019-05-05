import unittest
from collections import OrderedDict

import falcon

from gyma.vdv.Tests.Base.test_helpers import load_from_json_file, TEST_ACCOUNT
from gyma.vdv.Tests.Sport.BaseSportTestCase import BaseSportTestCase

from gyma.vdv.Entities.EntitySport import EntitySport

from gyma.vdv.db import DBConnection


TEST_PARAMETERS_PATH = './sport.json'


class CreateSportTests(BaseSportTestCase):

    # MARK: - setUp & tearDown

    @classmethod
    def setUpClass(cls):
        super(CreateSportTests, cls).setUpClass()

        cls.valid_sport_params = load_from_json_file(TEST_PARAMETERS_PATH)
        cls.valid_request_params = {"json": cls.valid_sport_params}

        cls.invalid_sport_params = {}
        cls.invalid_request_params = {"json":  {}}

    def tearDown(self):
        with DBConnection() as session:
            session.db.query(EntitySport).delete()
            session.db.commit()

    # MARK: - Tests

    def test_create_sport_given_valid_params(self):
        # When
        resp = self.client.simulate_post(
            self.request_uri_path, **self.valid_request_params
        )

        # Then
        self.assertEqual(resp.status, falcon.HTTP_200)
        self.assertTrue(self._is_sport_in_db(self.valid_sport_params))

    def test_create_sport_given_invalid_sport_params(self):
        # When
        resp = self.client.simulate_post(
            self.request_uri_path, **self.invalid_request_params
        )

        # Then
        self.assertEqual(resp.status, falcon.HTTP_501)
        self.assertFalse(self._is_sport_in_db(self.invalid_sport_params))

    def test_create_sport_when_same_sport_already_exists(self):
        # When
        for i in range(2):
            resp = self.client.simulate_post(
                self.request_uri_path, **self.valid_request_params
            )

        # Then
        self.assertEqual(resp.status, falcon.HTTP_412)
        self.assertFalse(
            self._is_sport_objects_increased_by_value(
                2, self.valid_sport_params)
        )

    # MARK: - Private methods:

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

    def _is_sport_objects_increased_by_value(self, value, sport_params):
        sport_objects_count = EntitySport.get().filter_by(
            name=sport_params.get("name")
        ).count()
        return sport_objects_count == value


if __name__ == '__main__':
    unittest.main()
