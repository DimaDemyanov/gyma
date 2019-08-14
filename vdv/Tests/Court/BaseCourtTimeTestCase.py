import sys

from gyma.vdv.Tests.Court.BaseCourtTestCase import BaseCourtTestCase

from gyma.vdv.Entities.EntityTime import EntityTime

from gyma.vdv.Prop.PropCourtTime import PropCourtTime

from gyma.vdv.db import DBConnection


DIR_PATH = sys.path[0]
COURT_PARAMETERS_PATH = '{}/court_with_courtTime_prop.json'.format(sys.path[0])


class BaseCourtTimeTestCase(BaseCourtTestCase):

    # MARK - Private class methods

    @classmethod
    def _delete_created_court_time_reference(cls, court_id, time_id):
        with DBConnection() as session:
            session.db.query(PropCourtTime).filter_by(
                vdvid=court_id, value=time_id
            ).delete()
            session.db.commit()

    @classmethod
    def _delete_created_times(cls):
        with DBConnection() as session:
            session.db.query(EntityTime).delete()
            session.db.commit()

    # MARK - Private methods

    def _get_created_time_id(self, time):
        created_times = EntityTime.get().filter_by(time=time).all()
        if len(created_times) != 1:
            return None
        created_time_id = created_times[0].vdvid
        return created_time_id

    def _is_court_time_in_db(self, court_time):
        created_time_id = self._get_created_time_id(court_time)

        if not created_time_id:
            return False

        court_times = PropCourtTime.get().filter_by(
            vdvid=self.created_court_id, value=created_time_id
        ).all()

        return len(court_times) == 1
