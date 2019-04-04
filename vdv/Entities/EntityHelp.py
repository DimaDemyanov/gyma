import datetime
import time

from sqlalchemy import Column, String, Integer, Date, Sequence, Boolean
from sqlalchemy.ext.declarative import declarative_base

from gyma.vdv.Entities.EntityBase import EntityBase
from gyma.vdv.Entities.EntityProp import EntityProp

from gyma.vdv.db import DBConnection


Base = declarative_base()


class EntityHelp(EntityBase, Base):
    __tablename__ = 'vdv_help'

    vdvid = Column(Integer, Sequence('vdv_seq'), primary_key=True)
    accountid = Column(Integer)
    message = Column(String)
    created = Column(Date)
    isdone = Column(Boolean)
    donetime = Column(Date)

    json_serialize_items_list = ['accountid', 'message']

    def __init__(self, message, accountid):
        super().__init__()
        self.message = message
        self.accountid = accountid
        ts = time.time()
        self.created = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M')
        self.isdone = False

    @classmethod
    def add_from_json(cls, data):
        vdvid = None

        if 'message' in data and 'accountid' in data:
            accountid = data['accountid']
            message = data['message']
            new_entity = EntityHelp(message, accountid)
            vdvid = new_entity.add()

            try:
                with DBConnection() as session:

                    session.db.commit()
            except Exception as e:
                EntityHelp.delete(vdvid)
                raise Exception('Internal error')
        else:
            raise Exception('Validation exception')
        return vdvid

    @classmethod
    def set_done(cls, id):
        PROPNAME_MAPPING = EntityProp.map_name_id()

        vdvid = None

        with DBConnection() as session:
            vdvid = id
            entity = session.db.query(EntityHelp).filter_by(vdvid=vdvid).all()
            if len(entity) == 0:
                vdvid = -1  # No user with given id
            if len(entity):
                for _ in entity:
                    _.isdone = True

                    ts = time.time()

                    _.donetime = datetime.datetime.fromtimestamp(ts).strftime(
                        '%Y-%m-%d %H:%M')

                    session.db.commit()

        return vdvid
