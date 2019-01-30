import datetime

from sqlalchemy import Column, String, Integer, Date, Sequence
from sqlalchemy.ext.declarative import declarative_base

from vdv.Entities.EntityBase import EntityBase

from vdv.Prop.PropSport import PropSport
from vdv.Prop.PropBool import PropBool
from vdv.Prop.PropMedia import PropMedia
from vdv.Prop.PropPost import PropPost

from vdv.db import DBConnection

Base = declarative_base()



class EntitySport(EntityBase, Base):
    __tablename__ = 'vdv_sport'

    vdvid = Column(Integer, Sequence('vdv_seq'), primary_key=True)
    name = Column(String)

    json_serialize_items_list = ['vdvid', 'name']

    def __init__(self, name):
        super().__init__()
        self.name = name

    @classmethod
    def add_from_json(cls, data):
        vdvid = None

        if 'name' in data:
            name = data['name']

            new_entity = EntitySport(name)
            vdvid = new_entity.add()

            try:
                with DBConnection() as session:

                    session.db.commit()
            except Exception as e:
                EntitySport.delete(vdvid)
                raise Exception('Internal error')
        else:
            raise Exception('Validation exception')
        return vdvid