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
from vdv.Prop.PropLocation import PropLocation
from vdv.db import DBConnection

Base = declarative_base()

class EntityCourt(EntityBase, Base):
    __tablename__ = 'vdv_court'

    vdvid = Column(Integer, Sequence('vdv_seq'), primary_key=True)
    name = Column(String)
    desc = Column(String)
    created = Column(Date)
    updated = Column(Date)

    json_serialize_items_list = ['vdvid', 'name', 'desc', 'created', 'updated']

    def __init__(self, name, desc):
        super().__init__()

        self.name = name
        self.desc = desc

        ts = time.time()
        self.created = self.updated = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M')

    @classmethod
    def add_from_json(cls, data):
        PROPNAME_MAPPING = EntityProp.map_name_id()

        vdvid = None

        PROP_MAPPING = {
            'private':
                lambda session, _vdvid, _id, _value: PropBool(_vdvid, _id, _value).add(session=session, no_commit=True),
            'isopen':
                lambda session, _vdvid, _id, _value: PropBool(_vdvid, _id, _value).add(session=session, no_commit=True),
            'isfree':
                lambda session, _vdvid, _id, _value: PropBool(_vdvid, _id, _value).add(session=session, no_commit=True),
            'isonair':
                lambda session, _vdvid, _id, _value: PropBool(_vdvid, _id, _value).add(session=session, no_commit=True),
            'price':
                lambda session, _vdvid, _id, _value: PropReal(_vdvid, _id, _value).add(session=session, no_commit=True),
            'location':
                lambda s, _vdvid, _id, _val: PropLocation(_vdvid, _id, _val).add(session=s, no_commit=True),
            'media':
                lambda s, _vdvid, _id, _val : [PropMedia(_vdvid, _id, _).add(session=s, no_commit=True) for _ in _val]
        }

        if 'name' in data and 'desc' in data and 'prop' in data :
            name = data['name']
            desc = data['desc']


            new_entity = EntityCourt(name, desc)
            vdvid = new_entity.add()

            with DBConnection() as session:
                for prop in data['prop']:
                    prop_name = prop['name']
                    prop_val = prop['value']
                    if prop_name in PROPNAME_MAPPING and prop_name in PROP_MAPPING:
                        PROP_MAPPING[prop_name](session, vdvid, PROPNAME_MAPPING[prop_name], prop_val)
                    else:
                        new_entity.delete(vdvid)
                        raise Exception('{%s} not existed property\nPlease use one of:\n%s' %
                                        (prop_name, str(PROPNAME_MAPPING)))

                session.db.commit()

        return vdvid

    @classmethod
    def get_wide_object(cls, vdvid):
        PROPNAME_MAPPING = EntityProp.map_name_id()

        PROP_MAPPING = {
            'private':  lambda _vdvid, _id: PropBool.get_object_property(_vdvid, _id),
            'isopen':   lambda _vdvid, _id: PropBool.get_object_property(_vdvid, _id),
            'isfree':   lambda _vdvid, _id: PropBool.get_object_property(_vdvid, _id),
            'isonair':  lambda _vdvid, _id: PropBool.get_object_property(_vdvid, _id),
            'price':    lambda _vdvid, _id: PropReal.get_object_property(_vdvid, _id),
            'location': lambda _vdvid, _id: PropLocation.get_object_property(_vdvid, _id),
            'media':    lambda _vdvid, _id: PropMedia.get_object_property(_vdvid, _id)
        }


        result = []
        for key, propid in PROPNAME_MAPPING.items():
            if key in PROP_MAPPING:
                result.append(OrderedDict([('name', key), ('value', PROP_MAPPING[key](vdvid, propid))]))

        return result

    @classmethod
    def delete_wide_object(cls, vdvid):
        PROPNAME_MAPPING = EntityProp.map_name_id()

        PROP_MAPPING = {
            'private':  lambda _vdvid, _id: PropBool.delete(_vdvid, _id, False),
            'isopen':   lambda _vdvid, _id: PropBool.delete(_vdvid, _id, False),
            'isfree':   lambda _vdvid, _id: PropBool.delete(_vdvid, _id, False),
            'isonair':  lambda _vdvid, _id: PropBool.delete(_vdvid, _id, False),
            'price':    lambda _vdvid, _id: PropReal.delete(_vdvid, _id, False),
            'location': lambda _vdvid, _id: PropLocation.delete(_vdvid, _id, False),
            'media':    lambda _vdvid, _id: PropMedia.delete(_vdvid, _id, False)
        }

        for key, propid in PROPNAME_MAPPING.items():
            if key in PROP_MAPPING:
                PROP_MAPPING[key](vdvid, propid)