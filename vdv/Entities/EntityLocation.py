import math

from sqlalchemy import Column, String, Integer, Float, Sequence
from sqlalchemy.ext.declarative import declarative_base

from gyma.vdv.Entities.EntityBase import EntityBase
# from gyma.vdv.Entities.EntityCourt import EntityCourt
from gyma.vdv.Entities.EntityProp import EntityProp


Base = declarative_base()


def distanceMath(lat1, lon1, lat2, lon2, math):
    distance = 6371 * (math.acos(math.sin(math.radians(lat1)) * math.sin(math.radians(lat2)) + math.cos   (
        math.radians(lat1)) * math.cos(math.radians(lat2)) * math.cos(math.radians(lon1) - math.radians(lon2))))
    return distance


class EntityLocation(EntityBase, Base):
    __tablename__ = 'vdv_location'

    vdvid = Column(Integer, Sequence('vdv_seq'), primary_key=True)
    name = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)

    json_serialize_items_list = ['vdvid', 'name', 'latitude', 'longitude']

    def __init__(self, name, latitude, longitude):
        super().__init__()

        self.name = name
        self.latitude = latitude
        self.longitude = longitude

    @classmethod
    def get_wide_info(self, id):
        PROPNAME_MAPPING = EntityProp.map_name_id()
        location = EntityLocation.get().filter_by(vdvid = id).all()[0]
        obj_dict = location.to_dict()
        from vdv.Entities.EntityCourt import EntityCourt
        from vdv.Prop.PropLocation import PropLocation
        prices = [o.price for o in EntityCourt.get().filter(EntityCourt.vdvid.in_(PropLocation.get_objects(id, PROPNAME_MAPPING['location'])))]
        if len(prices) == 0:
            obj_dict.update({'minCost': -1, 'maxCost': -1})
        else:
            min_cost = min(prices)
            max_cost = max(prices)
            obj_dict.update({'minCost': min_cost, 'maxCost': max_cost})
        return obj_dict
