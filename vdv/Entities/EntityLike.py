import datetime
import time

from sqlalchemy import Column, Date, Integer, Sequence
from sqlalchemy.ext.declarative import declarative_base

from vdv.Entities.EntityBase import EntityBase
from vdv.Entities.EntityProp import EntityProp

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
        PROPNAME_MAPPING = EntityProp.map_name_id()

        _id = None
        if 'weight' in data and 'vdvid' in data:
            weight = data['weight']
            vdvid = data['vdvid']

            from vdv.Prop.PropLike import PropLike
            likes = PropLike.get_post_user_related(vdvid, PROPNAME_MAPPING['like'], userId)


            if len(likes):
                for _ in likes:
                    EntityLike.delete(_['vdvid'])
                    PropLike.delete_value(_['vdvid'], raise_exception=False)

            new_entity = EntityLike(userId, weight)
            _id = new_entity.add()

            PropLike(vdvid, PROPNAME_MAPPING['like'], _id).add()

        return _id


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




