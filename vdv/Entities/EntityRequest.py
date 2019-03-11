
from sqlalchemy import Column, String, Integer, Date, Sequence, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from vdv.Entities.EntityBase import EntityBase
from vdv.Entities.EntityLandlord import EntityLandlord
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
        # for _ in pid:
        #     PropCourtTime.delete_one(vdvid=_.vdvid, value=_.value)


class EntityRequest(EntityBase, Base):
    __tablename__ = 'vdv_request'

    vdvid = Column(Integer, Sequence('vdv_seq'), primary_key=True)
    accountid = Column(Integer)
    courtid = Column(Integer)
    isconfirmed = Column(Boolean)
    ownertype = Column(String)
    requestid = Column(Integer)
    come = Column(Boolean)
    iscanceled = Column(Boolean)
    #court = relationship('EntityCourt', back_populates="request")

    json_serialize_items_list = ['vdvid','accountid', 'courtid', 'isconfirmed', 'ownertype', 'requestid', 'come', 'iscanceled']

    def __init__(self, accountid, courtid, ownertype, requestid):
        super().__init__()
        self.accountid = accountid
        self.courtid = courtid
        self.ownertype = ownertype
        self.requestid = requestid
        self.isconfirmed = None
        self.come = False
        self.iscanceled = False

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
            with DBConnection() as session:
                if 'accountid' in data and 'courtid' in data and 'ownertype' in data:
                    accountid = data['accountid']
                    courtid = data['courtid']
                    ownertype = data['ownertype']

                    new_entity = EntityRequest(accountid, courtid, ownertype, requestid)
                    vdvid = new_entity.add()

                    if 'prop' in data:

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


    @classmethod
    def get_wide_object(cls, vdvid, items=[]):
        PROPNAME_MAPPING = EntityProp.map_name_id()


        requests = EntityRequest.get().filter_by(vdvid=vdvid).all()[0]
        result = requests.to_dict()
        if 'landlord' in items:
            from vdv.Entities.EntityCourt import EntityCourt
            result.update({'landlord': EntityLandlord.get_wide_object(EntityLandlord.get().filter_by(vdvid=EntityCourt.get().filter_by(vdvid = requests[0].courtid).all()[0].ownerid).all()[0].vdvid)})
        if 'times' in items:
            result.update({'times':
                [time.time.strftime('%Y-%m-%d %H:%M') for time in EntityTime.get().filter(EntityTime.vdvid.in_(PropRequestTime.get_object_property(requests.vdvid, PROPNAME_MAPPING['request_time']))).all()]})

        return result

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
    def cancel(cls, vdvid):
        PROPNAME_MAPPING = EntityProp.map_name_id()
        with DBConnection() as session:
            entity = session.db.query(EntityRequest).filter_by(vdvid=vdvid).all()

            if len(entity):
                for _ in entity:
                    _.iscanceled = True
            session.db.commit()

    @classmethod
    def confirm(cls, vdvid):
        PROPNAME_MAPPING = EntityProp.map_name_id()
        with DBConnection() as session:
            entity = session.db.query(EntityRequest).filter_by(vdvid=vdvid).all()

            if len(entity):
                for _ in entity:
                    _.isconfirmed = True
                    times = PropRequestTime.get_object_property(_.vdvid, PROPNAME_MAPPING['request_time'])
                    for t in times:
                        PropCourtTime.delete_one(_.courtid, t)
                        for req in EntityRequest.get().filter(EntityRequest.vdvid.in_(PropRequestTime.get_objects(t, PROPNAME_MAPPING['request_time']))).all():
                            req.isconfirmed = False



                session.db.commit()

    @classmethod
    def set_come(cls, id, hascome):
        with DBConnection() as session:
            with DBConnection() as session:
                entity = session.db.query(EntityRequest).filter_by(vdvid=id).all()

                if len(entity):
                    for _ in entity:
                        _.come = hascome
                session.db.commit()

    @classmethod
    def get_request_by_requestid(cls, requestid):
        objects = EntityRequest.get().filter_by(requestid=requestid).all()
        return objects
