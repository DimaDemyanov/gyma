import unittest

import falcon

from gyma.vdv.Tests.Court.BaseCourtTestCase import BaseCourtTestCase

from gyma.vdv.Entities.EntityCourt import EntityCourt
from gyma.vdv.Entities.EntityTime import EntityTime

from gyma.vdv.Prop.PropCourtTime import PropCourtTime

from gyma.vdv.db import DBConnection


class CreateCourtTimesOnDateTests(BaseCourtTestCase):

    # MARK: - setUp & tearDown

    @classmethod
    def setUpClass(cls):
        super(CreateCourtTimesOnDateTests, cls).setUpClass()

        operation_id = 'createCourtTimesOnDate'
        cls.check_operation_id_has_operation_handler(operation_id)
        cls.request_uri_path = cls.get_request_uri_path(operation_id)

        cls.valid_court_params = cls._create_valid_court_params()
        cls.created_court_id = cls._create_court(cls.valid_court_params)

        cls.valid_court_time_param = "2030-01-01 20:00:00+00:00"
        cls.valid_request_params = {
            "json":  {
                "times": [
                    cls.valid_court_time_param
                ]
            },
            "params": {
                "courtid": str(cls.created_court_id)
            }
        }

        cls.non_existing_court_request_params = {
            "json":  {
                "times": [
                    cls.valid_court_time_param
                ]
            },
            "params": {
                "courtid": "-1"
            }
        }

    @classmethod
    def tearDownClass(cls):
        cls._delete_created_court_time_reference(cls.created_court_id)
        cls._delete_created_time()
        EntityCourt.delete(cls.created_court_id)
        super(CreateCourtTimesOnDateTests, cls).tearDownClass()

    # MARK: - Tests

    def test_create_court_time_given_valid_params(self):
        # When
        resp = self.client.simulate_post(
            self.request_uri_path, **self.valid_request_params
        )

        # Then
        self.assertEqual(resp.status, falcon.HTTP_200)
        self.assertTrue(
            self._is_court_time_in_db(self.valid_court_time_param)
        )

    def test_create_court_time_given_non_existing_court_param(self):
        # When
        resp = self.client.simulate_post(
            self.request_uri_path, **self.non_existing_court_request_params
        )

        # Then
        self.assertEqual(resp.status, falcon.HTTP_404)
        self.assertFalse(
            self._is_court_time_in_db(self.valid_court_time_param)
        )

    # MARK - Private class methods

    @classmethod
    def _delete_created_court_time_reference(cls, court_id):
        with DBConnection() as session:
            session.db.query(PropCourtTime).filter_by(vdvid=court_id).delete()
            session.db.commit()

    @classmethod
    def _delete_created_time(cls):
        with DBConnection() as session:
            session.db.query(EntityTime).delete()
            session.db.commit()

    # MARK - Private methods

    def _is_court_time_in_db(self, court_time):
        created_times = EntityTime.get().filter_by(time=court_time).all()

        if len(created_times) != 1:
            return False

        created_time_id = created_times[0].vdvid

        court_times = PropCourtTime.get().filter_by(
            vdvid=self.created_court_id, value=created_time_id
        ).all()

        return len(court_times) == 1


if __name__ == '__main__':
    unittest.main()
