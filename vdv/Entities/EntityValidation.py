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



class EntityValidation(EntityBase, Base):
    __tablename__ = 'vdv_validation'

    vdvid = Column(Integer, Sequence('vdv_seq'), primary_key=True)
    accountid = Column(Integer)
    code = Column(Integer)
    time_send = Column(Date)
    times_a_day = Column(Integer)

    #json_serialize_items_list = ['vdvid', 'name', 'phone', 'created', 'updated', 'mediaid', 'e_mail', 'password']

    def __init__(self, accountid, code, times_a_day):
        super().__init__()

        self.accountid = accountid
        self.code = code
        ts = time.time()
        self.time_send = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M')
        self.times_a_day = times_a_day

    @classmethod
    def create(cls, data):

        vdvid = None

        new_entity = EntityValidation(data['accountid'], data['code'], data['times_a_day'])
        vdvid = new_entity.add()

        #if 'prop' in data:
        try:
            with DBConnection() as session:
                session.db.commit()
        except Exception as e:
            EntityValidation.delete(vdvid)
            raise Exception('Internal error')

        return vdvid

    @classmethod
    def update(cls, data):

        vdvid = None

        if 'vdvid' in data:
            with DBConnection() as session:
                vdvid = data['vdvid']
                entity = session.db.query(EntityValidation).filter_by(vdvid=vdvid).all()
                if len(entity) == 0:
                    vdvid = -1          # No user with givven id
                if len(entity):
                    for _ in entity:
                        if 'code' in data:
                            _.code = data['code']

                        if 'times_a_day' in data:
                            _.times_a_day = data['times_a_day']

                        if 'time_send' in data:
                            _.data_send = data['time_send']

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
    def get_id_from_email(cls, e_mail):
        try:
            return cls.get().filter_by(e_mail=e_mail).all()[0].vdvid
        except:
            return None

    @classmethod
    def get_password_from_email(cls, e_mail):
        try:
            return cls.get().filter_by(e_mail=e_mail).all()[0].password
        except:
            return None

    @classmethod
    def is_private(cls, id):
        PROPNAME_MAPPING = EntityProp.map_name_id()
        res = PropBool.get_object_property(id, PROPNAME_MAPPING['private'])
        return res[0] if len(res) else False

