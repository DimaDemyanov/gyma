from collections import OrderedDict
import datetime
import time

from sqlalchemy import Column, String, Integer, Date, Sequence, Boolean, cast
from sqlalchemy.ext.declarative import declarative_base

from vdv.Entities.EntityBase import EntityBase
from vdv.Entities.EntityProp import EntityProp
from vdv.Entities.EntityTime import EntityTime
from vdv.Prop.PropCourtTime import PropCourtTime

from vdv.Prop.PropEquipment import PropEquipment
from vdv.Prop.PropMedia import PropMedia
from vdv.Prop.PropLocation import PropLocation
from vdv.Prop.PropRequest import PropRequest
from vdv.Prop.PropSport import PropSport
from vdv.db import DBConnection

Base = declarative_base()


def create_times(s, _vdvid, _id, _val, _uid):
    for _ in _val:
        times = EntityTime.get().filter_by(time=_).all()
        if times:
            id = times[0].vdvid
        if not times:
            id = EntityTime(_).add()
        PropCourtTime(_vdvid, _id, id).add(session=s, no_commit=True)
    s.db.commit()

def update_times(s, _vdvid, _id, _val, _uid):
    ids = [_.vdvid for _ in EntityTime.get().filter(cast(EntityTime.time,Date) == cast(_val[0],Date)).all()]
    times_court = PropCourtTime.get().filter_by(vdvid = _vdvid).filter(PropCourtTime.value.in_(ids)).all()
    for _ in times_court:
        PropCourtTime.delete_one(_.vdvid, _.value)
    create_times(s, _vdvid, _id, _val, _uid)
    s.db.commit()

class EntityCourt(EntityBase, Base):
    __tablename__ = 'vdv_court'

    vdvid = Column(Integer, Sequence('vdv_seq'), primary_key=True)
    ownerid = Column(Integer)
    name = Column(String)
    desc = Column(String)
    price = Column(Integer)
    time_begin = Column(Date)
    months = Column(Date)
    request_time = Column(Date)
    ispublished = Column(Boolean)
    created = Column(Date)
    updated = Column(Date)
    isdraft = Column(Boolean)

    json_serialize_items_list = ['vdvid', 'ownerid', 'name', 'desc', 'price', 'time_begin', 'months', 'request_time', 'ispublished', 'created', 'updated', 'isdraft']

    def __init__(self, ownerid, name, desc, price, time_begin, months, ispublished, isdraft):
        super().__init__()

        self.ownerid = ownerid
        self.name = name
        self.desc = desc
        self.price = price
        self.time_begin = time_begin
        self.months = months
        self.ispublished = ispublished
        self.isdraft = isdraft

        ts = time.time()
        self.request_time = self.created = self.updated = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M')

    def create_times(s, _vdvid, _id, _val, _uid):
        for _ in _val:
            times = EntityTime.get().filter_by(time=_).all()
            if times:
                id = times[0].vdvid
            if not times:
                id = EntityTime(_).add()
            PropCourtTime(_vdvid, _id, id).add(session=s, no_commit=True)

    @classmethod
    def add_from_json(cls, data):
        PROPNAME_MAPPING = EntityProp.map_name_id()

        vdvid = None

        PROP_MAPPING = {
            'location':
                lambda s, _vdvid, _id, _val, _uid: PropLocation(_vdvid, _id, _val)
                    .add(session=s, no_commit=True),
            'media':
                lambda s, _vdvid, _id, _val, _uid: [cls.process_media(s, 'image', _uid, _vdvid, _id, _)
                                                    for _ in _val],
            'equipment':
                lambda s, _vdvid, _id, _val, _uid:[PropEquipment(_vdvid, _id, _).add(session=s, no_commit=True)
                                                    for _ in _val],
            'sport':
                lambda s, _vdvid, _id, _val, _uid: [PropSport(_vdvid, _id, _).add(session=s, no_commit=True)
                                                    for _ in _val],
            'court_time':
                lambda s, _vdvid, _id, _val, _uid: cls.create_times(s, _vdvid, _id, _val, _uid)

        }

        if 'ownerid' in data and 'name' in data and 'months' in data and 'isdraft' in data:
            ownerid = data['ownerid']
            name = data['name']
            if 'time_begin' in data:
                time_begin = data['time_begin']
            else:
                time_begin = None
            months = data['months']
            isdraft = data['isdraft']
            if 'ispublished' in data:
                ispublished = data['ispublished']
            else:
                ispublished = False
            if 'price' in data:
                price = data['price']
            else:
                price = -1
            if 'desc' in data:
                desc = data['desc']
            else:
                desc = ''
            new_entity = EntityCourt(ownerid, name, desc, price, time_begin, months, ispublished, isdraft)
            vdvid = new_entity.add()

        if 'prop' in data:
            with DBConnection() as session:
                for prop_name, prop_val in data['prop'].items():
                    if prop_name in PROPNAME_MAPPING and prop_name in PROP_MAPPING:
                        PROP_MAPPING[prop_name](session, vdvid, PROPNAME_MAPPING[prop_name], prop_val, ownerid)
                    else:
                        new_entity.delete(vdvid)
                        raise Exception('{%s} not existed property\nPlease use one of:\n%s' %
                                        (prop_name, str(PROPNAME_MAPPING)))

                session.db.commit()

        return vdvid

    def update_times(s, _vdvid, _id, _val, _uid):
        times_court = PropCourtTime.get().filter_by(vdvid = _vdvid).all()
        for _ in times_court:
            PropCourtTime.delete_value(_.value)
        create_times(s, _vdvid, _id, _val, _uid)


    @classmethod
    def update_from_json(cls, data):
        def process_avatar(s, _vdvid, _id, _val):
            PropMedia.delete(_vdvid, _id, False)
            cls.process_media(s, 'image', _vdvid, _vdvid, _id, _val)

        PROPNAME_MAPPING = EntityProp.map_name_id()

        vdvid = None

        PROP_MAPPING = {
            'location':
                lambda s, _vdvid, _id, _val, _uid: PropLocation(_vdvid, _id, _val)
                    .update(session=s, no_commit=True),
            'media':
                lambda s, _vdvid, _id, _val, _uid: [cls.process_media(s, 'image', _uid, _vdvid, _id, _)
                                                    for _ in _val],
            'equipment':
                lambda s, _vdvid, _id, _val, _uid: [PropEquipment(_vdvid, _id, _).update(session=s, no_commit=True)
                                                    for _ in _val],
            'sport':
                lambda s, _vdvid, _id, _val, _uid: [PropSport(_vdvid, _id, _).update(session=s, no_commit=True)
                                                    for _ in _val],
            'court_time':
                lambda s, _vdvid, _id, _val, _uid: cls.update_times(s, _vdvid, _id, _val, _uid)
        }

        if 'id' in data:
            with DBConnection() as session:
                vdvid = data['id']
                entity = session.db.query(EntityCourt).filter_by(vdvid=vdvid).all()
                if len(entity) == 0:
                    vdvid = -1  # No user with given id
                if len(entity):
                    for _ in entity:
                        if 'ownerid' in data:
                            _.ownerid = data['ownerid']

                        if 'name' in data:
                            _.name = data['name']

                        if 'desc' in data:
                            _.desc = data['desc']

                        if 'price' in data:
                            _.price = data['price']

                        if 'time_begin' in data:
                            _.time_begin = data['time_begin']

                        if 'months' in data:
                            _.months = data['months']

                        if 'prop' in data:
                            for prop_name, prop_val in data['prop'].items():
                                if prop_name in PROPNAME_MAPPING and prop_name in PROP_MAPPING:
                                    PROP_MAPPING[prop_name](session, vdvid, PROPNAME_MAPPING[prop_name], prop_val, 0)

                        session.db.commit()

        return vdvid

    @classmethod
    def get_wide_object(cls, vdvid, items=[]):
        PROPNAME_MAPPING = EntityProp.map_name_id()

        PROP_MAPPING = {
            'location':  lambda _vdvid, _id: PropLocation.get_object_property(_vdvid, _id),
            'media':     lambda _vdvid, _id: PropMedia.get_object_property(_vdvid, _id),
            'equipment': lambda _vdvid, _id: PropEquipment.get_object_property(_vdvid, _id),
            'sport': lambda _vdvid, _id: PropSport.get_object_property(_vdvid, _id),
            #'court_time': lambda _vdvid, _id: [str(EntityTime.get().filter_by(vdvid = _).all()[0].time) for _ in PropCourtTime.get_object_property(_vdvid, _id)]
        }

        result = EntityCourt.get().filter_by(vdvid=vdvid).all()[0].to_dict()

        for key, propid in PROPNAME_MAPPING.items():
            if key in PROP_MAPPING and (not len(items) or key in items):
                result.update({key: PROP_MAPPING[key](vdvid, propid)})

        return result

    @classmethod
    def delete_wide_object(cls, vdvid):
        PROPNAME_MAPPING = EntityProp.map_name_id()

        PROP_MAPPING = {
            'location':  lambda _vdvid, _id: PropLocation.delete(_vdvid, _id, False),
            'request': lambda _vdvid, _id: PropRequest.delete(_vdvid, _id, False),
            'media':     lambda _vdvid, _id: PropMedia.delete(_vdvid, _id, False),
            'equipment': lambda _vdvid, _id: PropMedia.delete(_vdvid, _id, False)
        }

        for key, propid in PROPNAME_MAPPING.items():
            if key in PROP_MAPPING:
                PROP_MAPPING[key](vdvid, propid)