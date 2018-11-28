from collections import OrderedDict
import time
import datetime

from sqlalchemy import Column, String, Integer, Date, Sequence
from sqlalchemy.ext.declarative import declarative_base

from vdv.Entities.EntityBase import EntityBase

from vdv.Prop.PropBool import PropBool
from vdv.Prop.PropMedia import PropMedia
from vdv.Prop.PropPost import PropPost

from vdv.db import DBConnection

Base = declarative_base()



class EntityRequest(EntityBase, Base):
    __tablename__ = 'vdv_request'

    vdvid = Column(Integer, Sequence('vdv_seq'), primary_key=True)
    time_begin = Column(Date)
    time_end = Column(Date)


    json_serialize_items_list = ['vdvid', 'time_begin', 'time_end']

    def __init__(self, time_begin, time_end):
        super().__init__()

        self.time_begin = time_begin
        self.time_end = time_end

    @classmethod
    def add_from_json(cls, data):
        vdvid = None

        if 'time_begin' in data and 'time_end' in data:
            time_begin = data['time_begin']
            time_end = data['time_end']

            new_entity = EntityRequest(time_begin, time_end)
            vdvid = new_entity.add()

            try:
                with DBConnection() as session:
                    # for prop_name, prop_val in data['prop'].items():
                    #     if prop_name in PROPNAME_MAPPING and prop_name in PROP_MAPPING:
                    #         PROP_MAPPING[prop_name](session, vdvid, PROPNAME_MAPPING[prop_name], prop_val, vdvid)
                    #     else:
                    #         EntityUser.delete(vdvid)
                    #         raise Exception('{%s} not existed property\nPlease use one of:\n%s' %
                    #                         (prop_name, str(PROPNAME_MAPPING)))

                    session.db.commit()
            except Exception as e:
                EntityRequest.delete(vdvid)
                raise Exception('Internal error')
        else:
            raise Exception('Validation exception')
        return vdvid

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
        #         entity = session.db.query(EntityUser).filter_by(vdvid=vdvid).all()
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
    def delete_wide_object(cls, vdvid):
        EntityRequest.delete(cls, vdvid)

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

