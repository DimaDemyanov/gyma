import datetime

from sqlalchemy import Column, String, Integer, Date, Sequence
from sqlalchemy.ext.declarative import declarative_base

from vdv.Entities.EntityBase import EntityBase


from vdv.db import DBConnection

Base = declarative_base()



class EntityTariff(EntityBase, Base):
    __tablename__ = 'vdv_tariff'

    vdvid = Column(Integer, Sequence('vdv_tariffs_seq'), primary_key=True)
    months = Column(Integer)
    price = Column(Integer)
    sale = Column(Integer)

    json_serialize_items_list = ['vdvid', 'months', 'price', 'sale']

    def __init__(self, months, price, sale):
        super().__init__()
        self.months = months
        self.price = price
        self.sale = sale

    @classmethod
    def add_from_json(cls, data):
        if 'months' in data and 'price' in data and 'sale' in data:
            months = data['months']
            price = data['price']
            sale = data['sale']

            new_entity = EntityTariff(months, price, sale)
            vdvid = new_entity.add()

            try:
                with DBConnection() as session:
                    session.db.commit()
            except Exception as e:
                EntityTariff.delete(vdvid)
                raise Exception('Internal error')
        else:
            raise Exception('Validation exception')
        return vdvid