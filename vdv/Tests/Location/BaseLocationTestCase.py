from gyma.vdv.Tests.Base.BaseTestCase import BaseTestCase
from gyma.vdv.Tests.Base.test_helpers import (
    convert_dict_bool_str_values_to_bool
)


class BaseLocationTestCase(BaseTestCase):

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
            if type(dict1_value) is dict:
                self.check_dict1_in_dict2(dict2_value, dict1_value)
            else:
                self.assertEqual(dict2_value, dict1_value)
