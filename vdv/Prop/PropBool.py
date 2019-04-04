from gyma.vdv.Prop.PropBase import PropBase

from sqlalchemy import Column, Boolean
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class PropBool(PropBase, Base):
    __tablename__ = 'vdv_prop_court_time'
    value = Column(Boolean)

    def __init__(self, vdvid, propid, value):
        super().__init__(vdvid, propid, value)
