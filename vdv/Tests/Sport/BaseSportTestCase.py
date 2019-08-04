import unittest
from collections import OrderedDict

from gyma.vdv.Tests.Base.BaseTestCase import BaseTestCase

from gyma.vdv.Entities.EntitySport import EntitySport

from gyma.vdv.db import DBConnection


class BaseSportTestCase(BaseTestCase):

    # MARK: - Private methods:

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

    def _delete_created_sports(self):
        with DBConnection() as session:
            session.db.query(EntitySport).delete()
            session.db.commit()
