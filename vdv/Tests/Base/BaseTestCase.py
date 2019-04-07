import os

from falcon import testing, API

from gyma.vdv.serve_swagger import SpecServer
from gyma.vdv.app import configureDBConnection, configureSwagger, operation_handlers
from gyma.vdv.db import DBConnection

from gyma.vdv.Tests.Base import test_helpers


SWAGGER_TEMP_PATH = "./swagger_temp.json"


class AuthenticationForTest(object):
    def process_request(self, req, resp):
        req.context['phone'] = '79110001122'


class BaseTestCase(testing.TestCase):

    # MARK: - setUp & tearDown

    @classmethod
    def setUpClass(cls):
        """ Configure API and Connect to local DB """
        configureDBConnection()
        cls.api = API(middleware=[AuthenticationForTest()])
        server = SpecServer(operation_handlers=operation_handlers)
        configureSwagger(server)
        cls.api.add_sink(server, r'/')
        cls.client = testing.TestClient(cls.api)

    @classmethod
    def tearDownClass(cls):
        cls.__remove_swagger_temp()

    # MARK: - Public methods

    def check_operation_id_has_operation_handler(self, operation_id):
        if operation_id not in operation_handlers:
            self.fail("operationId '%s' doesn't match operation handler" % operation_id)

    def get_request_uri_path(self, operation_id):
        request_uri_path = test_helpers.get_uri_path_by_opearation_id(operation_id)
        if not request_uri_path:
            self.fail("Can't get uri path for given operationId: %s" % operation_id)
        return request_uri_path

    # MARK: - Private methods

    def __remove_swagger_temp(swagger_temp_path=SWAGGER_TEMP_PATH):
        if os.path.exists(swagger_temp_path):
            os.remove(swagger_temp_path)
