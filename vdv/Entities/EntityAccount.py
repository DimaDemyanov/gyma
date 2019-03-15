from collections import OrderedDict
import time
import datetime

from sqlalchemy import Column, String, Integer, Date, Sequence
from sqlalchemy.ext.declarative import declarative_base

from vdv.Entities.EntityBase import EntityBase
from vdv.Entities.EntityProp import EntityProp
from vdv.Entities.EntityCourt import EntityCourt

from vdv.Prop.PropMedia import PropMedia
from vdv.Prop.PropPost import PropPost

from vdv.db import DBConnection

Base = declarative_base()



class EntityAccount(EntityBase, Base):
    __tablename__ = 'vdv_account'

    vdvid = Column(Integer, Sequence('vdv_seq'), primary_key=True)
    name = Column(String)
    phone = Column(String)
    created = Column(Date)
    updated = Column(Date)
    mediaid = Column(Integer)
    email = Column(String)
    password = Column(String)
    accountType = Column(String)
    # Добавить поля password, is_admin, is_arendo

    json_serialize_items_list = ['vdvid', 'name', 'phone', 'created', 'updated', 'mediaid', 'email', 'password']

    def __init__(self, username, phone, mediaid, email, password):
        super().__init__()

        self.name = username
        self.phone = phone
        self.mediaid = mediaid
        self.email = email
        self.password = password
        self.accountType = ""
        ts = time.time()
        self.created = self.updated = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M')

    @classmethod
    def add_from_json(cls, data):

        vdvid = None

        if 'phone' in data and 'name' in data:
            phone = data['phone']
            username = data['name']
            if 'mediaid' in data:
                mediaid = data['mediaid']
            else:
                mediaid = None
            if 'email' in data:
                email = data['email']
            else:
                email = None
            if 'password' in data:
                password = data['password']
            else:
                password = None

            new_entity = EntityAccount(username, phone, mediaid, email, password)
            vdvid = new_entity.add()

        try:
            with DBConnection() as session:
                session.db.commit()
        except Exception as e:
            EntityAccount.delete(vdvid)
            raise Exception('Internal error')

        return vdvid

    @classmethod
    def update_from_json(cls, data):
        def process_avatar(s, _vdvid, _id, _val):
            PropMedia.delete(_vdvid, _id, False)
            cls.process_media(s, 'image', _vdvid, _vdvid, _id, _val)

        vdvid = None

        if 'vdvid' in data:
            with DBConnection() as session:
                vdvid = data['vdvid']
                entity = session.db.query(EntityAccount).filter_by(vdvid=vdvid).all()
                if len(entity) == 0:
                    vdvid = -1          # No user with given id
                if len(entity):
                    for _ in entity:
                        if 'name' in data:
                            _.name = data['name']

                        if 'mediaid' in data:
                            _.mediaid = data['mediaid']

                        if 'email' in data:
                            _.email = data['email']

                        if 'password' in data:
                            _.password = data['password']

                        session.db.commit()

        return vdvid

    @classmethod
    def get_wide_object(cls, vdvid, items=[]):
        PROPNAME_MAPPING = EntityProp.map_name_id()

        PROP_MAPPING = {
            'private': lambda _vdvid, _id: PropBool.get_object_property(_vdvid, _id),
            'post': lambda _vdvid, _id: PropPost.get_object_property(_vdvid, _id),
            'avatar': lambda _vdvid, _id: PropMedia.get_object_property(_vdvid, _id, ['vdvid', 'url'])
        }

        result = {
            'vdvid': vdvid,
            'court': []
        }

        for key, propid in PROPNAME_MAPPING.items():
            if key in PROP_MAPPING and (not len(items) or key in items):
                result.update({key: PROP_MAPPING[key](vdvid, propid)})

        courts = EntityCourt.get().filter_by(ownerid=vdvid).all()

        for _ in courts:
            result['court'].append(EntityCourt.get_wide_object(_.vdvid))

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
    def get_id_from_phone(cls, phone):
        try:
            return cls.get().filter_by(phone=phone).all()[0].vdvid
        except:
            return None

    @classmethod
    def get_id_from_email(cls, email):
        try:
            return cls.get().filter_by(email=email).all()[0].vdvid
        except:
            return None

    @classmethod
    def get_password_from_email(cls, email):
        try:
            return cls.get().filter_by(email=email).all()[0].password
        except:
            return None

    @classmethod
    def is_private(cls, id):
        PROPNAME_MAPPING = EntityProp.map_name_id()
        res = PropBool.get_object_property(id, PROPNAME_MAPPING['private'])
        return res[0] if len(res) else False