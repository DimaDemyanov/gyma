

from sqlalchemy import Column, Integer, Sequence
from sqlalchemy.ext.declarative import declarative_base

from vdv.Prop.PropBase import PropBase

Base = declarative_base()


class PropCourtTime(PropBase, Base):
    __tablename__ = 'vdv_prop_court_time'
    def __init__(self, vdvid, propid, value):
        super().__init__(vdvid, propid, value)