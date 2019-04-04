from sqlalchemy.ext.declarative import declarative_base

from gyma.vdv.Entities.EntityLike import EntityLike
from gyma.vdv.Prop.PropBase import PropBase

from gyma.vdv.db import DBConnection


Base = declarative_base()


class PropLike(PropBase, Base):
    __tablename__ = 'vdv_prop_like'

    def __init__(self, vdvid, propid, value):
        super().__init__(vdvid, propid, value)

    @classmethod
    def get_object_property(cls, vdvid, propid):
        with DBConnection() as session:
            return [_[1].to_dict() for _ in session.db.query(cls, EntityLike).
                    filter(cls.vdvid == vdvid).
                    filter(cls.propid == propid).
                    filter(cls.value == EntityLike.vdvid).all()]

    @classmethod
    def get_post_user_related(cls, vdvid, propid, userid):
        with DBConnection() as session:
            return [_[1].to_dict() for _ in session.db.query(cls, EntityLike).
                    filter(cls.vdvid == vdvid).
                    filter(cls.propid == propid).
                    filter(cls.value == EntityLike.vdvid).
                    filter(EntityLike.userid == userid).
                    all()]
