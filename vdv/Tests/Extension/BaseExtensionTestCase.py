from collections import OrderedDict
import sys

from gyma.vdv.Tests.Base.BaseTestCase import BaseTestCase
from gyma.vdv.Tests.Base.test_helpers import load_from_json_file, TEST_ACCOUNT

from gyma.vdv.Entities.EntityExtension import EntityExtension
from gyma.vdv.Entities.EntityCourt import EntityCourt
from gyma.vdv.Entities.EntityLandlord import EntityLandlord
from gyma.vdv.Entities.EntityTariff import EntityTariff

from gyma.vdv.db import DBConnection


DIR_PATH = sys.path[0]

EXTENSION_PARAMETERS_PATH = '{}/extension.json'.format(DIR_PATH)
LANDLORD_PARAMETERS_PATH = '{}/landlord.json'.format(DIR_PATH)
COURT_PARAMETERS_PATH = '{}/court.json'.format(DIR_PATH)
TARIFF_PARAMETERS_PATH = '{}/tariff.json'.format(DIR_PATH)


class BaseExtensionTestCase(BaseTestCase):

    # MARK: - setUp & tearDown

    @classmethod
    def setUpClass(cls):
        super(BaseExtensionTestCase, cls).setUpClass()
        cls.created_court_id = cls._create_court()
        cls.created_tariff_id = cls._create_tariff()

    @classmethod
    def tearDownClass(cls):
        super(BaseExtensionTestCase, cls).tearDownClass()
        with DBConnection() as session:
            session.db.query(EntityExtension).filter_by(
                courtid=cls.created_court_id,
                tariffid=cls.created_tariff_id
            ).delete()
            session.db.commit()

        EntityCourt.delete(cls.created_court_id)
        EntityLandlord.delete(cls.created_landlord_id)
        EntityTariff.delete(cls.created_tariff_id)

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
    def _delete_created_extension(self, extension_id):
        try:
            EntityExtension.delete(extension_id)
        except FileNotFoundError:
            pass

    @classmethod
    def _create_tariff(cls, tariff_params_path=TARIFF_PARAMETERS_PATH):
        valid_tariff_params = load_from_json_file(tariff_params_path)

        created_tariff_id = EntityTariff.add_from_json(valid_tariff_params)
        return created_tariff_id

    @classmethod
    def _create_court(cls, court_params_path=COURT_PARAMETERS_PATH):
        cls.created_landlord_id = cls._create_landlord()
        valid_court_params = load_from_json_file(court_params_path)
        valid_court_params['ownerid'] = str(cls.created_landlord_id)

        created_court_id = EntityCourt.add_from_json(valid_court_params)
        return created_court_id

    @classmethod
    def _create_landlord(cls, landlord_params_path=LANDLORD_PARAMETERS_PATH):
        valid_landlord_params = load_from_json_file(landlord_params_path)
        valid_landlord_params['accountid'] = TEST_ACCOUNT['vdvid']

        created_landlord_id = EntityLandlord.add_from_json(
            valid_landlord_params
        )
        return created_landlord_id

    @classmethod
    def _create_valid_extension_params(cls):
        valid_extension_params = load_from_json_file(EXTENSION_PARAMETERS_PATH)
        valid_extension_params['courtid'] = str(cls.created_court_id)
        valid_extension_params['tariffid'] = str(cls.created_tariff_id)
        return valid_extension_params
