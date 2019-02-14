import json
from collections import OrderedDict
import time
import datetime
from sqlalchemy import Column, String, Integer, Date, Sequence, Boolean
from sqlalchemy.ext.declarative import declarative_base

from vdv.Entities.EntityBase import EntityBase
from vdv.Entities.EntityProp import EntityProp
from vdv.Entities.EntityCourt import EntityCourt

from vdv.Prop.PropMedia import PropMedia
from vdv.Prop.PropPost import PropPost

from vdv.db import DBConnection

Base = declarative_base()



class EntityLandlord(EntityBase, Base):
    __tablename__ = 'vdv_landlord'

    vdvid = Column(Integer, Sequence('vdv_seq'), primary_key=True)
    accountid = Column(Integer)
    money = Column(Integer)
    isentity = Column(Boolean)
    company = Column(String)
    # Добавить поля password, is_admin, is_arendo

    json_serialize_items_list = ['vdvid', 'accountid', 'money', 'isentity', 'company']

    def __init__(self, accountid, money, isentity, company):
        super().__init__()
        self.accountid = accountid
        self.money = money
        self.isentity = isentity
        self.company = company

    @classmethod
    def add_from_json(cls, data):

        vdvid = None
        if 'accountid' in data and 'money' and 'isentity' in data:
            accountid = data['accountid']
            money = data['money']
            isentity = data['isentity']
            if 'company' in data:
                company = data['company']
            new_entity = EntityLandlord(accountid, money, isentity, company)
            vdvid = new_entity.add()

        try:
            with DBConnection() as session:
                session.db.commit()
        except Exception as e:
            EntityLandlord.delete(vdvid)
            raise Exception('Internal error')

        return vdvid

    @classmethod
    def update_from_json(cls, data):
        vdvid = None

        if 'id' in data:
            with DBConnection() as session:
                vdvid = data['id']
                entity = session.db.query(EntityLandlord).filter_by(vdvid=vdvid).all()
                if len(entity) == 0:
                    vdvid = -1          # No user with given id
                if len(entity):
                    for _ in entity:
                        if 'accountid' in data:
                            _.accountid = data['accountid']

                        if 'money' in data:
                            _.money = data['money']

                        if 'isentity' in data:
                            _.isentity = data['isentity']

                        if 'company' in data:
                            _.company = data['company']

                        session.db.commit()

        return vdvid

    @classmethod
    def get_wide_object(cls, vdvid, items=[]):
        # PROPNAME_MAPPING = EntityProp.map_name_id()
        #
        # PROP_MAPPING = {
        #     'private': lambda _vdvid, _id: PropBool.get_object_property(_vdvid, _id),
        #     'post': lambda _vdvid, _id: PropPost.get_object_property(_vdvid, _id),
        #     'avatar': lambda _vdvid, _id: PropMedia.get_object_property(_vdvid, _id, ['vdvid', 'url'])
        # }

        landlord = EntityLandlord.get().filter_by(vdvid=vdvid).all()[0]

        # for key, propid in PROPNAME_MAPPING.items():
        #     if key in PROP_MAPPING and (not len(items) or key in items):
        #         result.update({key: PROP_MAPPING[key](vdvid, propid)})

        # courts = EntityCourt.get().filter_by(ownerid=vdvid).all()

        # for _ in courts:
        #     result['court'].append(EntityCourt.get_wide_object(_.vdvid))

        return landlord.to_dict()

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
    def get_id_from_accountid(cls, accountid):
        try:
            return cls.get().filter_by(accountid=accountid).all()[0].vdvid
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