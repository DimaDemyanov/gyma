import json
import datetime
import time

from sqlalchemy import Column, String, Integer, Boolean, Date, Sequence
from sqlalchemy.ext.declarative import declarative_base

from vdv.Entities.EntityBase import EntityBase
from vdv.Entities.EntityProp import EntityProp

from vdv.Prop.PropBool import PropBool
from vdv.Prop.PropInt import PropInt
from vdv.Prop.PropReal import PropReal
from vdv.Prop.PropComment import PropComment
from vdv.Prop.PropMedia import PropMedia

Base = declarative_base()

class EntityCourt(EntityBase, Base):
    __tablename__ = 'vdv_court'

    vdvid = Column(Integer, Sequence('vdv_seq'), primary_key=True)
    name = Column(String)
    desc = Column(String)
    created = Column(Date)
    updated = Column(Date)

    json_serialize_items_list = ['vdvid', 'name', 'desc', 'created', 'updated']

    def __init__(self, name, desc):
        super().__init__()

        self.name = name
        self.desc = desc

        ts = time.time()
        self.created = self.updated = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M')

    @classmethod
    def add_from_json(cls, req_json):
        PROPNAME_MAPPING = EntityProp.map_name_id()

        PROP_MAPPING = {
            'private': lambda _vdvid, _id, _value: PropBool(_vdvid, _id, _value).add(),
            'media': lambda _vdvid, _id, _value : [PropMedia(_vdvid, _id, _).add() for _ in _value]
            #TODO fulfill this
        }

        data = json.loads(req_json)

        if ['name', 'desc', 'prop'] in data:
            name = data.name
            desc = data.desc

            vdvid = EntityCourt(name, desc).add()

            for prop in data.prop:
                if prop.name in PROPNAME_MAPPING:
                    PROP_MAPPING[prop.name](vdvid, PROPNAME_MAPPING[prop.name], prop.value)
                else:
                    raise NotImplemented('{%s} not existed property' % prop.name)



