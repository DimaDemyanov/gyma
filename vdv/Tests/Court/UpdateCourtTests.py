import unittest

import falcon

from gyma.vdv.Tests.Court.BaseCourtTestCase import BaseCourtTestCase

from gyma.vdv.Entities.EntityCourt import EntityCourt


OLD_COURT_PARAMETERS_PATH = './court.json'
NEW_COURT_PARAMETERS_PATH = './court1.json'


class UpdateCourtTests(BaseCourtTestCase):

    # setUp & tearDown

    @classmethod
    def setUpClass(cls):
        super(UpdateCourtTests, cls).setUpClass()

        operation_id = 'updateCourt'
        cls.check_operation_id_has_operation_handler(operation_id)
        cls.request_uri_path = cls.get_request_uri_path(operation_id)

        cls.old_valid_court_params = cls._create_valid_court_params(
            OLD_COURT_PARAMETERS_PATH
        )

        cls.new_valid_court_params = cls._create_valid_court_params(
            NEW_COURT_PARAMETERS_PATH
        )
        cls.valid_request_params = {"json": cls.new_valid_court_params}

        cls.non_existing_court_params = {
            'vdvid': -1,
            'name': "new name"
        }
        cls.non_existing_court_request_params = {
            "json": cls.non_existing_court_params
        }

        cls.invalid_court_params = {}
        cls.invalid_court_request_params = {
            "json": cls.non_existing_court_params
        }

    def setUp(self):
        self.created_court_id = self._create_court(self.old_valid_court_params)

    def tearDown(self):
        EntityCourt.delete(self.created_court_id)

    # Tests

    def test_update_court_given_valid_params(self):
        # Given
        self.new_valid_court_params['vdvid'] = self.created_court_id

        # When
        resp = self.client.simulate_put(
            self.request_uri_path, **self.valid_request_params
        )

        # Then
        self.assertEqual(resp.status, falcon.HTTP_200)
        self.check_dict1_in_dict2(self.new_valid_court_params, resp.json)

    def test_update_not_existing_court(self):
        # When
        resp = self.client.simulate_put(
            self.request_uri_path, **self.non_existing_court_request_params
        )

        # Then
        self.assertEqual(resp.status, falcon.HTTP_404)

    def test_update_court_given_invalid_params(self):
        # When
        resp = self.client.simulate_put(
            self.request_uri_path, **self.invalid_court_params
        )

        # Then
        self.assertEqual(resp.status, falcon.HTTP_405)


if __name__ == '__main__':
    unittest.main()
