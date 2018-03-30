from vdv.Prop.PropBase import PropBase

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

class PropReal(PropBase, Base):
    __tablename__ = 'vdv_prop_real'

    def __init__(self, vdvid, propid, value):
        super().__init__(vdvid, propid, value)
