from sqlalchemy import Column, Integer, Sequence, String
from sqlalchemy.ext.declarative import declarative_base

from vdv.Entities.EntityBase import EntityBase
from vdv.Entities.EntityUser import EntityUser

from vdv.db import DBConnection

Base = declarative_base()

class EntitySuperUser(EntityBase, Base):
    __tablename__ = 'vdv_user_admin'

    vdvid = Column(Integer, Sequence('vdv_seq'), primary_key=True)
    userid = Column(Integer, unique=True)
    level = Column(String)

    json_serialize_items_list = ['vdvid', 'userid', 'level']

    def __init__(self, userid, level):
        super().__init__()

        self.userid = userid
        self.level = level

    @classmethod
    def add_from_json(cls, data):
        vdvid = None

        if 'e_mail' in data and 'type' in data:
            e_mail = data['e_mail']
            type = data['type']
            id = EntityUser.get_id_from_email(e_mail)

            new_entity = EntitySuperUser(id, type)
            vdvid = new_entity.add()

        return vdvid

    @classmethod
    def is_id_super_admin(cls, userid):
        res = cls.get().filter_by(userid=userid).first()
        if res:
            return res.level == 'super'

        return False