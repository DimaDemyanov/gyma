from sqlalchemy import Column, String, Integer, Boolean, Date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import datetime
import time

Base = declarative_base()

class Court(Base):
    __tablename__ = 'vdv_court'

    courtid = Column(Integer, primary_key=True)
    name = Column(String)
    desc = Column(String)
    location = Column(Integer)
    address = Column(String)
    private = Column(Boolean)
    created = Column(Date)
    updated = Column(Date)

    def __init__(self, id, name, desc, location, address, private):
        self.courtid = id
        self.name = name
        self.desc = desc
        self.location = location
        self.address = address
        self.private = private
        ts = time.time()
        self.created = self.updated = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')