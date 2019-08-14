from collections import OrderedDict

from gyma.vdv.Tests.Base.BaseTestCase import BaseTestCase
from gyma.vdv.Tests.Base.test_helpers import (
    convert_dict_bool_str_values_to_bool
)

from gyma.vdv.Entities.EntityLocation import EntityLocation

from gyma.vdv.db import DBConnection


class BaseLocationTestCase(BaseTestCase):

    # MARK: - Public methods:

    def check_dict1_in_dict2(self, dict1, dict2):
        convert_dict_bool_str_values_to_bool(dict1)
        convert_dict_bool_str_values_to_bool(dict2)

        for dict1_key, dict1_value in dict1.items():
            if dict1_key == 'vdvid':
                continue
            try:
                dict1_value = round(float(dict1_value), 4)
            except ValueError:
                continue
            dict2_value = dict2[dict1_key]
            if isinstance(dict1_value, dict):
                self.check_dict1_in_dict2(dict2_value, dict1_value)
            else:
                self.assertEqual(dict2_value, dict1_value)

    # MARK: - Private methods:

    def _is_location_in_db(self, location_params):
        created_locations = EntityLocation.get().filter_by(
            name=location_params.get('name')
        ).all()

        if len(created_locations) != 1:
            return False

        created_sport = created_locations[0].to_dict()
        self.check_dict1_in_dict2(
            OrderedDict(location_params), created_sport
        )
        return True

    def _delete_created_locations(self):
        with DBConnection() as session:
            session.db.query(EntityLocation).delete()
            session.db.commit()
