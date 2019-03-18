import datetime

from sqlalchemy import Column, String, Integer, Date, Sequence
from sqlalchemy.ext.declarative import declarative_base

from vdv.Entities.EntityBase import EntityBase


from vdv.db import DBConnection

Base = declarative_base()



class EntitySport(EntityBase, Base):
    __tablename__ = 'vdv_sport'

    vdvid = Column(Integer, Sequence('vdv_seq'), primary_key=True)
    usertype = Column(String)
    token = Column(String)
    accountid = Column(Integer)

    json_serialize_items_list = ['vdvid', 'name', 'usertype', 'accountid']

    def __init__(self, usertype, token, accounid):
        super().__init__()
        self.usertype = usertype
        self.token = token
        self.accountid = accounid

    @classmethod
    def add_from_json(cls, data):
        vdvid = None

        if 'usertype' in data and 'token' in data and 'accountid' in data:
            usertype = data['usertype']
            token = data['token']
            accountid = data['accountid']

            new_entity = EntitySport(usertype, token, accountid)
            vdvid = new_entity.add()

            try:
                with DBConnection() as session:

                    session.db.commit()
            except Exception as e:
                EntitySport.delete(vdvid)
                raise Exception('Internal error')
        else:
            raise Exception('Validation exception')
        return vdvid