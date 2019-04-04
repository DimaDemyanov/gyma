from sqlalchemy.ext.declarative import declarative_base

from gyma.vdv.Entities.EntityMedia import EntityMedia
from gyma.vdv.Prop.PropBase import PropBase

from gyma.vdv.db import DBConnection


Base = declarative_base()


class PropMedia(PropBase, Base):
    __tablename__ = 'vdv_prop_media'

    def __init__(self, vdvid, propid, value):
        super().__init__(vdvid, propid, value)

    # @classmethod
    # def get_object_property(cls, vdvid, propid, items=[]):
    #     with DBConnection() as session:
    #         return [_[1].to_dict(items) for _ in session.db.query(cls, EntityMedia).
    #             filter(cls.vdvid == vdvid).
    #             filter(cls.propid == propid).
    #             filter(cls.value == EntityMedia.vdvid).all()]
