import concurrent.futures as ftr
import json
import logging
import mimetypes
import os
import posixpath
import re
import time
from collections import OrderedDict

import falcon
from falcon_multipart.middleware import MultipartMiddleware

from vdv import utils
from vdv.auth import auth
from vdv.db import DBConnection
from vdv.serve_swagger import SpecServer

from vdv.Entities.EntityLocation import Location
from vdv.Entities.EntityMedia import Media
from vdv.MediaResolver.MediaResolverFactory import MediaResolverFactory

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

def getPathParam(name, **request_handler_args):
    # Falcon fails to strip the rest of the query from path param
    return request_handler_args['uri_fields'][name].partition('?')[0]

def getIntPathParam(name, **request_handler_args):
    s = getPathParam(name, **request_handler_args)
    try:
        return int(s)
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
        resp.body = json.dumps({"version": f.read()})

def initDatabase(**request_handler_args):
    resp = request_handler_args['resp']

    #with DBConnection() as db:
    #    db.init()

    resp.status = falcon.HTTP_501

def cleanupDatabase(**request_handler_args):
    resp = request_handler_args['resp']
    #with DBConnection() as db:
    #    db.Cleanup()

    resp.status = falcon.HTTP_501

def getAllCourts(**request_handler_args):
    resp = request_handler_args['resp']
    resp.status = falcon.HTTP_501
    resp.body = json.dumps("Not implemented")

def getCourtById(**request_handler_args):
    resp = request_handler_args['resp']

    id = getIntPathParam('CourtId', **request_handler_args)
    if id is None:
        resp.status = falcon.HTTP_400
        return

    #c = Court.GetCourtJSON(id)
    #if not c:
    #    resp.status = falcon.HTTP_404
    #    return

    resp.status = falcon.HTTP_501
    resp.body = json.dumps("Not implemented")

def createCourt(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    query_body = req.stream.read()
    boundary = '--' + req.env['CONTENT_TYPE'].partition('=')[2]

    data_parts = query_body.split(boundary.encode())

    results = []
    for key in req._params.keys():
        data = req.get_param(key)
        try:
            resolver = MediaResolverFactory.produce(data.type.split('/')[0], data.file.read())
            resolver.Resolve()

            # TODO:NO NULL HERE AS OWNER
            id = Media(0, resolver.type, resolver.url).add()
            if id:
                results.append(id)
        except Exception as e:
            resp.status = falcon.HTTP_400
            resp.body = json.dumps("Media uploading error\nException::\n" + str(e), 2, 2)

    resp.body = json.dumps(results, 2, 2)
    resp.status = falcon.HTTP_200

    
def updateCourt(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    try:
        params = json.loads(req.stream.read().decode('utf-8'))
    except ValueError:
        resp.status = falcon.HTTP_405
        return

    id = params.get('id')
    if id is None:
        resp.status = falcon.HTTP_400
        return

    #if not Court.GetCourt(id):
    #    resp.status = falcon.HTTP_404
    #    return

    #Court.UpdateCourt(params)
    resp.status = falcon.HTTP_501
    

def deleteCourt(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    id = getIntPathParam('CourtId', **request_handler_args)
    if id is None:
        resp.status = falcon.HTTP_400
        return

    hard = stringToBool(req.params.get('hard', 'false'))

    #c = Court.GetCourt(id)
    #if not c:
    #    resp.status = falcon.HTTP_404
    #    return

    #Court.RemoveCourt(id, hard)
    resp.status = falcon.HTTP_501
    

def createUser(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    resp.status = falcon.HTTP_501
    

def updateUser(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    resp.status = falcon.HTTP_501
    

def getAllUsers(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    resp.status = falcon.HTTP_501
    

def getUserById(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    resp.status = falcon.HTTP_501
    

def deleteUser(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    resp.status = falcon.HTTP_501
    

def getUserFollowingsList(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    resp.status = falcon.HTTP_501
    

def userAddFollowing(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    resp.status = falcon.HTTP_501
    

def userDelFollowing(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    resp.status = falcon.HTTP_501
    

def getUserFollowersList(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    resp.status = falcon.HTTP_501
    

def getUserFollowersRequestList(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    resp.status = falcon.HTTP_501
    

def userResolveFollowerRequest(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    resp.status = falcon.HTTP_501
    

def getUserCourts(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    resp.status = falcon.HTTP_501


def userAddCourt(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    resp.status = falcon.HTTP_501


def userDelCourt(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    resp.status = falcon.HTTP_501


def createMedia(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    query_body = req.stream.read()
    boundary = '--' + req.env['CONTENT_TYPE'].partition('=')[2]

    data_parts = query_body.split(boundary.encode())

    results = []
    for key in req._params.keys():
        data = req.get_param(key)
        try:
            resolver = MediaResolverFactory.produce(data.type.split('/')[0], data.file.read())
            resolver.Resolve()

            #TODO:NO NULL HERE AS OWNER
            id = Media(0, resolver.type, resolver.url).add()
            if id:
                results.append(id)
        except Exception as e:
            resp.status = falcon.HTTP_400
            resp.body = json.dumps("Media uploading error\nException::\n" + str(e), 2, 2)

    resp.body = json.dumps(results, 2, 2)
    resp.status = falcon.HTTP_200


def getAllOwnerMedias(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    id = getIntPathParam('ownerId', **request_handler_args)

    if id is not None:
        objects = Media.get().filter_by(ownerid=id).all()
        resp.body = json.dumps([o.to_dict() for o in objects], 2, 2)
        resp.status = falcon.HTTP_200
        return

    resp.status = falcon.HTTP_500


def getMedia(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    id = getIntPathParam('mediaId', **request_handler_args)

    if id is not None:
        objects = Media.get().filter_by(vdvid=id).all()

        resp.body = json.dumps([o.to_dict() for o in objects], 2, 2)
        resp.status = falcon.HTTP_200
        return

    resp.status = falcon.HTTP_500

def deleteMedia(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    id = getIntPathParam('mediaId', **request_handler_args)

    if id:
        try:
            Media.delete(id)
        except FileNotFoundError:
            resp.status = falcon.HTTP_404
            return

        object = Media.get().filter_by(vdvid=id).all()
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

    id = Location(name, latitude, longitude).add()

    if id:
        objects = Location.get().filter_by(vdvid=id).all()

        resp.body = json.dumps([o.to_dict() for o in objects], 2, 2)
        resp.status = falcon.HTTP_200
        return

    resp.status = falcon.HTTP_500


def getLocationById(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    id = getIntPathParam('locId', **request_handler_args)

    if id is not None:
        objects = Location.get().filter_by(vdvid=id).all()

        resp.body = json.dumps([o.to_dict() for o in objects], 2, 2)
        resp.status = falcon.HTTP_200
        return

    resp.status = falcon.HTTP_500


def deleteLocation(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    id = getIntPathParam('locId', **request_handler_args)

    if id is not None:
        try:
            Location.delete(id)
        except FileNotFoundError:
            resp.status = falcon.HTTP_404
            return

        object = Location.get().filter_by(vdvid=id).all()
        if not len(object):
            resp.status = falcon.HTTP_200
            return

    resp.status = falcon.HTTP_400


def getAllLocations(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    objects = Location.get().all()#PropLike.get_object_property(0, 0)#

    resp.body = json.dumps([o.to_dict() for o in objects], 2, 2)
    resp.status = falcon.HTTP_200

operation_handlers = {
    'initDatabase':    [initDatabase],
    'cleanupDatabase': [cleanupDatabase],
    'getVersion':      [getVersion],
    'httpDefault':     [httpDefault],

    #Court methods
    'getAllCourts':           [getAllCourts],
    'getCourtById':           [getCourtById],
    'createCourt':            [createCourt],
    'updateCourt':            [updateCourt],
    'deleteCourt':            [deleteCourt],

    #User methods
    'createUser':             [createUser],
    'updateUser':             [updateUser],
    'getAllUsers':            [getAllUsers],
    'getUser':                [getUserById],
    'deleteUser':             [deleteUser],
    'getUserFollowingsList':        [getUserFollowingsList],
    'userAddFollowing':             [userAddFollowing],
    'userDelFollowing':             [userDelFollowing],
    'getUserFollowersList':         [getUserFollowersList],
    'getUserFollowersRequestList':  [getUserFollowersRequestList],
    'userResolveFollowerRequest':   [userResolveFollowerRequest],
    'getUserCourts':                [getUserCourts],
    'userAddCourt':                 [userAddCourt],
    'userDelCourt':                 [userDelCourt],

    #Media methods
    'createMedia':            [createMedia],
    'getAllOwnerMedias':      [getAllOwnerMedias],
    'getMedia':               [getMedia],
    'deleteMedia':            [deleteMedia],

    #Location methods
    'createLocation':         [createLocation],
    'getLocationById':        [getLocationById],
    'deleteLocation':         [deleteLocation],
    'getAllLocations':        [getAllLocations],
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


class Auth(object):
    def process_request(self, req, resp):
        # skip authentication for version, UI and Swagger
        if re.match('(/vdv/version|'
                     '/vdv/settings/urls|'
                     '/vdv/images|'
                     '/vdv/ui|'
                     '/vdv/swagger\.json|'
                     '/vdv/swagger-temp\.json|'
                     '/vdv/swagger-ui).*', req.relative_uri):
            return

        if req.method == 'OPTIONS':
            return # pre-flight requests don't require authentication

        token = None
        if req.auth:
            token = req.auth.split(" ")[1].strip()
        else:
            token = req.params.get('access_token')

        error = 'Authorization required.'
        if token:
            error, res = auth.Validate(token, auth.PROVIDER.GOOGLE)
            if not error:
                return # passed access token is valid

        raise falcon.HTTPUnauthorized(description=error,
                                      challenges=['Bearer realm=http://GOOOOGLE'])


logging.getLogger().setLevel(logging.DEBUG)
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

wsgi_app = api = falcon.API(middleware=[CORS(), MultipartMiddleware()])

server = SpecServer(operation_handlers=operation_handlers)

if 'server_host' in cfg:
    with open('swagger.json') as f:
        swagger_json = json.loads(f.read(), object_pairs_hook=OrderedDict)

    swagger_json['host'] = cfg['server_host']
    baseURL = '/marsrv'
    if 'basePath' in swagger_json:
        baseURL = swagger_json['basePath']

    json_string = json.dumps(swagger_json, indent=2)

    with open('swagger_temp.json', 'wt') as f:
        f.write(json_string)

with open('swagger_temp.json') as f:
    server.load_spec_swagger(f.read())

api.add_sink(server, r'/')