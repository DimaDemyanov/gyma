from gyma.vdv.Tests.Base.BaseTestCase import BaseTestCase

from gyma.vdv.Entities.EntitySimpleuser import EntitySimpleuser

from gyma.vdv.db import DBConnection


class BaseSimpleuserTestCase(BaseTestCase):

    # MARK: - Private methods

    def _get_property_isAgreeRules(self, simpleuser_params):
        with DBConnection() as session:
            isAgreeRulesList = session.db.query(EntitySimpleuser.isagreerules).\
                filter_by(accountid=simpleuser_params['accountid']).all()

        if len(isAgreeRulesList) != 1:
            return None

        return isAgreeRulesList[0][0]
