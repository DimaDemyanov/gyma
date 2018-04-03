import datetime
import os
import time

from sqlalchemy import Column, String, Integer, Date, Sequence
from sqlalchemy.ext.declarative import declarative_base

from vdv.Entities.EntityBase import EntityBase
from vdv.db import DBConnection

Base = declarative_base()

class EntityMedia(EntityBase, Base):
    __tablename__ = 'vdv_media'

    vdvid = Column(Integer, Sequence('vdv_seq'), primary_key=True)
    ownerid = Column(Integer)
    type    = Column(String)
    url     = Column(Integer)
    created = Column(Date)

    json_serialize_items_list = ['vdvid', 'ownerid', 'type', 'url', 'created']

    def __init__(self, ownerid, type, url):
        super().__init__()

        self.ownerid = ownerid
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