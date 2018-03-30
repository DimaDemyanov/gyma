from vdv.Prop.PropBase import PropBase

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

class PropReal(PropBase, Base):
    __tablename__ = 'vdv_prop_real'

    def __init__(self, name, type):
        super().__init__(name, type)
