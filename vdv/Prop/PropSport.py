

from sqlalchemy import Column, Integer, Sequence
from sqlalchemy.ext.declarative import declarative_base

from vdv.Entities.EntityMedia import EntityMedia
from vdv.Prop.PropBase import PropBase

Base = declarative_base()

from vdv.db import DBConnection

class PropSport(PropBase, Base):
    __tablename__ = 'vdv_prop_sport'

    def __init__(self, vdvid, propid, value):
        super().__init__(vdvid, propid, value)