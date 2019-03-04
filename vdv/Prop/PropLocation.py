from sqlalchemy.ext.declarative import declarative_base

from vdv.Entities.EntityLocation import EntityLocation
from vdv.Prop.PropBase import PropBase

Base = declarative_base()

from vdv.db import DBConnection

class PropLocation(PropBase, Base):
    __tablename__ = 'vdv_prop_location'

    def __init__(self, vdvid, propid, value):
        super().__init__(vdvid, propid, value)

    # @classmethod
    # def get_object_property(cls, vdvid, propid):
    #     with DBConnection() as session:
    #         return [_[1].to_dict() for _ in session.db.query(cls, EntityLocation).
    #             filter(cls.vdvid == vdvid).
    #             filter(cls.propid == propid).
    #             filter(cls.value == EntityLocation.vdvid).all()]

    @classmethod
    def get_object_in_area(cls, propid, p, r):
        with DBConnection() as session:
            return [_[0] for _ in session.db.query(cls, EntityLocation)
                .filter(cls.propid == propid)
                .filter(EntityLocation.longitude.between(p[1] - r, p[1] + r))
                .filter(EntityLocation.latitude.between(p[0] - r, p[0] + r))
                .filter(cls.value == EntityLocation.vdvid)
                .all()]