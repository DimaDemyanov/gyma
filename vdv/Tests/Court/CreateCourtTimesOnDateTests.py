import unittest

import falcon

from gyma.vdv.Tests.Court.BaseCourtTimeTestCase import BaseCourtTimeTestCase

from gyma.vdv.Entities.EntityCourt import EntityCourt


class CreateCourtTimesOnDateTests(BaseCourtTimeTestCase):

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
        # WARNING: be sure to delete references from PropCourtTime
        cls._delete_created_times()
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

        created_time_id = self._get_created_time_id(
            self.valid_court_time_param
        )
        self._delete_created_court_time_reference(
            self.created_court_id, created_time_id
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


if __name__ == '__main__':
    unittest.main()
