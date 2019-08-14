from gyma.vdv.Tests.Base.BaseTestCase import BaseTestCase

from gyma.vdv.Entities.EntityLandlord import EntityLandlord

from gyma.vdv.db import DBConnection


class BaseLandlordTestCase(BaseTestCase):

    # MARK: - Private methods

    def _get_property_isAgreeRules(self, landlord_params):
        with DBConnection() as session:
            isAgreeRulesList = session.db.query(EntityLandlord.isagreerules).\
                filter_by(accountid=landlord_params['accountid']).all()

        if len(isAgreeRulesList) != 1:
            return None

        return isAgreeRulesList[0][0]

    def _delete_created_landlords(self):
        with DBConnection() as session:
            session.db.query(EntityLandlord).delete()
            session.db.commit()
