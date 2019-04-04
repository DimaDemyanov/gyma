import datetime
import os
import time

from sqlalchemy import Column, String, Integer, Date, Sequence
from sqlalchemy.ext.declarative import declarative_base

from gyma.vdv.Entities.EntityBase import EntityBase

from gyma.vdv.db import DBConnection


Base = declarative_base()


class EntityMedia(EntityBase, Base):
    __tablename__ = 'vdv_media'

    vdvid = Column(Integer, Sequence('vdv_seq'), primary_key=True)
    ownerid = Column(Integer)
    name = Column(String)
    desc = Column(String)
    type    = Column(String)
    url     = Column(Integer)
    created = Column(Date)

    json_serialize_items_list = ['vdvid', 'ownerid', 'name', 'desc', 'type', 'url', 'created']

    def __init__(self, ownerid, type, url, name='', desc=''):
        super().__init__()

        self.ownerid = ownerid
        self.name = name
        self.desc = desc
        self.type = type
        self.url = url

        ts = time.time()
        self.created = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M')

    @classmethod
    def delete(cls, vdvid):
        def safe_delete(item):
            os.remove(item.url)
            session.db.delete(item)

        with DBConnection() as session:
            res = session.db.query(cls).filter_by(vdvid=vdvid).all()

            if len(res) == 1:
                [safe_delete(_) for _ in res]
                session.db.commit()
            else:
                raise FileNotFoundError('%s was not found' % cls.__name__)
