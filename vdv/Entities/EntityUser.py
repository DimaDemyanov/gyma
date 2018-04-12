from collections import OrderedDict
import time
import datetime

from sqlalchemy import Column, String, Integer, Date, Sequence, Boolean
from sqlalchemy.ext.declarative import declarative_base

from vdv.Entities.EntityBase import EntityBase
from vdv.Entities.EntityProp import EntityProp

from vdv.Prop.PropBool import PropBool
from vdv.Prop.PropMedia import PropMedia
from vdv.Prop.PropPost import PropPost
from vdv.Prop.PropLocation import PropLocation

from vdv.db import DBConnection

Base = declarative_base()

class EntityUser(EntityBase, Base):
    __tablename__ = 'vdv_user'

    vdvid = Column(Integer, Sequence('vdv_seq'), primary_key=True)
    username = Column(String)
    e_mail = Column(String)
    created = Column(Date)
    updated = Column(Date)

    json_serialize_items_list = ['vdvid', 'username', 'e_mail', 'created', 'updated']

    def __init__(self, username, email):
        super().__init__()

        self.username = username
        self.e_mail = email

        ts = time.time()
        self.created = self.updated = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M')

    @classmethod
    def add_from_json(cls, data):
        PROPNAME_MAPPING = EntityProp.map_name_id()

        vdvid = None

        PROP_MAPPING = {
            'private':
                lambda session, _vdvid, _id, _value: PropBool(_vdvid, _id, _value).add(session=session, no_commit=True),
            'post':
                lambda s, _vdvid, _id, _val: [PropPost(_vdvid, _id, _).add(session=s, no_commit=True) for _ in _val],
            'avatar':
                lambda s, _vdvid, _id, _val: PropMedia(_vdvid, _id, _val).add(session=s, no_commit=True)
        }

        if 'username' in data and 'e_mail' in data and 'prop' in data:
            username = data['username']
            e_mail = data['e_mail']

            new_entity = EntityUser(username, e_mail)
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
            'private': lambda _vdvid, _id: PropBool.get_object_property(_vdvid, _id),
            'post': lambda _vdvid, _id: PropPost.get_object_property(_vdvid, _id),
            'avatar': lambda _vdvid, _id: PropMedia.get_object_property(_vdvid, _id)
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
            'private': lambda _vdvid, _id: PropBool.delete(_vdvid, _id, False),
            'post': lambda _vdvid, _id: PropPost.delete(_vdvid, _id, False),
            'avatar': lambda _vdvid, _id: PropMedia.delete(_vdvid, _id, False)
        }

        for key, propid in PROPNAME_MAPPING.items():
            if key in PROP_MAPPING:
                PROP_MAPPING[key](vdvid, propid)

    @classmethod
    def get_id_from_username(cls, username):
        try:
            return cls.get().filter_by(username=username).all()[0].vdvid
        except:
            return None

    @classmethod
    def get_id_from_email(cls, e_mail):
        try:
            return cls.get().filter_by(e_mail=e_mail).all()[0].vdvid
        except:
            return None

