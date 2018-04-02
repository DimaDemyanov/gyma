from vdv.Prop.PropBase import PropBase

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()
from sqlalchemy import Column, Float

class PropReal(PropBase, Base):
    __tablename__ = 'vdv_prop_real'

    value = Column(Float)

    def __init__(self, vdvid, propid, value):
        super().__init__(vdvid, propid, value)
