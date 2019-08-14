import unittest
import sys

import falcon

from gyma.vdv.Tests.Court.BaseCourtTimeTestCase import BaseCourtTimeTestCase

from gyma.vdv.Entities.EntityCourt import EntityCourt

from gyma.vdv.Prop.PropCourtTime import PropCourtTime

from gyma.vdv.db import DBConnection



DIR_PATH = sys.path[0]
COURT_PARAMETERS_PATH = '{}/court_with_courtTime_prop.json'.format(DIR_PATH)


class GetTimesForDateTests(BaseCourtTimeTestCase):

    # MARK: - setUp & tearDown

    @classmethod
    def setUpClass(cls):
        super(GetTimesForDateTests, cls).setUpClass()

        operation_id = 'getTimesForDate'
        cls.check_operation_id_has_operation_handler(operation_id)
        cls.request_uri_path = cls.get_request_uri_path(operation_id)

        cls.valid_court_params = cls._create_valid_court_params(
            COURT_PARAMETERS_PATH
        )
        cls.valid_court_time_param = cls.valid_court_params['prop']['courtTime']
        cls.created_court_id = cls._create_court(cls.valid_court_params)

        cls.valid_request_params = {
            "params": {
                "courtid": str(cls.created_court_id),
                "date": cls.valid_court_time_param
            }
        }

        cls.non_existing_court_request_params = {
            "params": {
                "courtid": "-1",
                "date": cls.valid_court_time_param
            }
        }

    @classmethod
    def tearDownClass(cls):
        cls._delete_court_time_references(cls.created_court_id)
        cls._delete_created_times()
        EntityCourt.delete(cls.created_court_id)
        super(GetTimesForDateTests, cls).tearDownClass()

    # MARK: - Tests

    def test_get_court_time_given_valid_params(self):
        # When
        resp = self.client.simulate_get(
            self.request_uri_path, **self.valid_request_params
        )

        # Then
        self.assertEqual(resp.status, falcon.HTTP_200)
        expected_result = [
            {
                "time": "{court_date} {court_time}".format(
                    court_date=self.valid_court_params['prop']['courtTime'][0],
                    # court_date contains only date so by default time is midnight
                    court_time="00:00:00+03:00"
                    ),
                "state": "free"
            },
        ]
        self.assertEqual(resp.json, expected_result)

    def test_get_court_time_given_non_existing_court_param(self):
        # When
        resp = self.client.simulate_get(
            self.request_uri_path, **self.non_existing_court_request_params
        )

        # Then
        self.assertEqual(resp.status, falcon.HTTP_404)

    # TODO: Add new methods which create and user requests

    # MARK - Private class methods

    @classmethod
    def _delete_court_time_references(cls, court_id):
        with DBConnection() as session:
            session.db.query(PropCourtTime).filter_by(vdvid=court_id).delete()
            session.db.commit()


if __name__ == '__main__':
    unittest.main()
