from vdv.prop.PropBase import PropBase

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

class PropInt(PropBase, Base):
    __tablename__ = 'vdv_prop_int'

    def __init__(self, name, type):
        super().__init__(name, type)
