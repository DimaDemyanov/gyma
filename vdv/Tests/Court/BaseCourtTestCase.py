import sys
from collections import OrderedDict

from gyma.vdv.Tests.Base.BaseTestCase import BaseTestCase
from gyma.vdv.Tests.Base.test_helpers import load_from_json_file, TEST_ACCOUNT

from gyma.vdv.Entities.EntityCourt import EntityCourt
from gyma.vdv.Entities.EntityLandlord import EntityLandlord

from gyma.vdv.db import DBConnection


DIR_PATH = sys.path[0]
LANDLORD_PARAMETERS_PATH = '{}/landlord.json'.format(DIR_PATH)
COURT_PARAMETERS_PATH = '{}/court.json'.format(DIR_PATH)


class BaseCourtTestCase(BaseTestCase):

    # MARK: - setUp & tearDown

    @classmethod
    def setUpClass(cls):
        super(BaseCourtTestCase, cls).setUpClass()
        cls.created_landlord_id = cls._create_landlord()

    @classmethod
    def tearDownClass(cls):
        super(BaseCourtTestCase, cls).tearDownClass()
        EntityLandlord.delete(cls.created_landlord_id)

    # MARK: - Private methods:

    def _is_court_in_db(self, court_params):
        created_courts = EntityCourt.get().filter_by(
            name=court_params.get('name')
        ).all()

        if len(created_courts) != 1:
            return False

        created_court = created_courts[0].to_dict()
        self.check_dict1_in_dict2(
            OrderedDict(court_params), created_court
        )
        return True

    def _delete_created_courts(self):
        with DBConnection() as session:
            session.db.query(EntityCourt).delete()
            session.db.commit()

    # MARK: - Private class methods

    @classmethod
    def _create_court(cls, court_params):
        created_court_id = EntityCourt.add_from_json(court_params)
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
    def _create_valid_court_params(cls, court_params_path=COURT_PARAMETERS_PATH):
        valid_court_params = load_from_json_file(court_params_path)
        valid_court_params['ownerid'] = str(cls.created_landlord_id)
        return valid_court_params

    # MARK: - Private methods

    def _get_property_isPublished(self, court_params):
        with DBConnection() as session:
            ispublished_property_of_courts_with_same_name = session.db.query(
                EntityCourt.ispublished
            ).filter_by(name=court_params.get('name')).all()

        # len == 1 because there should be only 1 court with given name
        if len(ispublished_property_of_courts_with_same_name) != 1:
            return None

        # It is list of 1 tuple with 1 element: isPublished property
        isPublished = ispublished_property_of_courts_with_same_name[0][0]

        return isPublished
