from sqlalchemy.ext.declarative import declarative_base

from gyma.vdv.Entities.EntityRequest import EntityRequest
from gyma.vdv.Prop.PropBase import PropBase

from gyma.vdv.db import DBConnection


Base = declarative_base()


class PropRequest(PropBase, Base):
    __tablename__ = 'vdv_prop_request'
#    vdvid = relation_ship

    def __init__(self, vdvid, propid, value):
        super().__init__(vdvid, propid, value)

    @classmethod
    def get_object_property(cls, vdvid, propid):
        with DBConnection() as session:
            return [_[1].to_dict() for _ in session.db.query(cls, EntityRequest).
                    filter(cls.vdvid == vdvid).
                    filter(cls.propid == propid).
                    filter(cls.value == EntityRequest.vdvid).all()]
