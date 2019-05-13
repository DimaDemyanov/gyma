import unittest

import falcon

from gyma.vdv.Tests.Court.BaseCourtTestCase import BaseCourtTestCase
from gyma.vdv.Tests.Base.test_helpers import load_from_json_file

from gyma.vdv.Entities.EntityCourt import EntityCourt


class CreateCourtTests(BaseCourtTestCase):

    # MARK: - setUp & tearDown

    @classmethod
    def setUpClass(cls):
        super(CreateCourtTests, cls).setUpClass()

        operation_id = 'createCourt'
        cls.check_operation_id_has_operation_handler(operation_id)
        cls.request_uri_path = cls.get_request_uri_path(operation_id)

        cls.valid_court_params = cls._create_valid_court_params()
        cls.valid_request_params = {"json": cls.valid_court_params}

        cls.invalid_court_params = {}
        cls.invalid_request_params = {"json":  cls.invalid_court_params}

    def tearDown(self):
        self._delete_created_courts()

    # MARK: - Tests

    def test_create_court_given_valid_params(self):
        # When
        resp = self.client.simulate_post(
            self.request_uri_path, **self.valid_request_params
        )

        # Then
        self.assertEqual(resp.status, falcon.HTTP_200)
        self.assertTrue(self._is_court_in_db(self.valid_court_params))

    def test_create_court_given_invalid_court_params(self):
        # When
        resp = self.client.simulate_post(
            self.request_uri_path, **self.invalid_request_params
        )

        # Then
        self.assertEqual(resp.status, falcon.HTTP_405)
        self.assertFalse(
            self._is_court_in_db(self.invalid_court_params)
        )

    def test_create_court_when_court_with_same_name_already_exists(self):
        # When
        for i in range(2):
            resp = self.client.simulate_post(
                self.request_uri_path, **self.valid_request_params
            )

        # Then
        self.assertEqual(resp.status, falcon.HTTP_412)

        courts_with_same_name = EntityCourt.get().filter_by(
            name=self.valid_court_params.get('name')
        )
        self.assertEqual(courts_with_same_name.count(), 1)


if __name__ == '__main__':
    unittest.main()
