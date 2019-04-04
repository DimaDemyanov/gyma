from sqlalchemy import Column, Integer, Sequence
from sqlalchemy.ext.declarative import declarative_base

from gyma.vdv.Entities.EntityMedia import EntityMedia
from gyma.vdv.Prop.PropBase import PropBase

from gyma.vdv.db import DBConnection


Base = declarative_base()


class PropSport(PropBase, Base):
    __tablename__ = 'vdv_prop_sport'

    def __init__(self, vdvid, propid, value):
        super().__init__(vdvid, propid, value)
