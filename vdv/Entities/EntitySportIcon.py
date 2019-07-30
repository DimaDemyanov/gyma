from sqlalchemy import Column, String, Integer, Sequence
from sqlalchemy.ext.declarative import declarative_base

from gyma.vdv.Entities.EntityBase import EntityBase


Base = declarative_base()


class EntitySportIcon(EntityBase, Base):
    __tablename__ = 'vdv_sport_icon'

    vdvid = Column(Integer, Sequence('vdv_seq'), primary_key=True)
    sportid = Column(Integer)
    url = Column(Integer)

    json_serialize_items_list = ['vdvid', 'sportid', 'url']

    def __init__(self, sportid, url):
        super().__init__()
        self.sportid = sportid
        self.url = url
