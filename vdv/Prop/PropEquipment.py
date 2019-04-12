from sqlalchemy import Column, Integer, Sequence
from sqlalchemy.ext.declarative import declarative_base

from gyma.vdv.Prop.PropBase import PropBase


Base = declarative_base()


class PropEquipment(PropBase, Base):
    __tablename__ = 'vdv_prop_equipment'

    def __init__(self, vdvid, propid, value):
        super().__init__(vdvid, propid, value)
