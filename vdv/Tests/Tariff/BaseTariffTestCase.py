import unittest
from collections import OrderedDict

from gyma.vdv.Tests.Base.BaseTestCase import BaseTestCase

from gyma.vdv.Entities.EntityTariff import EntityTariff

from gyma.vdv.db import DBConnection


class BaseTariffTestCase(BaseTestCase):

    # MARK: - Private methods:

    def _is_tariff_in_db(self, tariff_params):
        created_tariffs = EntityTariff.get().filter_by(
            months=tariff_params.get('months'),
            price=tariff_params.get('price'),
            sale=tariff_params.get('sale'),
        ).all()

        if len(created_tariffs) != 1:
            return False

        created_tariff = created_tariffs[0].to_dict()
        self.check_dict1_in_dict2(
            OrderedDict(tariff_params), created_tariff
        )
        return True

    def _delete_all_tariffs(self):
       with DBConnection() as session:
            session.db.query(EntityTariff).delete()
            session.db.commit()