from sqlalchemy.ext.declarative import declarative_base

from vdv.Entities.Like import Like
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
            return [(_[0].propid, _[1]) for _ in session.db.query(cls, Like).
                filter(cls.vdvid == vdvid).
                filter(cls.propid == propid).
                filter(cls.value == Like.vdvid).all()]