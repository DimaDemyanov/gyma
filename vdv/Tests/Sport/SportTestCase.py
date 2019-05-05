import unittest
from collections import OrderedDict

from gyma.vdv.Tests.Base.BaseTestCase import BaseTestCase

from gyma.vdv.Entities.EntitySport import EntitySport


class SportTestCase(BaseTestCase):

    # MARK: - setUp & tearDown

    @classmethod
    def setUpClass(cls):
        super(SportTestCase, cls).setUpClass()

        operation_id = 'getSports'
        cls.check_operation_id_has_operation_handler(operation_id)
        cls.request_uri_path = cls.get_request_uri_path(operation_id)

    # MARK: - Private methods:

    # TODO: Create SportTestCase with method below for reuse
    def _is_sport_in_db(self, sport_params):
        created_sports = EntitySport.get().filter_by(
            name=sport_params.get('name')
        ).all()

        if len(created_sports) != 1:
            return False

        created_sport = created_sports[0].to_dict()
        self.check_dict1_in_dict2(
            OrderedDict(sport_params), created_sport
        )
        return True
