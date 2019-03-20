import json
from collections import OrderedDict
import time
import datetime
from sqlalchemy import Column, String, Integer, Date, Sequence, Boolean, cast, DateTime
from sqlalchemy.ext.declarative import declarative_base

from vdv.Entities.EntityBase import EntityBase
from vdv.Entities.EntityProp import EntityProp
from vdv.Entities.EntityTime import EntityTime

from vdv.Prop.PropMedia import PropMedia
from vdv.Prop.PropPost import PropPost
from vdv.Prop.PropRequestTime import PropRequestTime

from vdv.db import DBConnection

Base = declarative_base()



class EntityLandlord(EntityBase, Base):
    __tablename__ = 'vdv_landlord'

    vdvid = Column(Integer, Sequence('vdv_seq'), primary_key=True)
    accountid = Column(Integer)
    money = Column(Integer)
    isentity = Column(Boolean)
    company = Column(String)
    isagreerules = Column(Boolean)
    # Добавить поля password, is_admin, is_arendo

    json_serialize_items_list = ['vdvid', 'accountid', 'money', 'isentity', 'company', 'isagreerules']

    def __init__(self, accountid, money, isentity, company, isAgreeRules):
        super().__init__()
        self.accountid = accountid
        self.money = money
        self.isentity = isentity
        self.company = company
        self.isagreerules = isAgreeRules

    @classmethod
    def add_from_json(cls, data):

        vdvid = None
        if 'accountid' in data and 'money' in data and 'isentity' in data:
            accountid = data['accountid']
            money = data['money']
            isentity = data['isentity']
            company = None
            if 'company' in data:
                company = data['company']
            new_entity = EntityLandlord(accountid, money, isentity, company, False)
            vdvid = new_entity.add()
            from vdv.Entities.EntityAccount import EntityAccount
            account = EntityAccount.get().filter_by(vdvid=accountid).all()[0]
            account.accounttype = str(account.accounttype) + "/landlord"
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

        if 'vdvid' in data:
            with DBConnection() as session:
                vdvid = data['vdvid']
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
    def confirm_rules(cls, vdvid):
        with DBConnection() as session:
            entity = session.db.query(EntityLandlord).filter_by(vdvid=vdvid).all()
            if len(entity) == 0:
                vdvid = -1  # No user with given id
            if len(entity):
                for _ in entity:
                    _.isagreerules = True

                session.db.commit()

        return vdvid

    @classmethod
    def get_wide_object(cls, vdvid, items=[]):

        landlord = EntityLandlord.get().filter_by(vdvid=vdvid).all()[0]

        PROPNAME_MAPPING = EntityProp.map_name_id()

        accountid = landlord.accountid

        obj_dict = landlord.to_dict()

        count_come = 0
        count_not_come = 0

        from vdv.Entities.EntityCourt import EntityCourt
        courts = EntityCourt.get().filter_by(ownerid=vdvid).all()

        for c in courts:
            from vdv.Entities.EntityRequest import EntityRequest
            reqs = EntityRequest.get().filter_by(courtid=c.vdvid, isconfirmed=True, come=True).all()
            for _ in reqs:
                times = PropRequestTime.get_object_property(_.vdvid, PROPNAME_MAPPING['requestTime'])
                count_come += 1 if EntityTime.get().filter(EntityTime.vdvid.in_(times)).count() > 0 else 0

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