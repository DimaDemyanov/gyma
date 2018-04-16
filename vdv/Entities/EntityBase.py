import json

from collections import OrderedDict

from vdv.db import DBConnection

class EntityBase:
    PERMIT_NONE = 0
    PERMIT_ACCESSED = 1
    PERMIT_ADMIN = 2
    PERMIT_OWNER = 2

    json_serialize_items_list = ['']

    def to_dict(self):
        def dictionate_entity(entity):
            try:
                json.dump(entity)
                return entity
            except:
                if 'to_dict' in dir(entity):
                    return entity.to_dict()
                else:
                    return str(entity)

        res = OrderedDict([(key, dictionate_entity(self.__dict__[key])) for key in self.json_serialize_items_list])
        return res

    def __init__(self):
        pass

    def add(self):
        with DBConnection() as session:
            session.db.add(self)
            session.db.commit()
            return self.vdvid

        return None

    @classmethod
    def delete(cls, vdvid):
        with DBConnection() as session:
            res = session.db.query(cls).filter_by(vdvid=vdvid).all()

            if len(res):
                [session.db.delete(_) for _ in res]
                session.db.commit()
            else:
                raise FileNotFoundError('%s was not found' % cls.__name__)

    @classmethod
    def get(cls):
        with DBConnection() as session:
            return session.db.query(cls)

