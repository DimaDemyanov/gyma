from vdv.Prop.PropBase import PropBase

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

class PropBool(PropBase, Base):
    __tablename__ = 'vdv_prop_bool'

    def __init__(self, name, type):
        super().__init__(name, type)
