import datetime

from sqlalchemy import Column, String, Integer, Date, Sequence
from sqlalchemy.ext.declarative import declarative_base

from vdv.Entities.EntityBase import EntityBase


from vdv.db import DBConnection

Base = declarative_base()



class EntityEquipment(EntityBase, Base):
    __tablename__ = 'vdv_equipment'

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

            new_entity = EntityEquipment(name)
            vdvid = new_entity.add()

            try:
                with DBConnection() as session:

                    session.db.commit()
            except Exception as e:
                EntityEquipment.delete(vdvid)
                raise Exception('Internal error')
        else:
            raise Exception('Validation exception')
        return vdvid