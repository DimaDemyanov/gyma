from collections import OrderedDict

from sqlalchemy import Column, Boolean, Integer

from vdv.db import DBConnection

class PropBase:
    vdvid = Column(Integer, primary_key=True)
    propid = Column(Integer, primary_key=True)
    value = Column(Boolean)

    def to_dict(self):
        res = OrderedDict([(key, self.__dict__[key]) for key in ['vdvid', 'propid', 'value']])
        return res

    def __init__(self, vdvid, propid, value):
        self.vdvid = vdvid
        self.propid = propid
        self.value = value

    def add(self):
        with DBConnection() as session:
            session.db.add(self)
            session.db.commit()
            return self.vdvid, self.propid

    @classmethod
    def delete(cls, vdvid, propid):
        with DBConnection() as session:
            res = session.db.query(cls).filter_by(vdvid=vdvid, propid=propid).all()

            if len(res):
                [session.db.delete(_) for _ in res]
                session.db.commit()
            else:
                raise FileNotFoundError('(vdvid, propid) was not found')

    @classmethod
    def get(cls):
        with DBConnection() as session:
            return session.db.query(cls)

    @classmethod
    def get_object_property(cls, vdvid, propid):
        with DBConnection() as session:
            return [_.value for _ in session.db.query(cls).filter_by(vdvid=vdvid, propid=propid).all()]
