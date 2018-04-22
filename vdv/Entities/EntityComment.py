import datetime
import time

from sqlalchemy import Column, String, Integer, Date, Sequence
from sqlalchemy.ext.declarative import declarative_base

from vdv.Entities.EntityProp import EntityBase
from vdv.Entities.EntityProp import EntityProp

from vdv.db import DBConnection

Base = declarative_base()

class EntityComment(EntityBase, Base):
    __tablename__ = 'vdv_comment'


    vdvid = Column(Integer, Sequence('vdv_seq'), primary_key=True)
    userid = Column(Integer)
    text = Column(String)
    created = Column(Date)
    updated = Column(Date)

    json_serialize_items_list = ['vdvid', 'userid', 'text', 'created', 'updated']

    def __init__(self, userid, text):
        super().__init__()

        self.userid = userid
        self.text = text

        ts = time.time()
        self.created = self.updated = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M')

    @classmethod
    def add_from_json(cls, data, userId):
        PROPNAME_MAPPING = EntityProp.map_name_id()

        if 'text' in data and 'vdvid' in data:
            text = data['text']
            vdvid = data['vdvid']

            new_entity = EntityComment(userId, text)
            id = new_entity.add()

            from vdv.Prop.PropComment import PropComment
            PropComment(vdvid, PROPNAME_MAPPING["comment"], id).add()

        return id

    @classmethod
    def update_from_json(cls, data):
        vdvid = None

        if 'id' in data:
            with DBConnection() as session:
                vdvid = data['id']
                entity = session.db.query(EntityComment).filter_by(vdvid=vdvid).all()

                if len(entity):
                    for _ in entity:
                        if 'text' in data:
                            _.text = data['text']

                        session.db.commit()

        return vdvid
