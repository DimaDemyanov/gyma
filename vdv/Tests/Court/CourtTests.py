import sys
# TODO: FIX that:
sys.path.append("../../..")
from collections import OrderedDict
import json
import unittest

import falcon

from vdv.Tests.BaseTestCase import BaseTestCase
from vdv.app import SWAGGER_SPEC_PATH, operation_handlers


SWAGGER_SPEC_PATH = '../../../vdv/../swagger.json'



SWAGGER_SPEC = get_swagger_spec()

# class CourtAPITestCase(BaseTestCase):
#     def test_create_new_court(self):
#         pass

#     def test_get_court(self):
#         expected_response = {

#         }
#         response = self.client.simulate_get(request_url)
#         self.assertEqual(response.status, falcon.HTTP_200)
#         self.assertEqual(response.json, expected_response)


class GetAllCourtsTests(BaseTestCase):

    # MARK: - setUp & tearDown

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().setUp()

    # MARK: - Tests (GET)

    def test_get_all_courts_without_filters_sorted_by_price(self):
        operation_id = 'getAllCourts'
        params = {
            'filter1': 'all',
            'filter2': 'all',
            'sortedby': 'price',
        }

        if operation_id not in operation_handlers:
            self.assertFalse("operationId '%s' doesn't match any path" % operation_id)

        request_uri_path = get_uri_path_by_opearation_id(operation_id)
        if not request_uri_path:
            self.assertFalse("Can't get uri path for given operationId: %s" % operation_id)

        print(request_uri_path)

        # expected_response = [{}]
        # response = self.client.simulate_get('/vdv/court/filter', **{'params': params})
        # self.assertEqual(response.json, expected_response)

    def test_find_court_by_id(self):
        pass


if __name__ == '__main__':
    unittest.main()
