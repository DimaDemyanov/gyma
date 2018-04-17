from sqlalchemy.ext.declarative import declarative_base

from vdv.Entities.EntityPost import EntityPost
from vdv.Prop.PropBase import PropBase

Base = declarative_base()

from vdv.db import DBConnection

class PropPost(PropBase, Base):
    __tablename__ = 'vdv_prop_post'

    def __init__(self, vdvid, propid, value):
        super().__init__(vdvid, propid, value)

    @classmethod
    def get_object_property(cls, vdvid, propid, items=[]):
        with DBConnection() as session:
            res = []
            for _ in session.db.query(cls, EntityPost).\
                filter(cls.vdvid == vdvid).\
                filter(cls.propid == propid).\
                filter(cls.value == EntityPost.vdvid).all():

                obj_dict = _[1].to_dict(['vdvid', 'description'])
                obj_dict.update(EntityPost.get_wide_object(_[1].vdvid, items))
                res.append(obj_dict)

            return res