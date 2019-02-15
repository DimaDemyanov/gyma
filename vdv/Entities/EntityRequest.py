from collections import OrderedDict
import time
import datetime

from sqlalchemy import Column, String, Integer, Date, Sequence, Boolean
from sqlalchemy.ext.declarative import declarative_base


from vdv.Entities.EntityBase import EntityBase
from vdv.Entities.EntityProp import EntityProp
from vdv.Entities.EntityTime import EntityTime

from vdv.Prop.PropCourtTime import PropCourtTime

from vdv.Prop.PropMedia import PropMedia
from vdv.Prop.PropPost import PropPost
from vdv.Prop.PropRequestTime import PropRequestTime

from vdv.db import DBConnection

Base = declarative_base()

def to_request_times(s, _vdvid, _id, _val, _uid):
    for _ in _val:
        times = EntityTime.get().filter_by(time=_).all()
        if times:
            id = times[0].vdvid
        if not times:
            raise Exception('No time for request')
        courtid = EntityRequest.get().filter_by(vdvid=_vdvid).all()[0].courtid
        pid = PropCourtTime.get().filter_by(vdvid = int(courtid)).filter_by(value = id).all()
        if not pid:
            raise Exception('No time for request')
        PropRequestTime(_vdvid, _id, id).add(session=s)
        for _ in pid:
            PropCourtTime.delete_one(vdvid=_.vdvid, value=_.value)


class EntityRequest(EntityBase, Base):
    __tablename__ = 'vdv_request'

    vdvid = Column(Integer, Sequence('vdv_seq'), primary_key=True)
    accountid = Column(Integer)
    courtid = Column(Integer)
    isconfirmed = Column(Boolean)
    ownertype = Column(String)
    requestid = Column(Integer)


    json_serialize_items_list = ['vdvid','accountid', 'courtid', 'isconfirmed', 'ownertype', 'requestid']

    def __init__(self, accountid, courtid, ownertype, requestid):
        super().__init__()
        self.accountid = accountid
        self.courtid = courtid
        self.ownertype = ownertype
        self.requestid = requestid
        self.isconfirmed = None

    @classmethod
    def add_from_json(cls, datas):
        PROPNAME_MAPPING = EntityProp.map_name_id()

        vdvid = None

        PROP_MAPPING = {
            'request_time':
                lambda s, _vdvid, _id, _val, _uid: to_request_times(s, _vdvid, _id, _val, _uid)

        }

        with DBConnection() as session:
            requestid = session.db.execute(Sequence('vdv_req'))

        for data in datas:

            if 'accountid' in data and 'courtid' in data and 'ownertype' in data:
                accountid = data['accountid']
                courtid = data['courtid']
                ownertype = data['ownertype']

                new_entity = EntityRequest(accountid, courtid, ownertype, requestid)
                vdvid = new_entity.add()

                if 'prop' in data:
                    with DBConnection() as session:
                        for prop_name, prop_val in data['prop'].items():
                            if prop_name in PROPNAME_MAPPING and prop_name in PROP_MAPPING:
                                PROP_MAPPING[prop_name](session, vdvid, PROPNAME_MAPPING[prop_name], prop_val, accountid)
                            else:
                                new_entity.delete(vdvid)
                                raise Exception('{%s} not existed property\nPlease use one of:\n%s' %
                                                (prop_name, str(PROPNAME_MAPPING)))

                        session.db.commit()
            else:
                raise Exception('Validation exception')
        return requestid

    @classmethod
    def update_from_json(cls, data):
        return
        # def process_avatar(s, _vdvid, _id, _val):
        #     PropMedia.delete(_vdvid, _id, False)
        #     cls.process_media(s, 'image', _vdvid, _vdvid, _id, _val)
        #
        # PROPNAME_MAPPING = EntityProp.map_name_id()
        #
        # vdvid = None
        #
        # PROP_MAPPING = {
        #     'private':
        #         lambda session, _vdvid, _id, _value:
        #         PropBool(_vdvid, _id, _value).update(session=session)
        #         if len(PropBool.get().filter_by(vdvid=_vdvid, propid=_id).all())
        #         else PropBool(_vdvid, _id, _value).add(session=session),
        #     'avatar':
        #         lambda s, _vdvid, _id, _val:
        #         process_avatar(s, _vdvid, _id, _val)
        #
        # }
        #
        # if 'id' in data:
        #     with DBConnection() as session:
        #         vdvid = data['id']
        #         entity = session.db.query(EntityAccount).filter_by(vdvid=vdvid).all()
        #
        #         if len(entity):
        #             for _ in entity:
        #                 if 'username' in data:
        #                     _.username = data['username']
        #
        #                 if 'e_mail' in data:
        #                     _.e_mail = data['e_mail']
        #
        #                 session.db.commit()
        #
        #                 for prop_name, prop_val in data['prop'].items():
        #                     if prop_name in PROPNAME_MAPPING and prop_name in PROP_MAPPING:
        #                         PROP_MAPPING[prop_name](session, vdvid, PROPNAME_MAPPING[prop_name], prop_val)
        #
        #                 session.db.commit()
        #
        # return vdvid


    # @classmethod
    # def get_wide_object(cls, vdvid, items=[]):
    #     PROPNAME_MAPPING = EntityProp.map_name_id()
    #
    #     PROP_MAPPING = {
    #         'private': lambda _vdvid, _id: PropBool.get_object_property(_vdvid, _id),
    #         'post': lambda _vdvid, _id: PropPost.get_object_property(_vdvid, _id),
    #         'avatar': lambda _vdvid, _id: PropMedia.get_object_property(_vdvid, _id, ['vdvid', 'url'])
    #     }
    #
    #     result = {
    #         'vdvid': vdvid,
    #         'court': []
    #     }
    #     for key, propid in PROPNAME_MAPPING.items():
    #         if key in PROP_MAPPING and (not len(items) or key in items):
    #             result.update({key: PROP_MAPPING[key](vdvid, propid)})
    #
    #     courts = EntityCourt.get().filter_by(ownerid=vdvid).all()
    #
    #     for _ in courts:
    #         result['court'].append(EntityCourt.get_wide_object(_.vdvid))
    #
    #     return result

    @classmethod
    def decline(cls, vdvid):
        PROPNAME_MAPPING = EntityProp.map_name_id()
        with DBConnection() as session:
            entity = session.db.query(EntityRequest).filter_by(vdvid=vdvid).all()

            if len(entity):
                for _ in entity:
                    _.isconfirmed = False
                    pid = PropRequestTime.get().filter_by(vdvid=vdvid).all()
                    for i in pid:
                        PropCourtTime(_.courtid, PROPNAME_MAPPING['court_time'], i.value).add(session=session, no_commit=True)
                        PropRequestTime.delete_one(i.vdvid, i.value)
                session.db.commit()

    @classmethod
    def confirm(cls, vdvid):
        with DBConnection() as session:
            entity = session.db.query(EntityRequest).filter_by(vdvid=vdvid).all()

            if len(entity):
                for _ in entity:
                    _.isconfirmed = True

                session.db.commit()


    # @classmethod
    # def get_id_from_username(cls, username):
    #     try:
    #         return cls.get().filter_by(username=username).all()[0].vdvid
    #     except:
    #         return None
    #
    # @classmethod
    # def get_id_from_email(cls, e_mail):
    #     try:
    #         return cls.get().filter_by(e_mail=e_mail).all()[0].vdvid
    #     except:
    #         return None
    #
    # @classmethod
    # def get_password_from_email(cls, e_mail):
    #     try:
    #         return cls.get().filter_by(e_mail=e_mail).all()[0].password
    #     except:
    #         return None

    # @classmethod
    # def is_private(cls, id):
    #     PROPNAME_MAPPING = EntityProp.map_name_id()
    #     res = PropBool.get_object_property(id, PROPNAME_MAPPING['private'])
    #     return res[0] if len(res) else False

