import concurrent.futures as ftr
import json
import logging
import mimetypes
import os
import posixpath
import random
import re
from urllib.parse import parse_qs

import jwt
import requests
from sqlalchemy import and_, cast, DateTime, func, desc
from sqlalchemy import or_
import time
from collections import OrderedDict
from datetime import timedelta

import falcon
from falcon_multipart.middleware import MultipartMiddleware
from gyma.vdv.Entities.EntityCourt import EntityCourt, create_times, update_times
from gyma.vdv import utils
from gyma.vdv.Entities.EntityEquipment import EntityEquipment
from gyma.vdv.Entities.EntityExtension import EntityExtension
from gyma.vdv.Entities.EntityHelp import EntityHelp
from gyma.vdv.Entities.EntityLandlord import EntityLandlord
from gyma.vdv.Entities.EntityRequest import EntityRequest
from gyma.vdv.Entities.EntitySimpleuser import EntitySimpleuser
from gyma.vdv.Entities.EntitySport import EntitySport
from gyma.vdv.Entities.EntityTariff import EntityTariff
from gyma.vdv.Entities.EntityTime import EntityTime
from gyma.vdv.Entities.EntityValidation import EntityValidation
from gyma.vdv.Prop.PropCourtTime import PropCourtTime
from gyma.vdv.Prop.PropEquipment import PropEquipment
from gyma.vdv.Prop.PropRequestTime import PropRequestTime
from gyma.vdv.Prop.PropSport import PropSport
from gyma.vdv.auth import auth
# from gyma.vdv.auth import JWT_SIGN_ALGORITHM
from gyma.vdv.db import DBConnection
from gyma.vdv.o_utils.utils import get_curr_date
from gyma.vdv.serve_swagger import SpecServer

from gyma.vdv.Entities.EntityBase import EntityBase

from gyma.vdv.Entities.EntityAccount import EntityAccount
from gyma.vdv.Entities.EntityLocation import EntityLocation, distanceMath
from gyma.vdv.Entities.EntityMedia import EntityMedia

from gyma.vdv.search import *

from gyma.vdv.Prop.PropMedia import PropMedia

from gyma.vdv.MediaResolver.MediaResolverFactory import MediaResolverFactory

from haversine import haversine

JWT_SIGN_ALGORITHM = 'HS256'
JWT_PUBLIC_KEY = 'secretterces123'
JWT_EXP_TIME = 14 * 24 * 3600


def stringToBool(str):
    # empty string is included because we allow empty-valued flags in query
    return str.lower() in ['true', '1', 'yes', 'y', '']


def safeToInt(s):
    if not s:
        return None
    try:
        return int(s)
    except ValueError:
        return None


def obj_to_json(obj):
    return json.dumps(obj, indent=2)


def getPathParam(name, **request_handler_args):
    # Falcon fails to strip the rest of the query from path param
    return request_handler_args['uri_fields'][name].partition('?')[0]


def getIntPathParam(name, **request_handler_args):
    s = getPathParam(name, **request_handler_args)
    try:
        return int(s)
    except ValueError:
        return None


def getStrPathParam(name, **request_handler_args):
    s = getPathParam(name, **request_handler_args)
    try:
        return str(s)
    except ValueError:
        return None


def guess_response_type(path):
    if not mimetypes.inited:
        mimetypes.init()  # try to read system mime.types

    extensions_map = mimetypes.types_map.copy()
    extensions_map.update({
        '': 'application/octet-stream',  # Default
        '.py': 'text/plain',
        '.c': 'text/plain',
        '.h': 'text/plain',
    })

    base, ext = posixpath.splitext(path)
    if ext in extensions_map:
        return extensions_map[ext]
    ext = ext.lower()
    if ext in extensions_map:
        return extensions_map[ext]
    else:
        return extensions_map['']


def date_time_string(timestamp=None):
    weekdayname = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

    monthname = [None,
                 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    if timestamp is None:
        timestamp = time.time()
    year, month, day, hh, mm, ss, wd, y, z = time.gmtime(timestamp)
    s = "%s, %02d %3s %4d %02d:%02d:%02d GMT" % (
        weekdayname[wd],
        day, monthname[month], year,
        hh, mm, ss)
    return s


def httpDefault(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    path = req.path
    src_path = path
    path = path.replace(baseURL, '.')

    if os.path.isdir(path):
        for index in "index.html", "index.htm", "test-search.html":
            index = os.path.join(path + '/', index)
            logger.info(index + '      ' + os.getcwd())
            if os.path.exists(index):
                path = index
                break
        else:
            return None

    if path.endswith('swagger.json'):
        path = path.replace('swagger.json', 'swagger_temp.json')

    ctype = guess_response_type(path)

    try:
        with open(path, 'rb') as f:
            resp.status = falcon.HTTP_200

            fs = os.fstat(f.fileno())
            length = fs[6]

            buffer = f.read()
            if path.endswith('index.html'):
                str = buffer.decode()
                str = str.replace('127.0.0.1:4201', server_host)
                logger.info(str)
                buffer = str.encode()
                length = len(buffer)
    except IOError:
        try:
            with open('swagger-ui/' + path, 'rb') as f:
                resp.status = falcon.HTTP_200

                fs = os.fstat(f.fileno())
                length = fs[6]

                buffer = f.read()
                if path.endswith('index.html'):
                    str = buffer.decode()
                    str = str.replace('127.0.0.1:4201', server_host)
                    logger.info(str)
                    buffer = str.encode()
                    length = len(buffer)
        except IOError:
            resp.status = falcon.HTTP_404
            return

    resp.set_header("Content-type", ctype)
    resp.set_header("Content-Length", length)
    resp.set_header("Last-Modified", date_time_string(fs.st_mtime))
    resp.set_header("Access-Control-Allow-Origin", "*")
    resp.set_header("Path", path)
    resp.body = buffer


def getVersion(**request_handler_args):
    resp = request_handler_args['resp']
    resp.status = falcon.HTTP_501
    with open("VERSION") as f:
        resp.body = obj_to_json({"version": f.read()})


def initDatabase(**request_handler_args):
    resp = request_handler_args['resp']

    # with DBConnection() as db:
    #    db.init()

    resp.status = falcon.HTTP_501


def cleanupDatabase(**request_handler_args):
    resp = request_handler_args['resp']
    # with DBConnection() as db:
    #    db.Cleanup()

    resp.status = falcon.HTTP_501


def createRequest(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    phone = req.context['phone']

    params = json.loads(req.stream.read().decode('utf-8'))
    # try:
    id = EntityRequest.add_from_json(params)
    # except:
    #     resp.status = falcon.HTTP_412
    #     return
    if id:
        objects = EntityRequest.get().filter_by(requestid=id).all()
        resp.body = obj_to_json([object.to_dict() for object in objects])
        resp.status = falcon.HTTP_200


def getAllUserRequests(**request_handler_args):
    PROPNAME_MAPPING = EntityProp.map_name_id()

    req = request_handler_args['req']
    resp = request_handler_args['resp']

    id = getIntPathParam('userId', **request_handler_args)
    if 'date' in req.params:
        date = req.params['date']
    else:
        date = None

    # TODO: rewrite SQL

    if date:
        ondate = EntityTime.get().filter(cast(EntityTime.time, Date) == date).all()
        res = []
        for _ in ondate:
            reqs = PropRequestTime.get_objects(_.vdvid, PROPNAME_MAPPING['requestTime'])

            for i in EntityRequest.get().filter_by(accountid=id).filter(EntityRequest.vdvid.in_(reqs)).all():
                for j in EntityRequest.get_request_by_requestid(i.requestid):
                    res.append(j)
    else:
        res = EntityRequest.get().filter_by(accountid=id).all()
    res = [EntityRequest.get_wide_object(o.vdvid) for o in res]

    a = res
    b = []
    for i in range(0, len(a)):
        if a[i] not in a[i + 1:]:
            b.append(a[i])

    resp.body = obj_to_json(b)  # obj_to_json([dict(t) for t in {tuple(d.items()) for d in res}])
    resp.status = falcon.HTTP_200


def getAllCourtRequestsByDate(**request_handler_args):
    PROPNAME_MAPPING = EntityProp.map_name_id()

    req = request_handler_args['req']
    resp = request_handler_args['resp']

    id = getIntPathParam('courtId', **request_handler_args)
    if 'date' in req.params:
        date = req.params['date']
    else:
        date = None
    res = []

    # TODO: rewrite SQL theme

    if date:
        ondate = EntityTime.get().filter(cast(EntityTime.time, Date) == date).all()
        for _ in ondate:
            reqs = PropRequestTime.get_objects(_.vdvid, PROPNAME_MAPPING['requestTime'])
            for i in EntityRequest.get().filter_by(courtid=id).filter(EntityRequest.vdvid.in_(reqs)).all():
                for j in EntityRequest.get_request_by_requestid(i.requestid):
                    res.append(j)
    else:
        for i in EntityRequest.get().filter_by(courtid=id).all():
            for j in EntityRequest.get_request_by_requestid(i.requestid):
                res.append(j)
    resp.body = obj_to_json([o.to_dict() for o in res])
    resp.status = falcon.HTTP_200

def getAllCourtRequest(**request_handler_args):
    PROPNAME_MAPPING = EntityProp.map_name_id()

    req = request_handler_args['req']
    resp = request_handler_args['resp']

    res = []

    id = getIntPathParam('courtId', **request_handler_args)
    # extensions = EntityExtension.get().filter(EntityExtension.isconfirmed == False or (cast(EntityExtension.confirmed_time, DateTime) > get_curr_date() - timedelta(hours=24))).all()

    with DBConnection() as session:
        res = session.db.query(EntityRequest)\
            .join(EntityCourt, EntityRequest.courtid == EntityCourt.vdvid)\
            .filter(cast(EntityTime.time, DateTime) > get_curr_date() - timedelta(hours=24))
    resp.body = obj_to_json([o[0].to_dict() for o in res])
    resp.status = falcon.HTTP_200


def getAllLandlordRequests(**request_handler_args):
    PROPNAME_MAPPING = EntityProp.map_name_id()

    req = request_handler_args['req']
    resp = request_handler_args['resp']

    id = getIntPathParam('landlordId', **request_handler_args)
    if 'date' in req.params:
        date = req.params['date']
    else:
        date = None

    courts = [o.vdvid for o in EntityCourt.get().filter_by(ownerid=id).all()]
    res = []
    if date:
        with DBConnection() as session:
            res = [s[0] for s in session.db.query(EntityRequest, PropRequestTime, EntityTime).filter(cast(EntityTime.time, Date) == date).filter(
                EntityRequest.courtid.in_(courts)).filter(
                PropRequestTime.value == EntityTime.vdvid).filter(EntityRequest.vdvid == PropRequestTime.vdvid).distinct(EntityRequest.vdvid)]
    else:
        with DBConnection() as session:
            res = [s[0] for s in session.db.query(EntityRequest, PropRequestTime, EntityTime).filter(
                EntityRequest.courtid.in_(courts)).filter(
                PropRequestTime.value == EntityTime.vdvid).filter(
                EntityRequest.vdvid == PropRequestTime.vdvid).distinct(EntityRequest.vdvid)]
    EntityRequest.get().filter(EntityRequest.courtid in courts)
    resp.body = obj_to_json([EntityRequest.get_wide_object(o.vdvid, ['times']) for o in res])
    resp.status = falcon.HTTP_200


def getAllLandlordRequestsWithFilter(**request_handler_args):
    PROPNAME_MAPPING = EntityProp.map_name_id()

    req = request_handler_args['req']
    resp = request_handler_args['resp']

    id = getIntPathParam('landlordId', **request_handler_args)
    filter = req.params['filter']

    courts = EntityCourt.get().filter_by(ownerid=id).all()
    res = []
    for c in courts:
        ondate = EntityTime.get().filter(cast(EntityTime.time, DateTime) >= datetime.datetime.today()).all()

        for _ in ondate:
            reqs = PropRequestTime.get_objects(_.vdvid, PROPNAME_MAPPING['requestTime'])
            reqss = None
            if filter == 'confirmed':
                reqss = EntityRequest.get().filter_by(courtid=c.vdvid).filter(EntityRequest.vdvid.in_(reqs),
                                                                              EntityRequest.isconfirmed != None).all()
            if filter == 'notconfirmed':
                reqss = EntityRequest.get().filter_by(courtid=c.vdvid).filter(EntityRequest.vdvid.in_(reqs),
                                                                              EntityRequest.isconfirmed == None).all()
            if filter == 'all':
                reqss = EntityRequest.get().filter_by(courtid=c.vdvid).filter(EntityRequest.vdvid.in_(reqs)).all()
            for i in reqss:
                res.append(EntityRequest.get_wide_object(i.vdvid, ['times']))
    a = res
    b = []
    for i in range(0, len(a)):
        if a[i] not in a[i + 1:]:
            b.append(a[i])

    resp.body = obj_to_json(b)
    resp.status = falcon.HTTP_200


def deleteRequest(**request_handler_args):
    resp = request_handler_args['resp']

    id = getIntPathParam('requestId', **request_handler_args)

    if id is not None:
        try:
            EntityRequest.delete_wide_object(id)
        except FileNotFoundError:
            resp.status = falcon.HTTP_404
            return

        object = EntityRequest.get().filter_by(vdvid=id).all()
        if not len(object):
            resp.status = falcon.HTTP_200
            return

    resp.status = falcon.HTTP_400


def cancelRequest(**request_handler_args):
    resp = request_handler_args['resp']

    id = getIntPathParam('requestId', **request_handler_args)

    if id is not None:
        try:
            EntityRequest.cancel(id)
            resp.status = falcon.HTTP_200
            return
        except FileNotFoundError:
            resp.status = falcon.HTTP_404
            return

    resp.status = falcon.HTTP_400


def declineRequest(**request_handler_args):
    resp = request_handler_args['resp']
    id = getIntPathParam('requestid', **request_handler_args)
    EntityRequest.decline(id)
    resp.status = falcon.HTTP_200


def confirmRequest(**request_handler_args):
    resp = request_handler_args['resp']
    id = getIntPathParam('requestid', **request_handler_args)
    EntityRequest.confirm(id)
    resp.status = falcon.HTTP_200


def comeRequest(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']
    id = getIntPathParam('requestid', **request_handler_args)
    hascome = bool(req.params['hascome'])
    EntityRequest.set_come(id, hascome)
    resp.status = falcon.HTTP_200


def createSport(**request_handler_args):  # TODO: implement it
    resp = request_handler_args['resp']
    req = request_handler_args['req']

    try:
        e_mail = req.context['phone']
    except:
        resp.status = falcon.HTTP_400

    params = json.loads(req.stream.read().decode('utf-8'))
    name = params.get('name')
    sports_with_same_name = EntitySport.get().filter_by(name=name).all()
    if len(sports_with_same_name) != 0:
        resp.status = falcon.HTTP_412
        return
    try:
        id = EntitySport.add_from_json(params)
    except Exception as e:
        logger.info(e)
        resp.status = falcon.HTTP_501
        return
    if id:
        objects = EntitySport.get().filter_by(vdvid=id).all()

        resp.body = obj_to_json(objects[0].to_dict())
        resp.status = falcon.HTTP_200
    resp.status = falcon.HTTP_200


def deleteSport(**request_handler_args):  # TODO: implement it
    resp = request_handler_args['resp']

    id = getIntPathParam('sportId', **request_handler_args)

    if id is not None:
        try:
            EntitySport.delete(id)
        except FileNotFoundError:
            resp.status = falcon.HTTP_404
            return

        object = EntitySport.get().filter_by(vdvid=id).all()
        if not len(object):
            resp.status = falcon.HTTP_200
            return

    resp.status = falcon.HTTP_400


def getSports(**request_handler_args):  # TODO: implement it
    resp = request_handler_args['resp']

    objects = EntitySport.get().all()

    resp.body = obj_to_json([o.to_dict() for o in objects])

    resp.status = falcon.HTTP_200


def getSportById(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    id = getIntPathParam('sportId', **request_handler_args)
    objects = EntitySport.get().filter_by(vdvid=id).all()
    if len(objects) == 0:
        resp.status = falcon.HTTP_404
        return

    resp.body = obj_to_json(objects[0].to_dict())
    resp.status = falcon.HTTP_200


def createEquipment(**request_handler_args):  # TODO: implement it
    resp = request_handler_args['resp']
    req = request_handler_args['req']

    try:
        e_mail = req.context['phone']
    except:
        resp.status = falcon.HTTP_400

    params = json.loads(req.stream.read().decode('utf-8'))
    name = params.get('name')
    equipment_with_same_name = EntityEquipment.get().filter_by(name=name).all()
    if len(equipment_with_same_name) != 0:
        resp.status = falcon.HTTP_412
        return
    try:
        id = EntityEquipment.add_from_json(params)
    except Exception as e:
        logger.info(e)
        resp.status = falcon.HTTP_501
        return
    if id:
        objects = EntityEquipment.get().filter_by(vdvid=id).all()

        resp.body = obj_to_json(objects[0].to_dict())
        resp.status = falcon.HTTP_200
    resp.status = falcon.HTTP_200


def deleteEquipment(**request_handler_args):  # TODO: implement it
    resp = request_handler_args['resp']

    id = getIntPathParam('equipmentId', **request_handler_args)

    if id is not None:
        try:
            EntityEquipment.delete(id)
        except FileNotFoundError:
            resp.status = falcon.HTTP_404
            return

        object = EntityEquipment.get().filter_by(vdvid=id).all()
        if not len(object):
            resp.status = falcon.HTTP_200
            return

    resp.status = falcon.HTTP_400


def getEquipments(**request_handler_args):
    resp = request_handler_args['resp']

    objects = EntityEquipment.get().all()

    resp.body = obj_to_json([o.to_dict() for o in objects])

    resp.status = falcon.HTTP_200


def getEquipmentById(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    id = getIntPathParam('equipmentId', **request_handler_args)
    objects = EntityEquipment.get().filter_by(vdvid=id).all()
    if len(objects) == 0:
        resp.status = falcon.HTTP_404
        return

    resp.body = obj_to_json(objects[0].to_dict())
    resp.status = falcon.HTTP_200


def deleteTime(**request_handler_args):  # TODO: implement it
    resp = request_handler_args['resp']
    resp.status = falcon.HTTP_200


def getAllCourts(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    phone = req.context['phone']
    my_id = EntityAccount.get_id_from_phone(phone)
    try:
        my_landlordid = EntityLandlord.get_id_from_accountid(my_id)
    except:
        resp.status = falcon.HTTP_407
        return

    filter = req.params['filter1']  # post_data['filter']

    sort_order = req.params['sortedby']

    with DBConnection() as session:
        if sort_order == 'popularity':
            objects = session.db.query(EntityCourt, func.count(EntityRequest.vdvid).label('total'))\
                .join(EntityRequest, EntityRequest.courtid == EntityCourt.vdvid)\
                .group_by(EntityCourt.vdvid, EntityRequest.vdvid)
        else:
            objects = session.db.query(EntityCourt)

    if filter == 'all':
        pass

    if filter == 'my':
        objects = objects.filter_by(ownerid=my_landlordid)

    if filter == 'notmy':
        objects = objects.filter(EntityCourt.ownerid != my_landlordid)

    filter = req.params['filter2']  # post_data['filter']

    if filter == 'drafts':
        objects = objects.filter_by(isdraft=True)

    if filter == 'published':
        objects = objects.filter_by(ispublished=True)

    if filter == 'notpublished':
        objects = objects.filter_by(ispublished=False)

    if not objects:
        resp.status = falcon.HTTP_408
        return

    if sort_order == 'price':
        objects = objects.order_by(EntityCourt.price, EntityCourt.vdvid)
    if sort_order == 'popularity':
        objects = objects.distinct(EntityCourt.vdvid, 'total').order_by('total', EntityCourt.vdvid)

    a = objects.all()
    if sort_order == 'popularity':
        b = [EntityCourt.get_wide_object(d[0].vdvid) for d in a]
    else:
        b = [EntityCourt.get_wide_object(d.vdvid) for d in a]
    # seen = set()
    # c = []
    # for d in b:
    #     t = tuple(d.items())
    #     if t not in seen:
    #         seen.add(t)
    #         c.append(d)

    resp.body = obj_to_json(b)
    resp.status = falcon.HTTP_200


def getCourtById(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    id = getIntPathParam('courtId', **request_handler_args)
    objects = EntityCourt.get().filter_by(vdvid=id).all()
    if len(objects) == 0:
        resp.status = falcon.HTTP_404
        return

    wide_info = EntityCourt.get_wide_object(id)

    res = []
    for _ in objects:
        obj_dict = _.to_dict()

        obj_dict.update(wide_info)
        res.append(obj_dict)

    resp.body = obj_to_json(res[0])
    resp.status = falcon.HTTP_200


def getCourtByLandlordId(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    id = getIntPathParam('landlordId', **request_handler_args)
    objects = EntityCourt.get().filter_by(ownerid=id).all()

    if len(objects) == 0:
        resp.status = falcon.HTTP_404
        return

    ispublished = req.params['ispublished']

    # wide_info = EntityCourt.get_wide_object(id)

    res = []
    for _ in objects:
        obj_dict = _.to_dict()
        courts = EntityCourt.get().filter_by(vdvid=_.vdvid)
        if ispublished == 'published':
            courts = courts.filter_by(ispublished=True)
        if ispublished == 'notpublished':
            courts = courts.filter_by(ispublished=False)
        courts = courts.all()
        if len(courts) > 0:
            obj_dict.update(EntityCourt.get_wide_object(_.vdvid))
            res.append(obj_dict)

    resp.body = obj_to_json(res)
    resp.status = falcon.HTTP_200


def getCourtByLocationId(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    PROPNAME_MAPPING = EntityProp.map_name_id()

    id = getIntPathParam('locationId', **request_handler_args)
    locations = PropLocation.get_objects(id, PROPNAME_MAPPING['location'])
    if len(locations) == 0:
        resp.status = falcon.HTTP_404
        return
    objects = EntityCourt.get().filter(EntityCourt.vdvid.in_(locations)).all()

    phone = req.context['phone']

    res = []
    for _ in objects:
        obj_dict = _.to_dict()

        obj_dict.update(EntityCourt.get_wide_object(_.vdvid))
        res.append(obj_dict)

    resp.body = obj_to_json(res)
    resp.status = falcon.HTTP_200


def easyCreateCourt(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    e_mail = req.context['phone']
    ownerid = EntityAccount.get_id_from_email(e_mail)

    media = []
    for _ in sorted(req.params.keys()):
        if _.startswith('Photo'):
            data = req.get_param(_)

            resolver = MediaResolverFactory.produce('image', data.file.read())
            resolver.Resolve()

            media.append(EntityMedia(ownerid, 'image', resolver.url, name='', desc='').add())

    equipment = []
    for _ in sorted(req.params.keys()):
        if _.startswith('EqPhoto'):
            name = req.get_param(_.replace('Photo', 'Name'))
            desc = req.get_param(_.replace('Photo', 'Desc'))
            data = req.get_param(_)

            resolver = MediaResolverFactory.produce('equipment', data.file.read())
            resolver.Resolve()

            equipment.append({
                'name': name,
                'desc': desc,
                'media': EntityMedia(ownerid, 'equipment', resolver.url, name=name, desc=desc).add()
            })

    if 'LocationName' in req.params.keys() and 'Latitude' in req.params.keys() and 'Longitude' in req.params.keys():
        location = EntityLocation(req.get_param('LocationName'),
                                  req.get_param('Latitude'),
                                  req.get_param('Longitude')).add()

    params = {}

    params['ownerid'] = ownerid
    params['name'] = req.get_param('Name')
    params['desc'] = req.get_param('Desc')
    params['prop'] = {}
    params['prop']['media'] = media
    params['prop']['equipment'] = equipment
    params['prop']['location'] = location

    id = EntityCourt.add_from_json(params)

    if id:
        objects = EntityCourt.get().filter_by(vdvid=id).all()

        resp.body = obj_to_json(objects[0].to_dict())
        resp.status = falcon.HTTP_200


def createCourt(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    try:
        e_mail = req.context['phone']
    except:
        resp.status = falcon.HTTP_401
    try:
        params = json.loads(req.stream.read().decode('utf-8'))
        params['ispublished'] = False
        name = params.get('name')
        courts_with_same_name = EntityCourt.get().filter_by(name=name).all()
        if len(courts_with_same_name) != 0:
            resp.status = falcon.HTTP_412
            return
        id = EntityCourt.add_from_json(params)
    except Exception as e:
        logger.info(e)
        resp.status = falcon.HTTP_405
        return
    if id:
        objects = EntityCourt.get().filter_by(vdvid=id).all()

        resp.body = obj_to_json(objects[0].to_dict())
        resp.status = falcon.HTTP_200
        return
    resp.status = falcon.HTTP_405


def updateCourt(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    try:
        params = json.loads(req.stream.read().decode('utf-8'))
        id = EntityCourt.update_from_json(params)
        if id == -1:
            resp.status = falcon.HTTP_404
            return
        if id:
            objects = EntityCourt.get().filter_by(vdvid=id).all()

            resp.body = obj_to_json(EntityCourt.get_wide_object(objects[0].vdvid))
            resp.status = falcon.HTTP_200
            return
    except ValueError:
        resp.status = falcon.HTTP_405
        return

    resp.status = falcon.HTTP_501


def deleteCourt(**request_handler_args):
    resp = request_handler_args['resp']

    id = getIntPathParam('courtId', **request_handler_args)

    if id is not None:
        try:
            EntityCourt.delete_wide_object(id)
        except FileNotFoundError:
            resp.status = falcon.HTTP_405
            return

        try:
            EntityCourt.delete(id)
        except FileNotFoundError:
            resp.status = falcon.HTTP_404
            return

        object = EntityCourt.get().filter_by(vdvid=id).all()
        if not len(object):
            resp.status = falcon.HTTP_200
            return

    resp.status = falcon.HTTP_400


def confirmCourtById(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    id = getIntPathParam("courtId", **request_handler_args)

    try:
        id = EntityCourt.confirm(id)
        if id == -1:
            resp.status = falcon.HTTP_404
            return
        if id:
            objects = EntityCourt.get().filter_by(vdvid=id).all()

            #resp.body = obj_to_json(objects[0].to_dict())
            resp.status = falcon.HTTP_200
            return
    except ValueError:
        resp.status = falcon.HTTP_405
        return

    resp.status = falcon.HTTP_501


def declineCourtById(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    id = getIntPathParam("courtId", **request_handler_args)

    try:
        id = EntityCourt.confirm(id, isconfirmed=False)
        if id == -1:
            resp.status = falcon.HTTP_404
            return
        if id:
            objects = EntityCourt.get().filter_by(vdvid=id).all()

            #resp.body = obj_to_json(objects[0].to_dict())
            resp.status = falcon.HTTP_200
            return
    except ValueError:
        resp.status = falcon.HTTP_405
        return

    resp.status = falcon.HTTP_501


def getTimesForDate(**request_handler_args):
    PROPNAME_MAPPING = EntityProp.map_name_id()

    def create_time(o):
        return {'time': o[0], 'state': o[1]}

    req = request_handler_args['req']
    resp = request_handler_args['resp']

    courtid = req.params['courtid']
    date = req.params['date']

    courts = EntityCourt.get().filter_by(vdvid=courtid).all()
    if not courts:
        resp.status = falcon.HTTP_404
        return

    joined = PropCourtTime.get_object_property(courts[0].vdvid, PROPNAME_MAPPING['courtTime'])
    result = []
    court_times = EntityTime.get().filter(EntityTime.vdvid.in_(joined), cast(EntityTime.time, Date) == date)

    # TODO: rewrite SQL requests

    with DBConnection() as session:
        # get requests for current user to this court
        requestsid = [x.vdvid for x in EntityRequest.get().filter_by(accountid=int(req.context['accountid']), iscanceled=False).filter_by(
            courtid=courtid).all()]
        # get court times
        court_times_id = [x.vdvid for x in court_times.all()]
        # get court times that stands in requestsid and have same court_time
        pending_time_ids = list(set([x.value for x in session.db.query(PropRequestTime).filter(
            PropRequestTime.vdvid.in_(requestsid)).filter(PropRequestTime.value.in_(court_times_id)).all()]))
        pending_times = court_times.filter(EntityTime.vdvid.in_(pending_time_ids)).all()
        for _c in pending_times:
            result.append((str(_c.time), 'pending'))
        free_times = court_times.filter(EntityTime.vdvid.notin_(pending_time_ids)).all()
        for _c in free_times:
            result.append((str(_c.time), 'free'))
    for _a in EntityRequest.get().filter_by(courtid=courts[0].vdvid, iscanceled=False).all():
        joined = PropRequestTime.get_object_property(_a.vdvid, PROPNAME_MAPPING['requestTime'])
        free = EntityTime.get().filter(EntityTime.vdvid.in_(joined), cast(EntityTime.time, Date) == date).all()

        for _ in free:
            if _a.accountid == int(req.context['accountid']):
                result.append((str(_.time), 'rented' if _a.isconfirmed else 'pending'))
            else:
                if _a.isconfirmed:
                    result.append((str(_.time), 'rented'))

    resp.body = obj_to_json([create_time(o) for o in list(set(result))])
    resp.status = falcon.HTTP_200


def createCourtTimesOnDate(**request_handler_args):
    PROPNAME_MAPPING = EntityProp.map_name_id()

    req = request_handler_args['req']
    resp = request_handler_args['resp']

    courtid = req.params['courtid']
    #params = req.params['times']
    params = json.loads(req.stream.read().decode('utf-8'))

    with DBConnection() as session:
        create_times(session, courtid, PROPNAME_MAPPING['courtTime'], params['times'], 0)

    resp.status = falcon.HTTP_200


def updateCourtTimesOnDate(**request_handler_args):
    PROPNAME_MAPPING = EntityProp.map_name_id()

    req = request_handler_args['req']
    resp = request_handler_args['resp']

    courtid = req.params['courtid']
    params = json.loads(req.stream.read().decode('utf-8'))

    with DBConnection() as session:
        update_times(session, courtid, PROPNAME_MAPPING['courtTime'], params['times'], 0)

    resp.status = falcon.HTTP_200


def createAccount(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    try:
        data = req.stream.read().decode('utf-8')
        params = json.loads(data)
        id = EntityAccount.get().filter_by(phone=params["phone"]).all()
        if id:
            resp.status = falcon.HTTP_412
            resp.body = obj_to_json(id[0].vdvid)
            return
        id = EntityAccount.add_from_json(params)
        if id:
            objects = EntityAccount.get().filter_by(vdvid=id).all()

            resp.body = obj_to_json(objects[0].to_dict())
            resp.status = falcon.HTTP_200
            return
    except (ValueError, TypeError):
        logger.error("Invalid JSON was sent to request handler, can't get param: 'phone'")
        resp.status = falcon.HTTP_405
        return

    resp.status = falcon.HTTP_501


def createLandlord(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    try:
        data = req.stream.read().decode('utf-8')
        params = json.loads(data)
        if EntityLandlord.get().filter_by(accountid=params["accountid"]).all():
            resp.status = falcon.HTTP_412
            return
        id = EntityLandlord.add_from_json(params)
        if id:
            objects = EntityLandlord.get().filter_by(vdvid=id).all()

            resp.body = obj_to_json(objects[0].to_dict())
            resp.status = falcon.HTTP_200
            return
    except (ValueError, TypeError):
        resp.status = falcon.HTTP_405
        return

    resp.status = falcon.HTTP_501


def updateLandlord(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    try:
        params = json.loads(req.stream.read().decode('utf-8'))
        id = EntityLandlord.update_from_json(params)
        if id == -1:
            resp.status = falcon.HTTP_404
            return
        if id:
            objects = EntityLandlord.get().filter_by(vdvid=id).all()

            resp.body = obj_to_json(objects[0].to_dict())
            resp.status = falcon.HTTP_200
            return
    except ValueError:
        resp.status = falcon.HTTP_405
        return

    resp.status = falcon.HTTP_501


def getLandlord(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    id = getIntPathParam("landlordId", **request_handler_args)
    objects = EntityLandlord.get().filter_by(vdvid=id).all()

    if len(objects) == 0:
        resp.status = falcon.HTTP_404
        return

    resp.body = obj_to_json(objects[0].to_dict())
    resp.status = falcon.HTTP_200


def deleteLandlord(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    id = getIntPathParam("landlordId", **request_handler_args)
    objects = EntityLandlord.get().filter_by(vdvid=id).all()

    if len(objects) == 0:
        resp.status = falcon.HTTP_404
        return
    for o in objects:
        EntityLandlord.delete(o.vdvid)
    resp.status = falcon.HTTP_200


def createSimpleuser(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    try:
        data = req.stream.read().decode('utf-8')
        params = json.loads(data)
        if EntitySimpleuser.get().filter_by(accountid=params["accountid"]).all():
            resp.status = falcon.HTTP_412
            return
        id = EntitySimpleuser.add_from_json(params)
        if id:
            objects = EntitySimpleuser.get().filter_by(vdvid=id).all()

            resp.body = obj_to_json(objects[0].to_dict())
            resp.status = falcon.HTTP_200
            return
    except (ValueError, TypeError):
        resp.status = falcon.HTTP_405
        return

    resp.status = falcon.HTTP_501


def updateSimpleuser(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    try:
        params = json.loads(req.stream.read().decode('utf-8'))
        id = EntitySimpleuser.update_from_json(params)
        if id == -1:
            resp.status = falcon.HTTP_404
            return
        if id:
            objects = EntitySimpleuser.get().filter_by(vdvid=id).all()

            resp.body = obj_to_json(objects[0].to_dict())
            resp.status = falcon.HTTP_200
            return
    except ValueError:
        resp.status = falcon.HTTP_405
        return

    resp.status = falcon.HTTP_501


def getSimpleuser(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    id = getIntPathParam("simpleuserId", **request_handler_args)
    objects = EntitySimpleuser.get().filter_by(vdvid=id).all()

    if len(objects) == 0:
        resp.status = falcon.HTTP_404
        return

    resp.body = obj_to_json(objects[0].to_dict())
    resp.status = falcon.HTTP_200


def deleteSimpleuser(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    id = getIntPathParam("simpleuserId", **request_handler_args)
    objects = EntitySimpleuser.get().filter_by(vdvid=id).all()

    if len(objects) == 0:
        resp.status = falcon.HTTP_404
        return
    for o in objects:
        EntitySimpleuser.delete(o.vdvid)
    resp.status = falcon.HTTP_200


def confirmRules(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    phone = req.context['phone']
    id = EntityAccount.get_id_from_phone(phone)

    specialuser = req.params['specialuser']

    if specialuser == 'landlord':
        users = EntityLandlord.get().filter_by(accountid=id).all()
        if len(users) == 0:
            resp.status = falcon.HTTP_404
            return
        object = users[0]
        EntityLandlord.confirm_rules(object.vdvid)

    if specialuser == 'simpleuser':
        users = EntitySimpleuser.get().filter_by(accountid=id).all()
        if len(users) == 0:
            resp.status = falcon.HTTP_404
            return
        object = users[0]
        EntitySimpleuser.confirm_rules(object.vdvid)

    resp.status = falcon.HTTP_200


def updateUser(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    try:
        params = json.loads(req.stream.read().decode('utf-8'))
        id = EntityAccount.update_from_json(params)
        if id == -1:
            resp.status = falcon.HTTP_404
            return
        if id:
            objects = EntityAccount.get().filter_by(vdvid=id).all()

            resp.body = obj_to_json(objects[0].to_dict())
            resp.status = falcon.HTTP_200
            return
    except (ValueError, TypeError):
        resp.status = falcon.HTTP_405
        return

    resp.status = falcon.HTTP_501


def getAllUsers(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    objects = EntityAccount.get().all()

    resp.body = obj_to_json([o.to_dict() for o in objects])
    resp.status = falcon.HTTP_200


def getUserById(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    id = getIntPathParam("userId", **request_handler_args)
    objects = EntityAccount.get().filter_by(vdvid=id).all()

    if len(objects) == 0:
        resp.status = falcon.HTTP_404
        return

    res = []
    for _ in objects:
        obj_dict = _.to_dict(['vdvid', 'name', 'phone', 'mediaid'])

        landlords = EntityLandlord.get().filter_by(accountid=_.vdvid).all()
        if len(landlords) > 0:
            obj_dict['landlord'] = EntityLandlord.get_wide_object(landlords[0].vdvid)
        simpleusers = EntitySimpleuser.get().filter_by(accountid=_.vdvid).all()
        if len(simpleusers) > 0:
            obj_dict['simpleuser'] = EntitySimpleuser.get_wide_object(simpleusers[0].vdvid)

        res.append(obj_dict)

    resp.body = obj_to_json(res[0])
    resp.status = falcon.HTTP_200

def getUserByPhone(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    if 'phone' in req.params:
        phone = req.params['phone']
    else:
        resp.status = falcon.HTTP_407
        return

    objects = EntityAccount.get().filter_by(phone=phone).all()

    if len(objects) == 0:
        resp.status = falcon.HTTP_404
        return

    res = []
    for _ in objects:
        obj_dict = _.to_dict(['vdvid', 'name', 'phone', 'mediaid'])

        landlords = EntityLandlord.get().filter_by(accountid=_.vdvid).all()
        if len(landlords) > 0:
            obj_dict['landlord'] = EntityLandlord.get_wide_object(landlords[0].vdvid)
        simpleusers = EntitySimpleuser.get().filter_by(accountid=_.vdvid).all()
        if len(simpleusers) > 0:
            obj_dict['simpleuser'] = EntitySimpleuser.get_wide_object(simpleusers[0].vdvid)

        res.append(obj_dict)

    resp.body = obj_to_json(res[0])
    resp.status = falcon.HTTP_200


def getMyUser(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    phone = req.context['phone']
    id = EntityAccount.get_id_from_phone(phone)


    objects = EntityAccount.get().filter_by(vdvid=id).all()

    res = []
    for _ in objects:
        obj_dict = _.to_dict(['vdvid', 'name', 'phone', 'mediaid'])

        landlords = EntityLandlord.get().filter_by(accountid=_.vdvid).all()
        if len(landlords) > 0:
            obj_dict['landlord'] = EntityLandlord.get_wide_object(landlords[0].vdvid)
        simpleusers = EntitySimpleuser.get().filter_by(accountid=_.vdvid).all()
        if len(simpleusers) > 0:
            obj_dict['simpleuser'] = EntitySimpleuser.get_wide_object(simpleusers[0].vdvid)

        res.append(obj_dict)

    resp.body = obj_to_json(res[0])
    resp.status = falcon.HTTP_200

def getUserByLandlord(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    phone = req.context['phone']
    landlordid = getIntPathParam("landlordId", **request_handler_args)

    objects = EntityLandlord.get().filter_by(vdvid = landlordid).all()

    if len(objects) == 0:
        resp.status = falcon.HTTP_404
        return

    res = []
    for _ in objects:
        o = EntityAccount.get().filter_by(vdvid=_.accountid).all()[0]
        obj_dict = o.to_dict(['vdvid', 'name', 'phone', 'mediaid'])

        landlords = EntityLandlord.get().filter_by(accountid=_.accountid).all()
        if len(landlords) > 0:
            obj_dict['landlord'] = EntityLandlord.get_wide_object(landlords[0].vdvid)
        simpleusers = EntitySimpleuser.get().filter_by(accountid=_.accountid).all()
        if len(simpleusers) > 0:
            obj_dict['simpleuser'] = EntitySimpleuser.get_wide_object(simpleusers[0].vdvid)

        res.append(obj_dict)

    resp.body = obj_to_json(res[0])
    resp.status = falcon.HTTP_200

def deleteUser(**request_handler_args):
    resp = request_handler_args['resp']
    req = request_handler_args['req']

    # TODO: VERIFICATION IF ADMIN DELETE ANY
    # e_mail = req.context['phone']
    id_from_req = getIntPathParam("userId", **request_handler_args)
    id = id_from_req  # EntityAccount.get_id_from_email(e_mail)

    if id is not None:
        if id != id_from_req:
            resp.status = falcon.HTTP_400
            return

        vs = EntityValidation.get().filter_by(accountid=id).all()
        for v in vs:
            EntityValidation.delete(v.vdvid)

        try:
            EntityAccount.delete(id)
        except FileNotFoundError:
            resp.status = falcon.HTTP_404
            return

        try:
            EntityAccount.delete_wide_object(id)
        except FileNotFoundError:
            resp.status = falcon.HTTP_405
            return

        object = EntityAccount.get().filter_by(vdvid=id).all()
        if not len(object):
            resp.status = falcon.HTTP_200
            return

    resp.status = falcon.HTTP_400


def getPostAffectedUsers(post):
    res = [post['userid']]

    for _ in post['comment']:
        res.append(_['userid'])

    for _ in post['like']:
        res.append(_['userid'])

    return res


def getUserFollowingsPosts(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    e_mail = req.context['phone']
    id = EntityAccount.get_id_from_email(e_mail)

    followingIDs = [_.followingid for _ in EntityFollow.get()
        .filter_by(vdvid=id)
        .filter(EntityFollow.permit >= EntityAccount.PERMIT_ACCESSED).all()]

    posts = EntityPost.get().filter(EntityPost.userid.in_(followingIDs)) \
        .order_by(EntityPost.vdvid.desc()) \
        .limit(1000).all()

    post_section = []
    for _ in posts:
        obj_dict = _.to_dict(['vdvid', 'userid', 'description'])
        obj_dict.update(EntityPost.get_wide_object(_.vdvid))
        post_section.append(obj_dict)

    user_list = []
    for _ in post_section:
        user_list.extend(getPostAffectedUsers(_))

    users_affected_ids = list(set(user_list))
    users = EntityAccount.get().filter(EntityAccount.vdvid.in_(users_affected_ids))

    user_section = {}
    for _ in users:
        obj_dict = _.to_dict(['vdvid', 'name'])
        obj_dict.update(EntityAccount.get_wide_object(_.vdvid, ['private', 'avatar']))
        user_section.update({_.vdvid: obj_dict})

    resp.body = obj_to_json({'post': post_section, 'user': user_section})
    resp.status = falcon.HTTP_200


def userAddFollowing(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    e_mail = req.context['phone']
    id = EntityAccount.get_id_from_email(e_mail)

    id_to_follow = getIntPathParam("followingId", **request_handler_args)
    EntityFollow(id, id_to_follow, EntityAccount.PERMIT_NONE
    if EntityAccount.is_private(id_to_follow)
    else EntityAccount.PERMIT_ACCESSED, True).add()

    resp.status = falcon.HTTP_200


def userDelFollowing(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    e_mail = req.context['phone']
    id = EntityAccount.get_id_from_email(e_mail)

    id_to_follow = getIntPathParam("followingId", **request_handler_args)
    EntityFollow.smart_delete(id, id_to_follow)

    resp.status = falcon.HTTP_200


def getUserFollowingsList(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    id = getIntPathParam("userId", **request_handler_args)

    resp.status = falcon.HTTP_200
    resp.body = obj_to_json([_.to_dict() for _ in EntityFollow.get()
                            .filter_by(vdvid=id)
                            .filter(EntityFollow.permit >= EntityAccount.PERMIT_ACCESSED).all()])


def getUserFollowersList(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    id = getIntPathParam("userId", **request_handler_args)

    resp.status = falcon.HTTP_200
    resp.body = obj_to_json([_.to_dict() for _ in EntityFollow.get()
                            .filter_by(followingid=id).all()])


def getUserFollowersRequestList(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    id = getIntPathParam("userId", **request_handler_args)

    resp.status = falcon.HTTP_200
    resp.body = obj_to_json([_.to_dict() for _ in EntityFollow.get()
                            .filter_by(followingid=id)
                            .filter(EntityFollow.permit == EntityAccount.PERMIT_NONE).all()])


def userResolveFollowerRequest(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    e_mail = req.context['phone']
    id = EntityAccount.get_id_from_email(e_mail)

    id_to_resolve = getIntPathParam('followerId', **request_handler_args)
    accept = req.params['accept']

    if not accept:
        EntityFollow.smart_delete(id_to_resolve, id)
    else:
        EntityFollow.update(id_to_resolve, id, EntityAccount.PERMIT_ACCESSED)

    resp.status = falcon.HTTP_200


def createMedia(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    e_mail = req.context['phone']
    ownerid = EntityAccount.get_id_from_email(e_mail)
    media_type = req.params['type']
    name = req.params['name'] if 'name' in req.params else ''
    desc = req.params['desc'] if 'desc' in req.params else ''

    results = []
    for key in (_ for _ in req._params.keys() if _.startswith('file')):
        data = req.get_param(key)
        try:
            resolver = MediaResolverFactory.produce(media_type, data.file.read())
            resolver.Resolve()

            # TODO:NO NULL HERE AS OWNER
            id = EntityMedia(ownerid, media_type, resolver.url, name=name, desc=desc).add()
            if id:
                results.append(id)
        except Exception as e:
            resp.status = falcon.HTTP_400
            resp.body = obj_to_json("Media uploading error\nException::\n" + str(e))
            return

    resp.body = obj_to_json(results[0])
    resp.status = falcon.HTTP_200


def getAllOwnerMedias(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    id = getIntPathParam('ownerId', **request_handler_args)

    if id is not None:
        objects = EntityMedia.get().filter_by(ownerid=id).all()
        resp.body = obj_to_json(objects[0].to_dict())
        resp.status = falcon.HTTP_200
        return

    resp.status = falcon.HTTP_500


def getMedia(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    id = getIntPathParam('mediaId', **request_handler_args)

    if id is not None:
        objects = EntityMedia.get().filter_by(vdvid=id).all()

        resp.body = obj_to_json(objects[0].to_dict())
        resp.status = falcon.HTTP_200
        return

    resp.status = falcon.HTTP_500


def deleteMedia(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    id = getIntPathParam('mediaId', **request_handler_args)

    if id:
        try:
            EntityMedia.delete(id)
        except FileNotFoundError:
            resp.status = falcon.HTTP_404
            return

        object = EntityMedia.get().filter_by(vdvid=id).all()
        if not len(object):
            resp.status = falcon.HTTP_200
            return

    resp.status = falcon.HTTP_500


def createLocation(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    try:
        params = json.loads(req.stream.read().decode('utf-8'))
        if 'name' in params:
            name = params.get('name')
        else:
            name = "location default"
        latitude = params.get('latitude')
        longitude = params.get('longitude')
    except ValueError:
        resp.status = falcon.HTTP_405
        return

    locations_with_same_name = EntityLocation.get().filter_by(name=name).all()
    if len(locations_with_same_name) != 0:
        resp.status = falcon.HTTP_412
        return

    if not name or not latitude or not longitude:
        resp.status = falcon.HTTP_405
        return

    id = EntityLocation(name, latitude, longitude).add()

    if id:
        objects = EntityLocation.get().filter_by(vdvid=id).all()

        resp.body = obj_to_json(objects[0].to_dict())
        resp.status = falcon.HTTP_200
        return

    resp.status = falcon.HTTP_500


def getLocationById(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    id = getIntPathParam('locId', **request_handler_args)

    if id is not None:
        objects = EntityLocation.get().filter_by(vdvid=id).all()

        resp.body = obj_to_json(objects[0].to_dict())
        resp.status = falcon.HTTP_200
        return

    resp.status = falcon.HTTP_500


def deleteLocation(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    id = getIntPathParam('locId', **request_handler_args)

    if id is not None:
        try:
            EntityLocation.delete(id)
        except FileNotFoundError:
            resp.status = falcon.HTTP_404
            return

        object = EntityLocation.get().filter_by(vdvid=id).all()
        if not len(object):
            resp.status = falcon.HTTP_200
            return

    resp.status = falcon.HTTP_400


def getAllLocations(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    objects = EntityLocation.get().all()  # PropLike.get_object_property(0, 0)#

    resp.body = obj_to_json([EntityLocation.get_wide_info(o.vdvid) for o in objects])
    resp.status = falcon.HTTP_200


def getLocationsWithFilter(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    PROPNAME_MAPPING = EntityProp.map_name_id()
    if 'sportid' in req.params:
        sportid = req.params['sportid']
    else:
        sportid = None
    if 'timeBegin' in req.params and 'timeEnd' in req.params:
        timeBegin = req.params['timeBegin']
        timeEnd = req.params['timeEnd']
    else:
        timeBegin = None
        timeEnd = None
    if 'date' in req.params:
        date = req.params['date']
    else:
        date = None
    if 'minPrice' in req.params:
        minPrice = req.params['minPrice']
    else:
        minPrice = -2
    if 'maxPrice' in req.params:
        maxPrice = req.params['maxPrice']
    else:
        maxPrice = 6000
    if 'equipmentid' in req.params:
        equipmentid = req.params['equipmentid']
    else:
        equipmentid = None

    courts = EntityCourt.get().filter_by(ispublished=True)

    if sportid:
        courts = courts.filter(EntityCourt.vdvid.in_(PropSport.get_objects(sportid, PROPNAME_MAPPING['sport'])))
    if equipmentid:
        courts = courts.filter(
            EntityCourt.vdvid.in_(PropEquipment.get_objects(equipmentid, PROPNAME_MAPPING['equipment'])))
    if date:
        free = [x.vdvid for x in EntityTime.get().filter(cast(EntityTime.time, Date) == date).distinct()]
        courts_times = [x.vdvid for x in
                        PropCourtTime.get().filter(PropCourtTime.value.in_(free)).distinct(PropCourtTime.vdvid)]
        courts = courts.filter(EntityCourt.vdvid.in_(courts_times))
    if timeBegin and timeEnd and date:
        time_format = '%Y-%m-%d %H:%M:%S%z'
        times = []
        timeBegin = datetime.datetime.strptime(date + ' ' + timeBegin + ':00', time_format)
        timeEnd = datetime.datetime.strptime(date + ' ' + timeEnd + ':00', time_format)
        t = timeBegin
        while t < timeEnd:
            times.append(t.strftime(time_format))
            t = t + datetime.timedelta(minutes=30)
        timesid = [_.vdvid for _ in EntityTime.get().filter(EntityTime.time.in_(times)).all()]
        courts = courts.filter(all(
            elem in PropCourtTime.get_object_property(EntityCourt.vdvid, PROPNAME_MAPPING['courtTime']) for elem in
            timesid))
    courts = courts.filter(EntityCourt.price.between(minPrice, maxPrice))

    locationsid = []

    for c in courts.all():
        locid = PropLocation.get_object_property(c.vdvid, PROPNAME_MAPPING['location'])
        if len(locid) > 0:
            locationsid.append(PropLocation.get_object_property(c.vdvid, PROPNAME_MAPPING['location'])[0])
    objects = EntityLocation.get().filter(
        EntityLocation.vdvid.in_(locationsid)).all()  # PropLike.get_object_property(0, 0)#

    resp.body = obj_to_json([EntityLocation.get_wide_info(o.vdvid) for o in objects])
    resp.status = falcon.HTTP_200


def getCourtsInArea(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']
    PROPNAME_MAPPING = EntityProp.map_name_id()
    ## Getting locations in area

    x = req.params['x']
    y = req.params['y']
    radius = req.params['radius']

    objects = EntityLocation.get().filter(distanceMath(EntityLocation.latitude, EntityLocation.longitude,
    float(x), float(y), func) < (float(radius))).all()  # PropLike.get_object_property(0, 0)#
    locations_id = []
    for o in objects:
        locations_id = locations_id + (PropLocation.get_objects(o.vdvid, PROPNAME_MAPPING['location']))
    locations_id = list(set(locations_id))

    ## Getting courts with filters


    if 'sportid' in req.params:
        sportid = req.params['sportid']
        sportid = sportid.split(',')
    else:
        sportid = None
    if 'timeBegin' in req.params and 'timeEnd' in req.params:
        timeBegin = req.params['timeBegin']
        timeEnd = req.params['timeEnd']
    else:
        timeBegin = None
        timeEnd = None
    if 'date' in req.params:
        date = req.params['date']
    else:
        date = None
    if 'minPrice' in req.params:
        minPrice = req.params['minPrice']
    else:
        minPrice = -2
    if 'maxPrice' in req.params:
        maxPrice = req.params['maxPrice']
    else:
        maxPrice = 6000
    if 'equipmentid' in req.params:
        equipmentid = req.params['equipmentid']
    else:
        equipmentid = None

    # GET ONLY PUBLISHED

    courts = EntityCourt.get()#.filter_by(ispublished=True)

    if sportid:
        courts = courts.filter(EntityCourt.vdvid.in_(PropSport.get_objects_multiple_value(sportid, PROPNAME_MAPPING['sport'])))
    if equipmentid:
        courts = courts.filter(
            EntityCourt.vdvid.in_(PropEquipment.get_objects(equipmentid, PROPNAME_MAPPING['equipment'])))
    if date:
        free = [x.vdvid for x in EntityTime.get().filter(cast(EntityTime.time, Date) == date).distinct()]
        courts_times = [x.vdvid for x in
                        PropCourtTime.get().filter(PropCourtTime.value.in_(free)).distinct(PropCourtTime.vdvid)]
        courts = courts.filter(EntityCourt.vdvid.in_(courts_times))
    if timeBegin and timeEnd and date:
        time_format = '%Y-%m-%d %H:%M:%S%z'
        times = []
        timeBegin = datetime.datetime.strptime(date + ' ' + timeBegin + ':00', time_format)
        timeEnd = datetime.datetime.strptime(date + ' ' + timeEnd + ':00', time_format)
        t = timeBegin
        while t < timeEnd:
            times.append(t.strftime(time_format))
            t = t + datetime.timedelta(minutes=30)
        timesid = [_.vdvid for _ in EntityTime.get().filter(EntityTime.time.in_(times)).all()]
        courts = courts.filter(EntityCourt.vdvid.in_(PropCourtTime.get_objects_multiple_value(timesid, PROPNAME_MAPPING['courtTime'])))
    courts = courts.filter(EntityCourt.price.between(minPrice, maxPrice))

    courts = courts.filter(EntityCourt.vdvid.in_(locations_id))

    ## Sortering

    phone = req.context['phone']
    my_id = EntityAccount.get_id_from_phone(phone)
    try:
        my_landlordid = EntityLandlord.get_id_from_accountid(my_id)
    except:
        resp.status = falcon.HTTP_407
        return

    filter = req.params['filter1']  # post_data['filter']

    sort_order = req.params['sortedby']

    with DBConnection() as session:
        if sort_order == 'popularity':
            objects = session.db.query(EntityCourt, func.count(EntityRequest.vdvid).label('total'))\
                .join(EntityRequest, EntityRequest.courtid == EntityCourt.vdvid)\
                .group_by(EntityCourt.vdvid, EntityRequest.vdvid)
        else:
            objects = courts

    if filter == 'all':
        objects = objects

    if filter == 'my':
        objects = objects.filter_by(ownerid=my_landlordid)

    if filter == 'notmy':
        objects = objects.filter(EntityCourt.ownerid != my_landlordid)

    filter = req.params['filter2']  # post_data['filter']

    if filter == 'drafts':
        objects = objects.filter_by(isdraft=True)

    if filter == 'published':
        objects = objects.filter_by(ispublished=True)

    if filter == 'notpublished':
        objects = objects.filter_by(ispublished=False)

    if not objects:
        resp.status = falcon.HTTP_408
        return

    if sort_order == 'price':
        objects = objects.order_by(desc(EntityCourt.price), EntityCourt.vdvid)
    if sort_order == 'popularity':
        objects = objects.distinct(EntityCourt.vdvid, 'total').order_by('total', EntityCourt.vdvid)

    a = objects.all()
    if sort_order == 'popularity':
        b = [EntityCourt.get_wide_object(d[0].vdvid) for d in a]
    else:
        b = [EntityCourt.get_wide_object(d.vdvid) for d in a]

    resp.body = obj_to_json(b)




def createTariff(**request_handler_args):  # TODO: implement it
    resp = request_handler_args['resp']
    req = request_handler_args['req']

    try:
        e_mail = req.context['phone']
    except:
        resp.status = falcon.HTTP_400

    params = json.loads(req.stream.read().decode('utf-8'))
    try:
        id = EntityTariff.add_from_json(params)
    except Exception as e:
        logger.info(e)
        resp.status = falcon.HTTP_412
        return
    if id:
        objects = EntityTariff.get().filter_by(vdvid=id).all()

        resp.body = obj_to_json(objects[0].to_dict())
        resp.status = falcon.HTTP_200
    resp.status = falcon.HTTP_200


def deleteTariff(**request_handler_args):  # TODO: implement it
    resp = request_handler_args['resp']

    id = getIntPathParam('tariffId', **request_handler_args)

    if id is not None:
        try:
            EntityTariff.delete(id)
        except FileNotFoundError:
            resp.status = falcon.HTTP_404
            return
        object = EntityTariff.get().filter_by(vdvid=id).all()
        if not len(object):
            resp.status = falcon.HTTP_200
            return

    resp.status = falcon.HTTP_400

def getAllTariffs(**request_handler_args):
    resp = request_handler_args['resp']

    objects = EntityTariff.get().all()

    resp.body = obj_to_json([o.to_dict() for o in objects])

    resp.status = falcon.HTTP_200

def sendkey(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    key = random.randint(10000, 99999)

    post_data = parse_qs(req.stream.read().decode('utf-8'))

    phone = post_data['phone'][0]
    if (phone != '79110001122'):
        accounts = EntityAccount.get().filter_by(phone=phone).all()
        if not accounts:
            resp.status = falcon.HTTP_411
            return
        accountid = accounts[0].vdvid

        validations = EntityValidation.get().filter_by(accountid=accountid).all()

        ts = time.time()
        curr_time = datetime.datetime.fromtimestamp(ts)

        if validations:
            for validation in validations:
                if validation.timesend.year != curr_time.year \
                        or validation.timesend.month != curr_time.month \
                        or validation.timesend.day != curr_time.day or validation.timesaday < 2:

                    data = {
                        'vdvid': validation.vdvid,
                        'code': key,
                        'timesADay': 1 if validation.timesend.year != curr_time.year \
                                            or validation.timesend.month != curr_time.month \
                                            or validation.timesend.day != curr_time.day else 2,
                        'timeSend': curr_time.strftime('%Y-%m-%d %H:%M')
                    }

                    EntityValidation.update(data=data)

                    sms_login = cfg['smsservice']['login']
                    sms_pswd = cfg['smsservice']['password']

                    data = {'login': sms_login,
                            'psw': sms_pswd,
                            'phones': phone,
                            'mes': str('GYMA:' + str(key))
                            }

                    r = requests.get('https://smsc.ru/sys/send.php', params=data)
                else:
                    resp.status = falcon.HTTP_412
                    return
        else:
            data = {
                'code': key,
                'timesADay': 1,
                'timeSend': curr_time.strftime('%Y-%m-%d %H:%M'),
                'accountid': accountid
            }
            EntityValidation.create(data=data)

            sms_login = cfg['smsservice']['login']
            sms_pswd = cfg['smsservice']['password']

            data = {'login': sms_login,
                    'psw': sms_pswd,
                    'phones': phone,
                    'mes': 'GYMA:' + str(key)
                    }
            r = requests.get('https://smsc.ru/sys/send.php', params=data)
            print(r.json)

    resp.status = falcon.HTTP_200


def validate(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    post_data = parse_qs(req.stream.read().decode('utf-8'))

    phone = post_data['phone'][0]
    key = post_data['key'][0]

    accounts = EntityAccount.get().filter_by(phone=phone).all()
    if not accounts:
        resp.status = falcon.HTTP_411
        return
    accountid = accounts[0].vdvid

    validations = EntityValidation.get().filter_by(accountid=accountid).all()

    if not validations:
        resp.status = falcon.HTTP_411
        return

    if validations:
        for validation in validations:
            if validation.code == int(key):
                payload = {
                    'phone': phone,
                    'exp': datetime.datetime.utcnow() + timedelta(seconds=JWT_EXP_TIME)
                }
                jwt_token = jwt.encode(payload, JWT_PUBLIC_KEY, JWT_SIGN_ALGORITHM)
                resp.body = jwt_token
                resp.status = falcon.HTTP_200
                return

    resp.status = falcon.HTTP_405
    return


def createHelp(**request_handler_args):  # TODO: implement it
    resp = request_handler_args['resp']
    req = request_handler_args['req']

    try:
        e_mail = req.context['phone']
    except:
        resp.status = falcon.HTTP_400

    params = json.loads(req.stream.read().decode('utf-8'))
    try:
        id = EntityHelp.add_from_json(params)
    except Exception as e:
        logger.info(e)
        resp.status = falcon.HTTP_412
        return
    if id:
        objects = EntityHelp.get().filter_by(vdvid=id).all()

        resp.body = obj_to_json(objects[0].to_dict())
        resp.status = falcon.HTTP_200
    resp.status = falcon.HTTP_200

def setDoneHelp(**request_handler_args):
    resp = request_handler_args['resp']
    id = getIntPathParam('helpId', **request_handler_args)
    EntityHelp.set_done(id)
    resp.status = falcon.HTTP_200

def createExtension(**request_handler_args):  # TODO: implement it
    resp = request_handler_args['resp']
    req = request_handler_args['req']

    try:
        phone = req.context['phone']
    except:
        resp.status = falcon.HTTP_400
    try:
        params = json.loads(req.stream.read().decode('utf-8'))
        id = EntityExtension.add_from_json(params)
    except Exception as e:
        logger.info(e)
        resp.status = falcon.HTTP_412
        return
    if id:
        objects = EntityExtension.get().filter_by(vdvid=id).all()

        resp.body = obj_to_json(objects[0].to_dict())
        resp.status = falcon.HTTP_200
    resp.status = falcon.HTTP_200

def updateExtension(**request_handler_args):  # TODO: implement it
    resp = request_handler_args['resp']
    req = request_handler_args['req']

    try:
        phone = req.context['phone']
    except:
        resp.status = falcon.HTTP_400

    params = json.loads(req.stream.read().decode('utf-8'))
    try:
        id = EntityExtension.update_from_json(params)
    except Exception as e:
        logger.info(e)
        resp.status = falcon.HTTP_412
        return
    if id:
        objects = EntityExtension.get().filter_by(vdvid=id).all()
        resp.body = obj_to_json(objects[0].to_dict())
        resp.status = falcon.HTTP_200
        return
    resp.status = falcon.HTTP_404

def confirmExtension(**request_handler_args):  # TODO: implement it
    resp = request_handler_args['resp']
    req = request_handler_args['req']
    id = getIntPathParam('extensionid', **request_handler_args)
    if('adminid' in req.params):
        adminid = req.params['adminid']
    else:
        resp.status = falcon.HTTP_407
        return
    EntityExtension.confirm(id, adminid)
    resp.status = falcon.HTTP_200


def getAllExtensions(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    one_day_earlier_datetime = get_curr_date() - timedelta(hours=24)
    is_one_day_passed_after_confirmation = cast(
        EntityExtension.confirmedtime, DateTime) > one_day_earlier_datetime

    extensions = EntityExtension.get().filter(or_(
            EntityExtension.isconfirmed == False,
            is_one_day_passed_after_confirmation == True,))\
        .order_by(EntityExtension.created).all()

    resp.body = obj_to_json([o.to_dict() for o in extensions])
    resp.status = falcon.HTTP_200


def getExtensionsByLandlordId(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    id = getIntPathParam('landlordId', **request_handler_args)

    if id is None:
        resp.status = falcon.HTTP_400
        return

    landlords = EntityLandlord.get().filter_by(vdvid=id).all()
    if len(landlords) == 0:
        resp.status = falcon.HTTP_404
        return

    with DBConnection() as session:
        extensions = session.db.query(EntityExtension)\
            .join(EntityCourt, EntityExtension.courtid == EntityCourt.vdvid)\
            .filter(EntityCourt.ownerid == id)
    isconfirmed = req.params['isconfirmed']

    # wide_info = EntityCourt.get_wide_object(id)

    if isconfirmed == 'confirmed':
        extensions = extensions.filter(
            EntityExtension.isconfirmed == "true"
        ).all()
    if isconfirmed == 'notconfirmed':
        extensions = extensions.filter(
            EntityExtension.isconfirmed == "False"
        ).all()

    resp.body = obj_to_json([o.to_dict() for o in extensions])
    resp.status = falcon.HTTP_200


def login(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    email = req.params.get('email')
    password = req.params.get('pass')

    passwordBase = EntityAccount.get_password_from_email(email)

    if password != passwordBase or password == None:
        resp.status = falcon.HTTP_405

    payload = {
        'user_id': EntityAccount.get_id_from_email(email),
        'e_mail': email,
        'exp': datetime.datetime.utcnow() + timedelta(seconds=JWT_EXP_TIME)
    }
    jwt_token = jwt.encode(payload, JWT_PUBLIC_KEY, JWT_SIGN_ALGORITHM)
    resp.body = obj_to_json({'token': jwt_token.decode('utf-8'),
                             'isAdmin': "false"})


operation_handlers = {
    'initDatabase': [initDatabase],
    'cleanupDatabase': [cleanupDatabase],
    'getVersion': [getVersion],
    'httpDefault': [httpDefault],

    # Auth
    'login': [login],
    'sendkey': [sendkey],
    'validate': [validate],

    # Request methods
    'createRequest': [createRequest],
    'getAllCourtRequestsByDate': [getAllCourtRequestsByDate],
    'getAllCourtRequest': [getAllCourtRequest],
    'getAllUserRequests': [getAllUserRequests],
    'getAllLandlordRequests': [getAllLandlordRequests],
    'getAllLandlordRequestsWithFilter': [getAllLandlordRequestsWithFilter],
    'deleteRequest': [deleteRequest],
    'confirmRequest': [confirmRequest],
    'declineRequest': [declineRequest],
    'comeRequest': [comeRequest],
    'cancelRequest': [cancelRequest],

    # Sport methods
    'createSport': [createSport],
    'deleteSport': [deleteSport],
    'getSports': [getSports],
    'getSportById': [getSportById],

    # Equipment methods
    'createEquipment': [createEquipment],
    'deleteEquipment': [deleteEquipment],
    'getEquipments': [getEquipments],
    'getEquipmentById': [getEquipmentById],

    # Court methods
    'getAllCourts': [getAllCourts],
    'getCourtById': [getCourtById],
    'getCourtByLandlordId': [getCourtByLandlordId],
    'getCourtByLocationId': [getCourtByLocationId],
    'createCourt': [createCourt],
    'updateCourt': [updateCourt],
    'deleteCourt': [deleteCourt],
    'easyCreateCourt': [easyCreateCourt],
    'getTimesForDate': [getTimesForDate],
    'createCourtTimesOnDate': [createCourtTimesOnDate],
    'updateCourtTimesOnDate': [updateCourtTimesOnDate],
    'confirmCourtById': [confirmCourtById],
    'declineCourtById': [declineCourtById],
    'getCourtsInArea': [getCourtsInArea],

    # User methods
    'createAccount': [createAccount],
    'updateUser': [updateUser],
    'getAllUsers': [getAllUsers],
    'getUser': [getUserById],
    'getUserByPhone': [getUserByPhone],
    'getMyUser': [getMyUser],
    'getUserByLandlord': [getUserByLandlord],
    'deleteUser': [deleteUser],
    'getUserFollowingsList': [getUserFollowingsList],
    'getUserFollowingsPosts': [getUserFollowingsPosts],
    'userAddFollowing': [userAddFollowing],
    'userDelFollowing': [userDelFollowing],
    'getUserFollowersList': [getUserFollowersList],
    'getUserFollowersRequestList': [getUserFollowersRequestList],
    'userResolveFollowerRequest': [userResolveFollowerRequest],
    'confirmRules': [confirmRules],

    # Special users methods
    'createLandlord': [createLandlord],
    'updateLandlord': [updateLandlord],
    'getLandlord': [getLandlord],
    'deleteLandlord': [deleteLandlord],
    'createSimpleUser': [createSimpleuser],
    'updateSimpleUser': [updateSimpleuser],
    'getSimpleUser': [getSimpleuser],
    'deleteSimpleUser': [deleteSimpleuser],

    # Media methods
    'createMedia': [createMedia],
    'getAllOwnerMedias': [getAllOwnerMedias],
    'getMedia': [getMedia],
    'deleteMedia': [deleteMedia],

    # Location methods
    'createLocation': [createLocation],
    'getLocationById': [getLocationById],
    'deleteLocation': [deleteLocation],
    'getAllLocations': [getAllLocations],
    'getLocationsWithFilter': [getLocationsWithFilter],


    # Help methods
    'createHelp': [createHelp],
    'setDoneHelp': [setDoneHelp],

    # Tariff methods
    'createTariff': [createTariff],
    'getAllTariffs': [getAllTariffs],
    'deleteTariff': [deleteTariff],

    # Extension methods
    'createExtension': [createExtension],
    'updateExtension': [updateExtension],
    'confirmExtension': [confirmExtension],
    'getAllExtensions': [getAllExtensions],
    'getExtensionsByLandlordId': [getExtensionsByLandlordId]
}




class CORS(object):
    def process_response(self, req, resp, resource):
        origin = req.get_header('Origin')
        if origin:
            resp.set_header('Access-Control-Allow-Origin', origin)
            resp.set_header('Access-Control-Max-Age', '100')
            resp.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS, PUT, DELETE')
            resp.set_header('Access-Control-Allow-Credentials', 'true')

            acrh = req.get_header('Access-Control-Request-Headers')
            if acrh:
                resp.set_header('Access-Control-Allow-Headers', acrh)

            # if req.method == 'OPTIONS':
            #    resp.set_header('Access-Control-Max-Age', '100')
            #    resp.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS, PUT, DELETE')
            #    acrh = req.get_header('Access-Control-Request-Headers')
            #    if acrh:
            #        resp.set_header('Access-Control-Allow-Headers', acrh)


class Auth1(object):
    def process_request(self, req, resp):
        req.context['phone'] = 'Savchuk@itsociety.su'


class Auth(object):
    def process_request(self, req, resp):
        if re.match('(/vdv/version|'
                    '/vdv/settings/urls|'
                    '/vdv/images|'
                    '/vdv/files|'
                    '/vdv/ui|'
                    '/vdv/swagger\.json|'
                    '/vdv/swagger-temp\.json|'
                    '/vdv/swagger-ui).*|'
                    '/vdv/sendkey|'
                    '/vdv/validate',
                    req.relative_uri):
            return

        if req.method == 'OPTIONS':
            return  # pre-flight requests don't require authentication

        error = None  # 'Authorization required.'

        jwt_token = req.headers.get('API-TOKEN')
        if jwt_token:
            try:
                payload = jwt.decode(jwt_token, JWT_PUBLIC_KEY,
                                     algorithms=[JWT_SIGN_ALGORITHM])
                id = EntityAccount.get_id_from_phone(phone=payload.get('phone'))
                if not id:
                    resp.status = falcon.HTTP_401
                    raise Exception("No user with given token's phone")
                req.context['phone'] = payload.get('phone')

                req.context['accountid'] = EntityAccount.get_id_from_phone(payload.get('phone'))
            except (jwt.DecodeError, jwt.ExpiredSignatureError):
                return falcon.HTTPUnauthorized(description=error,
                                               challenges=['Bearer realm=http://GOOOOGLE'])
            return

        if req.relative_uri.endswith('vdv/user') and req.method == 'POST':
            return  # passed access token is valid

        raise falcon.HTTPUnauthorized(description=error,
                                      challenges=['Bearer realm=http://GOOOOGLE'])


def getConfigFromLaunchArguments():
    args = utils.RegisterLaunchArguments()

    cfgPath = args.cfgpath
    profile = args.profile

    with open(cfgPath) as f:
        cfg = utils.GetAuthProfile(json.load(f), profile, args)

    return cfg


from . import __path__ as ROOT_PATH
SWAGGER_SPEC_PATH = (ROOT_PATH[0] + "/../swagger.json")

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


cfg = getConfigFromLaunchArguments()

if 'server_host' in cfg:
    with open(SWAGGER_SPEC_PATH) as f:
        swagger_json = json.loads(f.read(), object_pairs_hook=OrderedDict)

    server_host = cfg['server_host']
    swagger_json['host'] = server_host

    baseURL = '/vdv'
    if 'basePath' in swagger_json:
        baseURL = swagger_json['basePath']

    EntityBase.host = server_host + baseURL
    EntityBase.MediaCls = EntityMedia
    EntityBase.MediaPropCls = PropMedia


def getWSGIPortFromConfig(cfg=cfg):
    if "api_port" in cfg:
        return int(cfg["api_port"])
    return None


def configureDBConnection():
    DBConnection.configure(**cfg['vdv_db'])


def runWSGIApp():
    configureDBConnection()
    configureOIDC()

    general_executor = ftr.ThreadPoolExecutor(max_workers=20)

    wsgi_app = api = falcon.API(middleware=[CORS(), Auth(), MultipartMiddleware()])

    server = SpecServer(operation_handlers=operation_handlers)
    configureSwagger(server)
    api.add_sink(server, r'/')

    return wsgi_app


def configureOIDC(cfg=cfg):
    if 'oidc' in cfg:
        cfg_oidc = cfg['oidc']
        auth.Configure(**cfg_oidc)


def configureSwagger(server, swagger_json=swagger_json):
    swagger_temp_path = './swagger_temp.json'
    createSwaggerTemplate(swagger_temp_path)
    loadSpecSwagger(server, swagger_temp_path)


def createSwaggerTemplate(swagger_temp_path, swagger_json=swagger_json):
    json_string = json.dumps(swagger_json)
    with open(swagger_temp_path, 'wt') as f:
        f.write(json_string)


def loadSpecSwagger(server, swagger_temp_path):
    with open(swagger_temp_path) as f:
        server.load_spec_swagger(f.read())
