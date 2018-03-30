from sqlalchemy.ext.declarative import declarative_base

from vdv.Entities.EntityLike import EntityLike
from vdv.Prop.PropBase import PropBase

Base = declarative_base()

from vdv.db import DBConnection

class PropLike(PropBase, Base):
    __tablename__ = 'vdv_prop_like'

    def __init__(self, name, type):
        super().__init__(name, type)

    @classmethod
    def get_object_property(cls, vdvid, propid):
        with DBConnection() as session:
            return [_[1] for _ in session.db.query(cls, EntityLike).
                filter(cls.vdvid == vdvid).
                filter(cls.propid == propid).
                filter(cls.value == EntityLike.vdvid).all()]