import datetime
import time

from sqlalchemy import Column, Date, Integer, Sequence
from sqlalchemy.ext.declarative import declarative_base

from vdv.Entities.EntityBase import EntityBase

from vdv.db import DBConnection

Base = declarative_base()

class EntityLike(EntityBase, Base):
    __tablename__ = 'vdv_like'

    vdvid = Column(Integer, Sequence('vdv_seq'), primary_key=True)
    userid = Column(Integer)
    created = Column(Date)
    weight = Column(Integer)

    json_serialize_items_list = ['vdvid', 'userid', 'created', 'weight']

    def __init__(self, userid, weight):
        super().__init__()

        self.userid = userid
        ts = time.time()
        self.created = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M')
        self.weight = weight

    @classmethod
    def add_from_json(cls, data, userId):
        vdvid = None

        if 'weight' in data:
            weight = data['weight']

            new_entity = EntityLike(userId, weight)
            vdvid = new_entity.add()

        return vdvid


    @classmethod
    def update_from_json(cls, data):
        vdvid = None

        if 'id' in data:
            with DBConnection() as session:
                vdvid = data['id']
                entity = session.db.query(EntityLike).filter_by(vdvid=vdvid).all()

                if len(entity):
                    for _ in entity:
                        if 'weight' in data:
                            _.weight = data['weight']

                        session.db.commit()

        return vdvid




