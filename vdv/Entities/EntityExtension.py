import datetime

import pytz as pytz
from sqlalchemy import Column, String, Integer, Date, Sequence, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base

from gyma.vdv.Entities.EntityBase import EntityBase
from gyma.vdv.Entities.EntityCourt import EntityCourt
from gyma.vdv.Entities.EntityTariff import EntityTariff

from gyma.vdv.db import DBConnection
from gyma.vdv.o_utils.utils import get_curr_date, time_add, time_to_str, str_to_time, get_curr_date_str


Base = declarative_base()


class EntityExtension(EntityBase, Base):
    __tablename__ = 'vdv_extension'

    vdvid = Column(Integer, Sequence('vdv_seq'), primary_key=True)
    courtid = Column(Integer)
    tariffid = Column(Integer)
    adminid = Column(Integer)
    isconfirmed = Column(Boolean)
    confirmedtime = Column(Date)
    created = Column(Date)

    json_serialize_items_list = ['vdvid', 'courtid', 'tariffid', 'adminid', 'isconfirmed', 'confirmedtime', 'created']

    def __init__(self, courtid, tariffid):
        super().__init__()
        self.courtid = courtid
        self.tariffid = tariffid
        self.created = get_curr_date()
        self.isconfirmed = False

    @classmethod
    def add_from_json(cls, data):
        if 'courtid' in data and 'tariffid' in data:
            courtid = data['courtid']
            tariffid = data['tariffid']

            new_entity = EntityExtension(courtid, tariffid)
            vdvid = new_entity.add()
        else:
            raise Exception('Validation exception')
        return vdvid

    @classmethod
    def update_from_json(cls, data):
        if 'vdvid' in data:
            ext = EntityExtension.get().filter_by(vdvid=data['vdvid']).all()[0]
            if 'tariffid' in data:
                ext.tariffid = data['tariffid']
        else:
            raise Exception('Validation exception')

    @classmethod
    def confirm(cls, vdvid, adminid):
        with DBConnection() as session:
            extensions = session.db.query(EntityExtension).filter_by(vdvid=vdvid).all()

            for _ in extensions:
                court = session.db.query(EntityCourt).filter_by(vdvid=_.courtid).all()[0]
                tariff = EntityTariff.get().filter_by(vdvid=_.tariffid).all()[0]
                if _.isconfirmed == True:
                    return
                if court.timebegin == None or court.timeend == None:
                    court.timebegin = get_curr_date()
                    court.timeend = time_to_str(time_add(get_curr_date(), tariff.months))
                else:
                    if court.timeend > pytz.utc.localize(get_curr_date()):
                        court.timeend = time_to_str(time_add(court.timeend, tariff.months))
                    else:
                        court.timeend = time_to_str(time_add(get_curr_date(), tariff.months))
                court.ispublished = True
                _.isconfirmed = True
                _.confirmedtime = get_curr_date_str()
                _.adminid = adminid
                session.db.commit()
