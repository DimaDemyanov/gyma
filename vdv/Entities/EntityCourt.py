from collections import OrderedDict
import datetime
import time

from sqlalchemy import Column, String, Integer, Date, Sequence
from sqlalchemy.ext.declarative import declarative_base

from vdv.Entities.EntityBase import EntityBase
from vdv.Entities.EntityProp import EntityProp

from vdv.Prop.PropBool import PropBool
from vdv.Prop.PropReal import PropReal
from vdv.Prop.PropMedia import PropMedia
from vdv.Prop.PropLike import PropLike
from vdv.Prop.PropLocation import PropLocation
from vdv.Prop.PropRequest import PropRequest
from vdv.db import DBConnection

Base = declarative_base()

class EntityCourt(EntityBase, Base):
    __tablename__ = 'vdv_court'

    vdvid = Column(Integer, Sequence('vdv_seq'), primary_key=True)
    ownerid = Column(Integer)
    name = Column(String)
    desc = Column(String)
    price = Column(Integer)
    created = Column(Date)
    updated = Column(Date)

    json_serialize_items_list = ['vdvid', 'ownerid', 'name', 'desc', 'price', 'created', 'updated']

    def __init__(self, ownerid, name, desc, price):
        super().__init__()

        self.ownerid = ownerid
        self.name = name
        self.desc = desc
        self.price = price

        ts = time.time()
        self.created = self.updated = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M')

    @classmethod
    def add_from_json(cls, data):
        PROPNAME_MAPPING = EntityProp.map_name_id()

        vdvid = None

        PROP_MAPPING = {
            'private':
                lambda session, _vdvid, _id, _value, _uid: PropBool(_vdvid, _id, _value)
                    .add(session=session, no_commit=True),
            'isopen':
                lambda session, _vdvid, _id, _value, _uid: PropBool(_vdvid, _id, _value)
                    .add(session=session, no_commit=True),
            'isfree':
                lambda session, _vdvid, _id, _value, _uid: PropBool(_vdvid, _id, _value)
                    .add(session=session, no_commit=True),
            'isonair':
                lambda session, _vdvid, _id, _value, _uid: PropBool(_vdvid, _id, _value)
                    .add(session=session, no_commit=True),
            'location':
                lambda s, _vdvid, _id, _val, _uid: PropLocation(_vdvid, _id, _val)
                    .add(session=s, no_commit=True),
            'request':
                lambda s, _vdvid, _id, _val, _uid: [PropRequest(_vdvid, _id, _).add(session=s, no_commit=True)
                                                    for _ in _val],
            'media':
                lambda s, _vdvid, _id, _val, _uid: [cls.process_media(s, 'image', _uid, _vdvid, _id, _)
                                                    for _ in _val],
            'equipment':
                lambda s, _vdvid, _id, _val, _uid: [cls.process_media(s, 'equipment', _uid, _vdvid, _id, _)
                                                    for _ in _val]
        }

        if 'ownerid' in data and 'name' in data and 'desc' in data:
            ownerid = data['ownerid']
            name = data['name']
            desc = data['desc']
            if 'price' in data:
                price = data['price']
            else:
                price = -1
            new_entity = EntityCourt(ownerid, name, desc, price)
            vdvid = new_entity.add()

        if 'prop' in data:
            with DBConnection() as session:
                for prop_name, prop_val in data['prop'].items():
                    if prop_name in PROPNAME_MAPPING and prop_name in PROP_MAPPING:
                        PROP_MAPPING[prop_name](session, vdvid, PROPNAME_MAPPING[prop_name], prop_val, ownerid)
                    else:
                        new_entity.delete(vdvid)
                        raise Exception('{%s} not existed property\nPlease use one of:\n%s' %
                                        (prop_name, str(PROPNAME_MAPPING)))

                session.db.commit()

        return vdvid

    @classmethod
    def update_from_json(cls, data):
        def process_avatar(s, _vdvid, _id, _val):
            PropMedia.delete(_vdvid, _id, False)
            cls.process_media(s, 'image', _vdvid, _vdvid, _id, _val)

        PROPNAME_MAPPING = EntityProp.map_name_id()

        vdvid = None

        PROP_MAPPING = {
            'private':
                lambda session, _vdvid, _id, _value, _uid: PropBool(_vdvid, _id, _value)
                    .update(session=session, no_commit=True),
            'isopen':
                lambda session, _vdvid, _id, _value, _uid: PropBool(_vdvid, _id, _value)
                    .update(session=session, no_commit=True),
            'isfree':
                lambda session, _vdvid, _id, _value, _uid: PropBool(_vdvid, _id, _value)
                    .update(session=session, no_commit=True),
            'isonair':
                lambda session, _vdvid, _id, _value, _uid: PropBool(_vdvid, _id, _value)
                    .update(session=session, no_commit=True),
            'location':
                lambda s, _vdvid, _id, _val, _uid: PropLocation(_vdvid, _id, _val)
                    .update(session=s, no_commit=True),
            'request':
                lambda s, _vdvid, _id, _val, _uid: [PropRequest(_vdvid, _id, _).update(session=s, no_commit=True)
                                                    for _ in _val],
            'media':
                lambda s, _vdvid, _id, _val, _uid: [cls.process_media(s, 'image', _uid, _vdvid, _id, _)
                                                    for _ in _val],
            'equipment':
                lambda s, _vdvid, _id, _val, _uid: [cls.process_media(s, 'equipment', _uid, _vdvid, _id, _)
                                                    for _ in _val]
        }

        if 'id' in data:
            with DBConnection() as session:
                vdvid = data['id']
                entity = session.db.query(EntityCourt).filter_by(vdvid=vdvid).all()
                if len(entity) == 0:
                    vdvid = -1  # No user with givven id
                if len(entity):
                    for _ in entity:
                        if 'ownerid' in data:
                            _.ownerid = data['ownerid']

                        if 'name' in data:
                            _.name = data['name']

                        if 'desc' in data:
                            _.desc = data['desc']

                        if 'price' in data:
                            _.price = data['price']

                        if 'prop' in data:
                            for prop_name, prop_val in data['prop'].items():
                                if prop_name in PROPNAME_MAPPING and prop_name in PROP_MAPPING:
                                    PROP_MAPPING[prop_name](session, vdvid, PROPNAME_MAPPING[prop_name], prop_val)

                        session.db.commit()

        return vdvid

    @classmethod
    def get_wide_object(cls, vdvid, items=[]):
        PROPNAME_MAPPING = EntityProp.map_name_id()

        PROP_MAPPING = {
            'private':   lambda _vdvid, _id: PropBool.get_object_property(_vdvid, _id),
            'isopen':    lambda _vdvid, _id: PropBool.get_object_property(_vdvid, _id),
            'isfree':    lambda _vdvid, _id: PropBool.get_object_property(_vdvid, _id),
            'isonair':   lambda _vdvid, _id: PropBool.get_object_property(_vdvid, _id),
            'price':     lambda _vdvid, _id: PropReal.get_object_property(_vdvid, _id),
            'location':  lambda _vdvid, _id: PropLocation.get_object_property(_vdvid, _id),
            'request': lambda _vdvid, _id: PropLocation.get_object_property(_vdvid, _id),
            'media':     lambda _vdvid, _id: PropMedia.get_object_property(_vdvid, _id),
            'equipment': lambda _vdvid, _id: PropMedia.get_object_property(_vdvid, _id),
            'like':      lambda _vdvid, _id: PropLike.get_object_property(_vdvid, _id)
        }

        result = {
            'vdvid': vdvid
        }
        for key, propid in PROPNAME_MAPPING.items():
            if key in PROP_MAPPING and (not len(items) or key in items):
                result.update({key: PROP_MAPPING[key](vdvid, propid)})

        return result

    @classmethod
    def delete_wide_object(cls, vdvid):
        PROPNAME_MAPPING = EntityProp.map_name_id()

        PROP_MAPPING = {
            'private':   lambda _vdvid, _id: PropBool.delete(_vdvid, _id, False),
            'isopen':    lambda _vdvid, _id: PropBool.delete(_vdvid, _id, False),
            'isfree':    lambda _vdvid, _id: PropBool.delete(_vdvid, _id, False),
            'isonair':   lambda _vdvid, _id: PropBool.delete(_vdvid, _id, False),
            'price':     lambda _vdvid, _id: PropReal.delete(_vdvid, _id, False),
            'location':  lambda _vdvid, _id: PropLocation.delete(_vdvid, _id, False),
            'request': lambda _vdvid, _id: PropRequest.delete(_vdvid, _id, False),
            'media':     lambda _vdvid, _id: PropMedia.delete(_vdvid, _id, False),
            'equipment': lambda _vdvid, _id: PropMedia.delete(_vdvid, _id, False)
        }

        for key, propid in PROPNAME_MAPPING.items():
            if key in PROP_MAPPING:
                PROP_MAPPING[key](vdvid, propid)