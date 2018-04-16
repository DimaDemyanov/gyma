import time
import datetime

from sqlalchemy import Column, Boolean, Integer, Date, Sequence
from sqlalchemy.ext.declarative import declarative_base

from vdv.db import DBConnection

from vdv.Entities.EntityBase import EntityBase

Base = declarative_base()

class EntityFollow(EntityBase, Base):
    __tablename__ = 'vdv_follow'

    vdvid = Column(Integer, primary_key=True)
    followingid = Column(Integer, primary_key=True)
    permit = Column(Integer)
    is_user = Column(Boolean)
    created = Column(Date)

    json_serialize_items_list = ['vdvid', 'followingid', 'permit', 'is_user', 'created']

    def __init__(self, vdvid, followingid, permit, is_user):
        super().__init__()

        self.vdvid = vdvid
        self.followingid = followingid
        self.permit = permit
        self.is_user = is_user

        ts = time.time()
        self.created = self.updated = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M')

    @classmethod
    def smart_delete(cls, vdvid, followingid):
        with DBConnection() as session:
            res = session.db.query(cls).filter_by(vdvid=vdvid, followingid=followingid).all()

            if len(res):
                [session.db.delete(_) for _ in res]
                session.db.commit()
            else:
                raise FileNotFoundError('%s was not found' % cls.__name__)

    @classmethod
    def update(cls, vdvid, followingid, permit):
        with DBConnection() as session:
            res = session.db.query(cls).filter_by(vdvid=vdvid, followingid=followingid).all()

            if len(res):
                for _ in res:
                    _.permit = permit
                session.db.commit()
            else:
                raise FileNotFoundError('%s was not found' % cls.__name__)
