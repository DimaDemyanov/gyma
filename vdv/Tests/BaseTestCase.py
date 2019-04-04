from falcon import testing, API

from gyma.vdv.serve_swagger import SpecServer
from gyma.vdv.app import configureDBConnection, configureSwagger, operation_handlers
from gyma.vdv.db import DBConnection


class BaseTestCase(testing.TestCase):
    @classmethod
    def setUpClass(cls):
        """ Configure API and Connect to local DB """
        configureDBConnection()

        cls.api = API()
        server = SpecServer(operation_handlers=operation_handlers)

        configureSwagger(server)

        cls.api.add_sink(server, r'/')

        # TODO: Create new local DB

    def tearDown(self):
        pass

        # TODO: Drop created Elements
