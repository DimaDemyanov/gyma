import concurrent.futures as ftr
import json
import logging
import mimetypes
import os
import posixpath
import random
import re
from datetime import datetime, timedelta
from urllib.parse import parse_qs

import jwt
import requests
from sqlalchemy import and_, cast
from sqlalchemy import or_
import time
from collections import OrderedDict
from datetime import timedelta

import falcon
from falcon_multipart.middleware import MultipartMiddleware

from vdv import utils
from vdv.Entities.EntityEquipment import EntityEquipment
from vdv.Entities.EntityLandlord import EntityLandlord
from vdv.Entities.EntityRequest import EntityRequest
from vdv.Entities.EntitySport import EntitySport
from vdv.Entities.EntityTime import EntityTime
from vdv.Entities.EntityValidation import EntityValidation
from vdv.Prop.PropCourtTime import PropCourtTime
from vdv.Prop.PropRequestTime import PropRequestTime
from vdv.auth import auth
# from vdv.auth import JWT_SIGN_ALGORITHM
from vdv.db import DBConnection
from vdv.serve_swagger import SpecServer

from vdv.Entities.EntityBase import EntityBase
from vdv.Entities.EntityCourt import EntityCourt
from vdv.Entities.EntityAccount import EntityAccount
from vdv.Entities.EntityLocation import EntityLocation
from vdv.Entities.EntityMedia import EntityMedia
from vdv.Entities.EntityPost import EntityPost
from vdv.Entities.EntityFollow import EntityFollow
from vdv.Entities.EntityLike import EntityLike
from vdv.Entities.EntityComment import EntityComment

from vdv.search import *

from vdv.Prop.PropMedia import PropMedia
from vdv.Prop.PropLike import PropLike
from vdv.Prop.PropComment import PropComment

from vdv.MediaResolver.MediaResolverFactory import MediaResolverFactory

JWT_SIGN_ALGORITHM = 'HS256'
JWT_PUBLIC_KEY = 'secretterces123'
JWT_EXP_TIME = 24 * 3600


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
    resp = request_handler_args['resp']

    id = getIntPathParam('userId', **request_handler_args)

    objects = EntityRequest.get().filter_by(accountid=id).all()

    resp.body = obj_to_json([o.to_dict() for o in objects])
    resp.status = falcon.HTTP_200


def getAllCourtRequests(**request_handler_args):
    resp = request_handler_args['resp']

    id = getIntPathParam('courtId', **request_handler_args)

    objects = EntityRequest.get().filter_by(courtid=id).all()

    resp.body = obj_to_json([o.to_dict() for o in objects])
    resp.status = falcon.HTTP_200


def deleteRequest(**request_handler_args):
    resp = request_handler_args['resp']

    id = getIntPathParam('requestId', **request_handler_args)

    if id is not None:
        try:
            EntityRequest.delete(id)
        except FileNotFoundError:
            resp.status = falcon.HTTP_404
            return

        object = EntityRequest.get().filter_by(vdvid=id).all()
        if not len(object):
            resp.status = falcon.HTTP_200
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

def createSport(**request_handler_args):  # TODO: implement it
    resp = request_handler_args['resp']
    req = request_handler_args['req']

    try:
        e_mail = req.context['phone']
    except:
        resp.status = falcon.HTTP_400

    params = json.loads(req.stream.read().decode('utf-8'))
    try:
        id = EntitySport.add_from_json(params)
    except Exception as e:
        logger.info(e)
        resp.status = falcon.HTTP_412
        return
    if id:
        objects = EntitySport.get().filter_by(vdvid=id).all()

        resp.body = obj_to_json([o.to_dict() for o in objects])
        resp.status = falcon.HTTP_200
    resp.status = falcon.HTTP_200


def deleteSport(**request_handler_args):  # TODO: implement it
    resp = request_handler_args['resp']

    id = getIntPathParam('courtId', **request_handler_args)

    if id is not None:
        try:
            EntitySport.delete(id)
        except FileNotFoundError:
            resp.status = falcon.HTTP_404
            return

        try:
            EntitySport.delete_wide_object(id)
        except FileNotFoundError:
            resp.status = falcon.HTTP_405
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

    e_mail = req.context['phone']
    my_id = EntityAccount.get_id_from_email(e_mail)


    resp.body = obj_to_json([o.to_dict() for o in objects])
    resp.status = falcon.HTTP_200


def createEquipment(**request_handler_args):  # TODO: implement it
    resp = request_handler_args['resp']
    req = request_handler_args['req']

    try:
        e_mail = req.context['phone']
    except:
        resp.status = falcon.HTTP_400

    params = json.loads(req.stream.read().decode('utf-8'))
    try:
        id = EntityEquipment.add_from_json(params)
    except Exception as e:
        logger.info(e)
        resp.status = falcon.HTTP_412
        return
    if id:
        objects = EntityEquipment.get().filter_by(vdvid=id).all()

        resp.body = obj_to_json([o.to_dict() for o in objects])
        resp.status = falcon.HTTP_200
    resp.status = falcon.HTTP_200

def deleteEquipment(**request_handler_args):  # TODO: implement it
    resp = request_handler_args['resp']

    id = getIntPathParam('courtId', **request_handler_args)

    if id is not None:
        try:
            EntityEquipment.delete(id)
        except FileNotFoundError:
            resp.status = falcon.HTTP_404
            return

        try:
            EntityEquipment.delete_wide_object(id)
        except FileNotFoundError:
            resp.status = falcon.HTTP_405
            return

        object = EntityEquipment.get().filter_by(vdvid=id).all()
        if not len(object):
            resp.status = falcon.HTTP_200
            return

    resp.status = falcon.HTTP_400

def getEquipments(**request_handler_args):  # TODO: implement it
    resp = request_handler_args['resp']

    objects = EntityEquipment.get().all()

    resp.body = obj_to_json([o.to_dict() for o in objects])

    resp.status = falcon.HTTP_200

def getEquipmentById(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    id = getIntPathParam('equipmentId', **request_handler_args)
    objects = EntityEquipment.get().filter_by(vdvid=id).all()

    e_mail = req.context['phone']
    my_id = EntityAccount.get_id_from_email(e_mail)


    resp.body = obj_to_json([o.to_dict() for o in objects])
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
    # post_data = parse_qs(req.stream.read().decode('utf-8'))
    filter = req.params['filter'] # post_data['filter']
    if filter == 'all':
        objects = EntityCourt.get().all()
    if filter == 'my':
        objects = EntityCourt.get().filter_by(ownerid = my_landlordid).all()
    if filter == 'notmy':
        objects = EntityCourt.get().filter(EntityCourt.ownerid != my_landlordid).all()
    if not objects:
        resp.status = falcon.HTTP_408
        return
    resp.body = obj_to_json([EntityCourt.get_wide_object(o.vdvid) for o in objects])
    resp.status = falcon.HTTP_200


def getCourtById(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    id = getIntPathParam('courtId', **request_handler_args)
    objects = EntityCourt.get().filter_by(vdvid=id).all()

    e_mail = req.context['phone']
    my_id = EntityAccount.get_id_from_email(e_mail)

    wide_info = EntityCourt.get_wide_object(id)

    res = []
    for _ in objects:
        obj_dict = _.to_dict()

        obj_dict.update(wide_info)
        res.append(obj_dict)

    resp.body = obj_to_json(res)
    resp.status = falcon.HTTP_200

def getCourtByLandlordId(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    id = getIntPathParam('landlordId', **request_handler_args)
    objects = EntityCourt.get().filter_by(ownerid=id).all()

    phone = req.context['phone']

    #wide_info = EntityCourt.get_wide_object(id)

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

        resp.body = obj_to_json([o.to_dict() for o in objects])
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
        id = EntityCourt.add_from_json(params)
    except Exception as e:
        logger.info(e)
        resp.status = falcon.HTTP_405
        return
    if id:
        objects = EntityCourt.get().filter_by(vdvid=id).all()

        resp.body = obj_to_json([o.to_dict() for o in objects])
        resp.status = falcon.HTTP_200
        return
    resp.status = falcon.HTTP_406


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

            resp.body = obj_to_json([o.to_dict() for o in objects])
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
            EntityCourt.delete(id)
        except FileNotFoundError:
            resp.status = falcon.HTTP_404
            return

        try:
            EntityCourt.delete_wide_object(id)
        except FileNotFoundError:
            resp.status = falcon.HTTP_405
            return

        object = EntityCourt.get().filter_by(vdvid=id).all()
        if not len(object):
            resp.status = falcon.HTTP_200
            return

    resp.status = falcon.HTTP_400

def getTimesForDate(**request_handler_args):
    PROPNAME_MAPPING = EntityProp.map_name_id()

    req = request_handler_args['req']
    resp = request_handler_args['resp']

    courtid = req.params['courtid']
    date = req.params['date']

    objects = EntityCourt.get().filter_by(vdvid=courtid).all()
    if not objects:
        resp.status = falcon.HTTP_404
        return
    # with DBConnection() as session:
    #     joined = session.db.query(PropCourtTime).all()
    joined = PropCourtTime.get_object_property(objects[0].vdvid, PROPNAME_MAPPING['court_time'])
    result = []
    free = EntityTime.get().filter(EntityTime.vdvid.in_(joined), cast(EntityTime.time,Date) == date).all()

    for _ in free:
        result.append((_.vdvid, 'free'))
    for _a in EntityRequest.get().filter_by(courtid = objects[0].vdvid).all():
        joined = PropRequestTime.get_object_property(_a.vdvid, PROPNAME_MAPPING['request_time'])
        free = EntityTime.get().filter(EntityTime.vdvid.in_(joined), cast(EntityTime.time,Date) == date).all()

        for _ in free:
            result.append((_.vdvid, 'rented' if _a.isconfirmed else 'pending'))

    resp.body = obj_to_json(result)
    resp.status =falcon.HTTP_200

def createAccount(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    try:
        data = req.stream.read().decode('utf-8')
        params = json.loads(data)
        if EntityAccount.get().filter_by(phone=params["phone"]).all():
            resp.status = falcon.HTTP_412
            return
        id = EntityAccount.add_from_json(params)
        if id:
            objects = EntityAccount.get().filter_by(vdvid=id).all()

            resp.body = obj_to_json([o.to_dict() for o in objects])
            resp.status = falcon.HTTP_200
            return
    except ValueError:
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

            resp.body = obj_to_json([o.to_dict() for o in objects])
            resp.status = falcon.HTTP_200
            return
    except ValueError:
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

            resp.body = obj_to_json([o.to_dict() for o in objects])
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

    resp.body = obj_to_json([o.to_dict() for o in objects])
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
        EntityLandlord.delete(EntityLandlord, o.vdvid)
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

            resp.body = obj_to_json([o.to_dict() for o in objects])
            resp.status = falcon.HTTP_200
            return
    except ValueError:
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

    e_mail = req.context['phone']
    my_id = EntityAccount.get_id_from_email(e_mail)

    wide_info = EntityAccount.get_wide_object(id, ['private', 'avatar', 'post'])

    wide_info['post'].sort(key=lambda x: x['vdvid'], reverse=True)

    wide_info['is_me'] = my_id == id
    wide_info['followed'] = EntityFollow.get().filter_by(vdvid=my_id, followingid=id).count() > 0
    wide_info['following_amount'] = EntityFollow.get().filter_by(vdvid=id).count()
    wide_info['followers_amount'] = EntityFollow.get().filter_by(followingid=id).count()

    res = []
    for _ in objects:
        obj_dict = _.to_dict(['vdvid', 'name'])
        obj_dict.update(wide_info)
        res.append(obj_dict)

    resp.body = obj_to_json(res)
    resp.status = falcon.HTTP_200


def getMyUser(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    phone = req.context['phone']
    id = EntityAccount.get_id_from_phone(phone)

    objects = EntityAccount.get().filter_by(vdvid=id).all()


    # TODO: LIMIT the posts output counts with a paging
    #wide_info = EntityAccount.get_wide_object(id)

    # wide_info['post'].sort(key=lambda x: x['vdvid'], reverse=True)
    # followings = EntityFollow.get().filter_by(vdvid=id).all()
    # wide_info['is_me'] = True
    # wide_info['followed'] = False
    # wide_info['following_amount'] = len(followings)
    # wide_info['followers_amount'] = EntityFollow.get().filter_by(followingid=id).count()

    res = []
    for _ in objects:
        obj_dict = _.to_dict(['vdvid', 'name', 'phone', 'mediaid'])

        landlords = EntityLandlord.get().filter_by(accountid = _.vdvid)
        if landlords:
            obj_dict['landlord'] = EntityLandlord.get_wide_object(landlords[0].vdvid)
        #obj_dict.update(wide_info)

        res.append(obj_dict)

    resp.body = obj_to_json(res)
    resp.status = falcon.HTTP_200


def deleteUser(**request_handler_args):
    resp = request_handler_args['resp']
    req = request_handler_args['req']

    # TODO: VERIFICATION IF ADMIN DELETE ANY
    # e_mail = req.context['phone']
    id_from_req = getIntPathParam("userId", **request_handler_args)
    id = id_from_req#EntityAccount.get_id_from_email(e_mail)

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

    resp.body = obj_to_json(results)
    resp.status = falcon.HTTP_200


def getAllOwnerMedias(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    id = getIntPathParam('ownerId', **request_handler_args)

    if id is not None:
        objects = EntityMedia.get().filter_by(ownerid=id).all()
        resp.body = obj_to_json([o.to_dict() for o in objects])
        resp.status = falcon.HTTP_200
        return

    resp.status = falcon.HTTP_500


def getMedia(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    id = getIntPathParam('mediaId', **request_handler_args)

    if id is not None:
        objects = EntityMedia.get().filter_by(vdvid=id).all()

        resp.body = obj_to_json([o.to_dict() for o in objects])
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
        name = params.get('name')
        latitude = params.get('latitude')
        longitude = params.get('longitude')
    except ValueError:
        resp.status = falcon.HTTP_405
        return

    if not name:
        resp.status = falcon.HTTP_405
        return

    id = EntityLocation(name, latitude, longitude).add()

    if id:
        objects = EntityLocation.get().filter_by(vdvid=id).all()

        resp.body = obj_to_json([o.to_dict() for o in objects])
        resp.status = falcon.HTTP_200
        return

    resp.status = falcon.HTTP_500


def getLocationById(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    id = getIntPathParam('locId', **request_handler_args)

    if id is not None:
        objects = EntityLocation.get().filter_by(vdvid=id).all()

        resp.body = obj_to_json([o.to_dict() for o in objects])
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

    resp.body = obj_to_json([o.to_dict() for o in objects])
    resp.status = falcon.HTTP_200

def getLocationsInArea(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    x = req.params['x']
    y = req.params['y']
    radius = req.params['radius']

    objects = EntityLocation.get().filter( (EntityLocation.latitude - x)**2 + (EntityLocation.longitude - y)**2 < radius ** 2).all()  # PropLike.get_object_property(0, 0)#

    resp.body = obj_to_json([o.to_dict() for o in objects])
    resp.status = falcon.HTTP_200

def getPostById(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    id = getIntPathParam("postId", **request_handler_args)
    objects = EntityPost.get().filter_by(vdvid=id).all()

    wide_info = EntityPost.get_wide_object(id)

    post_section = []
    for _ in objects:
        obj_dict = _.to_dict()
        obj_dict.update(wide_info)
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


def getAllPosts(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    objects = EntityPost.get().all()

    resp.body = obj_to_json([o.to_dict() for o in objects])
    resp.status = falcon.HTTP_200


def createPost(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    userId = EntityAccount.get_id_from_email(req.context['phone'])

    if userId is None:
        resp.status = falcon.HTTP_405
        return

    params = json.loads(req.stream.read().decode('utf-8'))
    id = EntityPost.add_from_json(params, userId)

    if id:
        objects = EntityPost.get().filter_by(vdvid=id).all()

        resp.body = obj_to_json([o.to_dict() for o in objects])
        resp.status = falcon.HTTP_200
        return

    resp.status = falcon.HTTP_500


def updatePost(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    try:
        params = json.loads(req.stream.read().decode('utf-8'))
        id = EntityPost.update_from_json(params)

        if id:
            objects = EntityPost.get().filter_by(vdvid=id).all()

            resp.body = obj_to_json([o.to_dict() for o in objects])
            resp.status = falcon.HTTP_200
            return
    except ValueError:
        resp.status = falcon.HTTP_405
        return

    resp.status = falcon.HTTP_501


def deletePost(**request_handler_args):
    resp = request_handler_args['resp']

    id = getIntPathParam('postId', **request_handler_args)

    if id is not None:
        try:
            EntityPost.delete(id)
        except FileNotFoundError:
            resp.status = falcon.HTTP_404
            return

        try:
            EntityPost.delete_wide_object(id)
        except FileNotFoundError:
            resp.status = falcon.HTTP_405
            return

        object = EntityPost.get().filter_by(vdvid=id).all()
        if not len(object):
            resp.status = falcon.HTTP_200
            return

    resp.status = falcon.HTTP_400


def search(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    params = json.loads(req.stream.read().decode('utf-8'))

    _cls, ids = serach_objects(params)

    result = []
    for _ in _cls.get().filter(_cls.vdvid.in_(list(ids))).all():
        obj_dict = _.to_dict()
        if 'get_wide_object' in _cls.__dict__:
            obj_dict.update(
                _cls.get_wide_object(_.vdvid, ['private', 'avatar'] if _cls.__name__ == 'EntityAccount' else []))

        result.append(obj_dict)

    resp.body = obj_to_json(result)
    resp.status = falcon.HTTP_200


def getLikeById(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    id = getIntPathParam("likeId", **request_handler_args)
    objects = EntityLike.get().filter_by(vdvid=id).all()

    res = []
    for _ in objects:
        obj_dict = _.to_dict()
        res.append(obj_dict)

    resp.body = obj_to_json(res)
    resp.status = falcon.HTTP_200


def getAllLikes(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    objects = EntityLike.get().all()

    resp.body = obj_to_json([o.to_dict() for o in objects])
    resp.status = falcon.HTTP_200


def updateLike(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    try:
        params = json.loads(req.stream.read().decode('utf-8'))
        id = EntityLike.update_from_json(params)

        if id:
            objects = EntityLike.get().filter_by(vdvid=id).all()

            resp.body = obj_to_json([o.to_dict() for o in objects])
            resp.status = falcon.HTTP_200
            return
    except ValueError:
        resp.status = falcon.HTTP_405
        return

    resp.status = falcon.HTTP_501


def deleteLike(**request_handler_args):
    resp = request_handler_args['resp']

    id = getIntPathParam('likeId', **request_handler_args)

    if id is not None:
        try:
            EntityLike.delete(id)
            PropLike.delete_value(id, raise_exception=False)
        except FileNotFoundError:
            resp.status = falcon.HTTP_404
            return

        object = EntityLike.get().filter_by(vdvid=id).all()
        if not len(object):
            resp.status = falcon.HTTP_200
            return

    resp.status = falcon.HTTP_400


def createLike(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    params = json.loads(req.stream.read().decode('utf-8'))
    userId = EntityAccount.get_id_from_email(req.context['phone'])

    if userId is None:
        resp.status = falcon.HTTP_405
        return

    id = EntityLike.add_from_json(params, userId)

    if id:
        objects = EntityLike.get().filter_by(vdvid=id).all()

        resp.body = obj_to_json([o.to_dict() for o in objects])
        resp.status = falcon.HTTP_200
        return

    resp.status = falcon.HTTP_422


def getCommentById(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    id = getIntPathParam("commentId", **request_handler_args)
    objects = EntityComment.get().filter_by(vdvid=id).all()

    res = []
    for _ in objects:
        obj_dict = _.to_dict()
        res.append(obj_dict)

    resp.body = obj_to_json(res)
    resp.status = falcon.HTTP_200


def getAllComments(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    objects = EntityComment.get().all()

    resp.body = obj_to_json([o.to_dict() for o in objects])
    resp.status = falcon.HTTP_200


def updateComment(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    try:
        params = json.loads(req.stream.read().decode('utf-8'))
        id = EntityComment.update_from_json(params)

        if id:
            objects = EntityComment.get().filter_by(vdvid=id).all()

            resp.body = obj_to_json([o.to_dict() for o in objects])
            resp.status = falcon.HTTP_200
            return
    except ValueError:
        resp.status = falcon.HTTP_405
        return

    resp.status = falcon.HTTP_501


def deleteComment(**request_handler_args):
    resp = request_handler_args['resp']

    id = getIntPathParam('commentId', **request_handler_args)

    if id is not None:
        try:
            EntityComment.delete(id)
            PropComment.delete_value(id, raise_exception=False)
        except FileNotFoundError:
            resp.status = falcon.HTTP_404
            return

        object = EntityComment.get().filter_by(vdvid=id).all()
        if not len(object):
            resp.status = falcon.HTTP_200
            return

    resp.status = falcon.HTTP_400


def createComment(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    params = json.loads(req.stream.read().decode('utf-8'))
    userId = EntityAccount.get_id_from_email(req.context['phone'])

    if userId is None:
        resp.status = falcon.HTTP_405
        return

    id = EntityComment.add_from_json(params, userId)

    if id:
        objects = EntityComment.get().filter_by(vdvid=id).all()

        resp.body = obj_to_json([o.to_dict() for o in objects])
        resp.status = falcon.HTTP_200
        return

    resp.status = falcon.HTTP_500


def sendkey(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    key = random.randint(10000, 99999)

    post_data = parse_qs(req.stream.read().decode('utf-8'))


    phone = post_data['phone'][0]
    if (phone != '79110001122'):
        accounts = EntityAccount.get().filter_by(phone = phone).all()
        if not accounts:
            resp.status = falcon.HTTP_411
            return
        accountid = accounts[0].vdvid

        validations = EntityValidation.get().filter_by(accountid = accountid).all()

        ts = time.time()
        curr_time = datetime.datetime.fromtimestamp(ts)

        if validations:
            for validation in validations:
                if validation.time_send.year != curr_time.year  \
                    or validation.time_send.month != curr_time.month \
                    or validation.time_send.day != curr_time.day or validation.times_a_day < 2:

                    data = {
                       'id' : validation.vdvid,
                       'code' : key,
                       'times_a_day' : 1 if validation.time_send.year != curr_time.year  \
                    or validation.time_send.month != curr_time.month \
                    or validation.time_send.day != curr_time.day else 2,
                       'time_send' : curr_time.strftime('%Y-%m-%d %H:%M')
                    }



                    EntityValidation.update(data = data)

                    sms_login = cfg['smsservice']['login']
                    sms_pswd = cfg['smsservice']['password']

                    data = {'login': sms_login,
                            'psw': sms_pswd,
                            'phones': phone,
                            'mes': str('GYMA:' + str(key))
                            }

                    r = requests.get('https://smsc.ru/sys/send.php', params=data)
                else:
                    resp.status = falcon.HTTP_406
                    return
        else:
            data = {
                'code' : key,
                'times_a_day' : 1,
                'time_send' : curr_time.strftime('%Y-%m-%d %H:%M'),
                'accountid' : accountid
            }
            EntityValidation.create(data = data)

            sms_login = cfg['smsservice']['login']
            sms_pswd = cfg['smsservice']['password']

            data = {'login' : sms_login,
                    'psw' : sms_pswd,
                    'phones' : phone,
                    'mes' : 'GYMA key: ' + str(key)
                    }
            r = requests.get('https://smsc.ru/sys/send.php', params = data)
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
        resp.status = falcon.HTTP_407
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
    'getAllCourtRequests': [getAllCourtRequests],
    'getAllUserRequests': [getAllUserRequests],
    'deleteRequest': [deleteRequest],
    'confirmRequest': [confirmRequest],
    'declineRequest': [declineRequest],

    # Sport methods
    'createSport': [createSport],
    'deleteSport': [deleteSport],
    'getSports': [getSports],
    'getSportById': [getSportById],

    #Equipment methods
    'createEquipment': [createEquipment],
    'deleteEquipment': [deleteEquipment],
    'getEquipments': [getEquipments],
    'getEquipmentById': [getEquipmentById],

    # Court time methods
#    'createTime': [createTime],
#    'deleteTime': [deleteTime],

    # Court methods
    'getAllCourts': [getAllCourts],
    'getCourtById': [getCourtById],
    'getCourtByLandlordId': [getCourtByLandlordId],
    'createCourt': [createCourt],
    'updateCourt': [updateCourt],
    'deleteCourt': [deleteCourt],
    'easyCreateCourt': [easyCreateCourt],
    'getTimesForDate': [getTimesForDate],

    # User methods
    'createAccount': [createAccount],
    'updateUser': [updateUser],
    'getAllUsers': [getAllUsers],
    'getUser': [getUserById],
    'getMyUser': [getMyUser],
    'deleteUser': [deleteUser],
    'getUserFollowingsList': [getUserFollowingsList],
    'getUserFollowingsPosts': [getUserFollowingsPosts],
    'userAddFollowing': [userAddFollowing],
    'userDelFollowing': [userDelFollowing],
    'getUserFollowersList': [getUserFollowersList],
    'getUserFollowersRequestList': [getUserFollowersRequestList],
    'userResolveFollowerRequest': [userResolveFollowerRequest],

    # Special users methods
    'createLandlord': [createLandlord],
    'updateLandlord': [updateLandlord],
    'getLandlord': [getLandlord],
    'deleteLandlord': [deleteLandlord],

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
    'getLocationsInArea': [getLocationsInArea],

    # Post methods
    'getPostById': [getPostById],
    'getAllPosts': [getAllPosts],
    'createPost': [createPost],
    'updatePost': [updatePost],
    'deletePost': [deletePost],

    # Search methods
    'search': [search],

    # Like methods
    'getLikeById': [getLikeById],
    'getAllLikes': [getAllLikes],
    'updateLike': [updateLike],
    'deleteLike': [deleteLike],
    'createLike': [createLike],

    # Comment methods
    'getCommentById': [getCommentById],
    'getAllComments': [getAllComments],
    'updateComment': [updateComment],
    'deleteComment': [deleteComment],
    'createComment': [createComment]
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
                id = EntityAccount.get_id_from_phone(phone=payload.get("phone"))
                if not id:
                    raise Exception("No user with given token's phone")
                req.context['phone'] = payload.get('phone')
            except (jwt.DecodeError, jwt.ExpiredSignatureError):
                return falcon.HTTPUnauthorized(description=error,
                                               challenges=['Bearer realm=http://GOOOOGLE'])
            return

        if re.match('/vdv/user',
                    req.relative_uri):

            return  # passed access token is valid

        raise falcon.HTTPUnauthorized(description=error,
                                      challenges=['Bearer realm=http://GOOOOGLE'])


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
args = utils.RegisterLaunchArguments()

cfgPath = args.cfgpath
profile = args.profile
# configure
with open(cfgPath) as f:
    cfg = utils.GetAuthProfile(json.load(f), profile, args)
    DBConnection.configure(**cfg['vdv_db'])
    if 'oidc' in cfg:
        cfg_oidc = cfg['oidc']
        auth.Configure(**cfg_oidc)

general_executor = ftr.ThreadPoolExecutor(max_workers=20)

wsgi_app = api = falcon.API(middleware=[CORS(), Auth(), MultipartMiddleware()])
# Auth(),


server = SpecServer(operation_handlers=operation_handlers)

if 'server_host' in cfg:
    with open('swagger.json') as f:
        swagger_json = json.loads(f.read(), object_pairs_hook=OrderedDict)

    server_host = cfg['server_host']
    swagger_json['host'] = server_host

    baseURL = '/vdv'
    if 'basePath' in swagger_json:
        baseURL = swagger_json['basePath']

    json_string = json.dumps(swagger_json)

    with open('swagger_temp.json', 'wt') as f:
        f.write(json_string)

    EntityBase.host = server_host + baseURL
    EntityBase.MediaCls = EntityMedia
    EntityBase.MediaPropCls = PropMedia

with open('swagger_temp.json') as f:
    server.load_spec_swagger(f.read())

api.add_sink(server, r'/')
