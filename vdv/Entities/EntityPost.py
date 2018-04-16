from collections import OrderedDict
import datetime
import time

from sqlalchemy import Column, String, Integer, Date, Sequence
from sqlalchemy.ext.declarative import declarative_base

from vdv.Entities.EntityBase import EntityBase
from vdv.Entities.EntityProp import EntityProp
from vdv.Entities.EntityLocation import EntityLocation
from vdv.Entities.EntityComment import EntityComment
from vdv.Entities.EntityMedia import EntityMedia
from vdv.Entities.EntityLike import EntityLike

from vdv.Prop.PropLocation import PropLocation
from vdv.Prop.PropComment import PropComment
from vdv.Prop.PropLike import PropLike
from vdv.Prop.PropMedia import PropMedia

from vdv.db import DBConnection

Base = declarative_base()


class EntityPost(EntityBase, Base):
    __tablename__ = 'vdv_post'

    vdvid = Column(Integer, Sequence('vdv_seq'), primary_key=True)
    userid = Column(Integer)
    description = Column(String)
    created = Column(Date)
    updated = Column(Date)

    json_serialize_items_list = ['vdvid', 'userid', 'description', 'created', 'updated']

    def __init__(self, userid, description):
        super().__init__()

        self.userid = userid
        self.description = description

        ts = time.time()
        self.created = self.updated = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M')

    @classmethod
    def add_from_json(cls, data, userId):
        vdvid = None

        if userId is None:
            return None

        PROPNAME_MAPPING = EntityProp.map_name_id()

        PROP_MAPPING = {
            'location':
                lambda s, _vdvid, _id, _val: PropLocation(_vdvid, _id, _val).add(session=s, no_commit=True),
            'comment':
                lambda s, _vdvid, _id, _val: [PropComment(_vdvid, _id, _).add(session=s, no_commit=True) for _ in _val],
            'media':
                lambda s, _vdvid, _id, _val: [PropMedia(_vdvid, _id, _).add(session=s, no_commit=True) for _ in _val],
            'like':
                lambda s, _vdvid, _id, _val: [PropLike(_vdvid, _id, _).add(session=s, no_commit=True) for _ in _val]
        }

        if 'description' in data and "prop" in data:
            description = data['description']

            new_entity = EntityPost(userId, description)
            vdvid = new_entity.add()

            with DBConnection() as session:
                for prop_name, prop_val in data['prop'].items():

                    if prop_name in PROPNAME_MAPPING and prop_name in PROP_MAPPING:
                        PROP_MAPPING[prop_name](session, vdvid, PROPNAME_MAPPING[prop_name], prop_val)
                    else:
                        new_entity.delete(vdvid)
                        raise Exception('{%s} not existed property\nPlease use one of:\n%s' %
                                        (prop_name, str(PROPNAME_MAPPING)))

                from vdv.Prop.PropPost import PropPost
                PropPost(userId, PROPNAME_MAPPING["post"], vdvid).add(session, no_commit=True)
                session.db.commit()

        return vdvid

    @classmethod
    def get_wide_object(cls, vdvid):
        PROPNAME_MAPPING = EntityProp.map_name_id()

        PROP_MAPPING = {
            'location': lambda _vdvid, _id: PropLocation.get_object_property(_vdvid, _id),
            'comment':  lambda _vdvid, _id: PropComment.get_object_property(_vdvid, _id),
            'media':    lambda _vdvid, _id: PropMedia.get_object_property(_vdvid, _id),
            'like':     lambda _vdvid, _id: PropLike.get_object_property(_vdvid, _id)
        }

        result = {
            'vdvid': vdvid,
        }
        for key, propid in PROPNAME_MAPPING.items():
            if key in PROP_MAPPING:
                result.update({key: PROP_MAPPING[key](vdvid, propid)})

        return result

    @classmethod
    def delete_wide_object(cls, vdvid):
        PROPNAME_MAPPING = EntityProp.map_name_id()

        PROP_MAPPING = {
            'location': lambda _vdvid, _id: PropLocation.delete(_vdvid, _id, False),
            'comment':  lambda _vdvid, _id: PropComment.delete(_vdvid, _id, False),
            'media':    lambda _vdvid, _id: PropMedia.delete(_vdvid, _id, False),
            'like':     lambda _vdvid, _id: PropLike.delete(_vdvid, _id, False)
        }

        for key, propid in PROPNAME_MAPPING.items():
            if key in PROP_MAPPING:
                PROP_MAPPING[key](vdvid, propid)

        from vdv.Prop.PropPost import PropPost
        for _ in EntityPost.get().filter_by(vdvid=vdvid).all():
            PropPost.delete(_.userid, PROPNAME_MAPPING["post"], False)
