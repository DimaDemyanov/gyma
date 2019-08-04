import unittest
from collections import OrderedDict

from gyma.vdv.Tests.Base.BaseTestCase import BaseTestCase

from gyma.vdv.Entities.EntityEquipment import EntityEquipment


class BaseEquipmentTestCase(BaseTestCase):

    # MARK: - Private methods:

    def _is_equipment_in_db(self, equipment_params):
        created_equipments = EntityEquipment.get().filter_by(
            name=equipment_params.get('name')
        ).all()

        if len(created_equipments) != 1:
            return False

        created_equipment = created_equipments[0].to_dict()
        self.check_dict1_in_dict2(
            OrderedDict(equipment_params), created_equipment
        )
        return True
