import json
from collections import OrderedDict
import time
import datetime
from sqlalchemy import Column, String, Integer, Date, Sequence, Boolean, cast, DateTime
from sqlalchemy.ext.declarative import declarative_base

from gyma.vdv.Entities.EntityBase import EntityBase
from gyma.vdv.Entities.EntityProp import EntityProp
from gyma.vdv.Entities.EntityCourt import EntityCourt
from gyma.vdv.Entities.EntityRequest import EntityRequest
from gyma.vdv.Entities.EntityTime import EntityTime

from gyma.vdv.Prop.PropMedia import PropMedia
from gyma.vdv.Prop.PropPost import PropPost
from gyma.vdv.Prop.PropRequestTime import PropRequestTime

from gyma.vdv.db import DBConnection


Base = declarative_base()


class EntitySimpleuser(EntityBase, Base):
    __tablename__ = 'vdv_simple_user'

    vdvid = Column(Integer, Sequence('vdv_seq'), primary_key=True)
    accountid = Column(Integer)
    isagreerules = Column(Boolean)

    json_serialize_items_list = ['vdvid', 'accountid', 'isagreerules']

    def __init__(self, accountid, isagreerules):
        super().__init__()
        self.accountid = accountid
        self.isagreerules = isagreerules

    @classmethod
    def add_from_json(cls, data):

        vdvid = None
        if 'accountid' in data:
            accountid = data['accountid']
            new_entity = EntitySimpleuser(accountid, False)
            vdvid = new_entity.add()

        try:
            with DBConnection() as session:
                session.db.commit()
        except Exception as e:
            EntitySimpleuser.delete(vdvid)
            raise Exception('Internal error')

        return vdvid

    @classmethod
    def update_from_json(cls, data):
        vdvid = None

        if 'vdvid' in data:
            with DBConnection() as session:
                vdvid = data['vdvid']
                entity = session.db.query(EntitySimpleuser).filter_by(vdvid=vdvid).all()
                if len(entity) == 0:
                    vdvid = -1          # No user with given id
                if len(entity):
                    for _ in entity:
                        if 'accountid' in data:
                            _.accountid = data['accountid']

                        if 'isAgreeRules' in data:
                            _.isagreerules = data['isAgreeRules']

                        session.db.commit()

        return vdvid

    @classmethod
    def confirm_rules(cls, vdvid):
        with DBConnection() as session:
            entity = session.db.query(EntitySimpleuser).filter_by(vdvid=vdvid).all()
            if len(entity) == 0:
                vdvid = -1  # No user with given id
            if len(entity):
                for _ in entity:
                    _.isagreerules = True

                session.db.commit()

        return vdvid


    @classmethod
    def get_wide_object(cls, vdvid, items=[]):

        PROPNAME_MAPPING = EntityProp.map_name_id()

        simpleuser = EntitySimpleuser.get().filter_by(vdvid=vdvid).all()[0]

        accountid = simpleuser.accountid

        obj_dict = simpleuser.to_dict()

        count_come = 0
        count_not_come = 0

        reqs = EntityRequest.get().filter_by(accountid=accountid, isconfirmed = True, come = True).all()
        for _ in reqs:
            times = PropRequestTime.get_object_property(_.vdvid, PROPNAME_MAPPING['requestTime'])
            count_come += 1 if EntityTime.get().filter(EntityTime.vdvid.in_(times)).count() > 0 else 0

        reqs = EntityRequest.get().filter_by(accountid=accountid, isconfirmed=True, come=False).all()
        for _ in reqs:
            times = PropRequestTime.get_object_property(_.vdvid, PROPNAME_MAPPING['requestTime'])
            count_not_come += 1 if EntityTime.get().filter(EntityTime.vdvid.in_(times)).count() > 0 else 0

        obj_dict.update({'sucsess': count_come, 'notsucsess': count_not_come})

        return obj_dict

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