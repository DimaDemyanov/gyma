from collections import OrderedDict

from gyma.vdv.Tests.Base.BaseTestCase import BaseTestCase
from gyma.vdv.Tests.Base.test_helpers import load_from_json_file, TEST_ACCOUNT

from gyma.vdv.Entities.EntityExtension import EntityExtension
from gyma.vdv.Entities.EntityCourt import EntityCourt
from gyma.vdv.Entities.EntityLandlord import EntityLandlord
from gyma.vdv.Entities.EntityTariff import EntityTariff

from gyma.vdv.db import DBConnection


EXTENSION_PARAMETERS_PATH = './extension.json'
LANDLORD_PARAMETERS_PATH = './landlord.json'
COURT_PARAMETERS_PATH = './court.json'
TARIFF_PARAMETERS_PATH = './tariff.json'


class BaseExtensionTestCase(BaseTestCase):

    # MARK: - setUp & tearDown

    @classmethod
    def setUpClass(cls):
        super(BaseExtensionTestCase, cls).setUpClass()

        operation_id = 'createExtension'
        cls.check_operation_id_has_operation_handler(operation_id)
        cls.request_uri_path = cls.get_request_uri_path(operation_id)

        cls.created_court_id = cls._create_court()
        cls.created_tariff_id = cls._create_tariff()

        cls.valid_extension_params = cls._create_valid_extension_params()
        cls.valid_request_params = {"json": cls.valid_extension_params}

        cls.invalid_extension_params = {}
        cls.invalid_request_params = {"json":  cls.invalid_extension_params}

    @classmethod
    def tearDownClass(cls):
        with DBConnection() as session:
            session.db.query(EntityExtension).filter_by(
                courtid=cls.created_court_id,
                tariffid=cls.created_tariff_id
            ).delete()

            session.db.query(EntityCourt).filter_by(
                vdvid=cls.created_court_id
            ).delete()

            session.db.query(EntityLandlord).filter_by(
                vdvid=cls.created_landlord_id
            ).delete()

            session.db.query(EntityTariff).filter_by(
                vdvid=cls.created_tariff_id
            ).delete()

            session.db.commit()

    # MARK: - Private methods:

    def _is_extension_in_db(self, extension_params):
        created_extensions = EntityExtension.get().filter_by(
            courtid=extension_params.get('courtid'),
            tariffid=extension_params.get('tariffid')
        ).all()

        if len(created_extensions) != 1:
            return False

        created_extension = created_extensions[0].to_dict()
        self.check_dict1_in_dict2(
            OrderedDict(extension_params), created_extension
        )
        return True

    # MARK: - Private class methods

    @classmethod
    def _create_valid_extension_params(cls):
        valid_extension_params = load_from_json_file(EXTENSION_PARAMETERS_PATH)
        valid_extension_params['courtid'] = str(cls.created_court_id)
        valid_extension_params['tariffid'] = str(cls.created_tariff_id)
        return valid_extension_params

    @classmethod
    def _create_tariff(cls):
        valid_tariff_params = load_from_json_file(TARIFF_PARAMETERS_PATH)

        created_tariff_id = EntityTariff.add_from_json(valid_tariff_params)
        return created_tariff_id

    @classmethod
    def _create_court(cls):
        cls.created_landlord_id = cls._create_landlord()
        valid_court_params = load_from_json_file(COURT_PARAMETERS_PATH)
        valid_court_params['ownerid'] = str(cls.created_landlord_id)

        created_court_id = EntityCourt.add_from_json(valid_court_params)
        return created_court_id

    @classmethod
    def _create_landlord(cls):
        valid_landlord_params = load_from_json_file(LANDLORD_PARAMETERS_PATH)
        valid_landlord_params['accountid'] = TEST_ACCOUNT['vdvid']

        created_landlord_id = EntityLandlord.add_from_json(
            valid_landlord_params
        )
        return created_landlord_id
