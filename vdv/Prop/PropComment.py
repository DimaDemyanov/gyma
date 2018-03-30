from sqlalchemy.ext.declarative import declarative_base

from vdv.Entities.EntityComment import EntityComment
from vdv.Prop.PropBase import PropBase

Base = declarative_base()

from vdv.db import DBConnection

class PropLike(PropBase, Base):
    __tablename__ = 'vdv_prop_comment'

    def __init__(self, vdvid, propid, value):
        super().__init__(vdvid, propid, value)

    @classmethod
    def get_object_property(cls, vdvid, propid):
        with DBConnection() as session:
            return [_[1] for _ in session.db.query(cls, EntityComment).
                filter(cls.vdvid == vdvid).
                filter(cls.propid == propid).
                filter(cls.value == EntityComment.vdvid).all()]