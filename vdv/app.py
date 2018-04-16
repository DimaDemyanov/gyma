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

from vdv.Entities.EntityCourt import EntityCourt
from vdv.Entities.EntityUser import EntityUser
from vdv.Entities.EntityLocation import EntityLocation
from vdv.Entities.EntityMedia import EntityMedia
from vdv.Entities.EntityPost import EntityPost
from vdv.Entities.EntityFollow import EntityFollow
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

    objects = EntityCourt.get().all()

    resp.body = obj_to_json([o.to_dict() for o in objects])
    resp.status = falcon.HTTP_200

def getCourtById(**request_handler_args):
    resp = request_handler_args['resp']

    id = getIntPathParam('courtId', **request_handler_args)
    objects = EntityCourt.get().filter_by(vdvid=id).all()

    wide_info = EntityCourt.get_wide_object(id)
    result_arr = [o.to_dict() for o in objects]
    for item in result_arr:
        item['prop'] = wide_info

    resp.body = obj_to_json(result_arr)
    resp.status = falcon.HTTP_200


def createCourt(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    try:
        e_mail = req.context['email']
        ownerid = EntityUser.get_id_from_email(e_mail)

        params = json.loads(req.stream.read().decode('utf-8'))
        params['ownerid'] = ownerid

        id = EntityCourt.add_from_json(params)

        if id:
            objects = EntityCourt.get().filter_by(vdvid=id).all()

            resp.body = obj_to_json([o.to_dict() for o in objects])
            resp.status = falcon.HTTP_200
            return
    except ValueError:
        resp.status = falcon.HTTP_405
        return

    resp.status = falcon.HTTP_405

    
def updateCourt(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

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
    

def createUser(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    try:
        params = json.loads(req.stream.read().decode('utf-8'))
        id = EntityUser.add_from_json(params)

        if id:
            objects = EntityUser.get().filter_by(vdvid=id).all()

            resp.body = obj_to_json([o.to_dict() for o in objects])
            resp.status = falcon.HTTP_200
            return
    except ValueError:
        resp.status = falcon.HTTP_405
        return

    resp.status = falcon.HTTP_501
    

def updateUser(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    try:
        params = json.loads(req.stream.read().decode('utf-8'))
        id = EntityUser.update_from_json(params)

        if id:
            objects = EntityUser.get().filter_by(vdvid=id).all()

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

    objects = EntityUser.get().all()

    resp.body = obj_to_json([o.to_dict() for o in objects])
    resp.status = falcon.HTTP_200
    

def getUserById(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    id = getIntPathParam("userId", **request_handler_args)
    objects = EntityUser.get().filter_by(vdvid=id).all()

    wide_info = EntityUser.get_wide_object(id)
    result_arr = [o.to_dict() for o in objects]
    for item in result_arr:
        item['prop'] = wide_info

    resp.body = obj_to_json(result_arr)
    resp.status = falcon.HTTP_200


def getMyUser(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    e_mail = req.context['email']
    ownerid = EntityUser.get_id_from_email(e_mail)

    objects = EntityUser.get().filter_by(vdvid=ownerid).all()

    resp.body = obj_to_json([_.to_dict() for _ in objects])
    resp.status = falcon.HTTP_200


def deleteUser(**request_handler_args):
    resp = request_handler_args['resp']
    req = request_handler_args['req']

    e_mail = req.context['email']
    id_from_req = getIntPathParam("userId", **request_handler_args)
    id = EntityUser.get_id_from_email(e_mail)

    if id is not None:
        if id != id_from_req:
            resp.status = falcon.HTTP_400
            return

        try:
            EntityUser.delete(id)
        except FileNotFoundError:
            resp.status = falcon.HTTP_404
            return

        try:
            EntityUser.delete_wide_object(id)
        except FileNotFoundError:
            resp.status = falcon.HTTP_405
            return

        object = EntityUser.get().filter_by(vdvid=id).all()
        if not len(object):
            resp.status = falcon.HTTP_200
            return

    resp.status = falcon.HTTP_400


def getUserFollowingsPosts(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    e_mail = req.context['email']
    id = EntityUser.get_id_from_email(e_mail)

    followingIDs = [_.followingid for _ in EntityFollow.get()
        .filter_by(vdvid=id)
        .filter(EntityFollow.permit >= EntityUser.PERMIT_ACCESSED).all()]

    res = []
    for _ in followingIDs:
        res.extend(EntityUser.get_wide_object(_)['post'])

    resp.body = obj_to_json(res)
    resp.status = falcon.HTTP_200


def userAddFollowing(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    e_mail = req.context['email']
    id = EntityUser.get_id_from_email(e_mail)

    id_to_follow = getIntPathParam("followingId", **request_handler_args)
    EntityFollow(id, id_to_follow, EntityUser.PERMIT_NONE
                                    if EntityUser.is_private(id_to_follow)
                                    else EntityUser.PERMIT_ACCESSED, True).add()

    resp.status = falcon.HTTP_200
    

def userDelFollowing(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    e_mail = req.context['email']
    id = EntityUser.get_id_from_email(e_mail)

    id_to_follow = getIntPathParam("followingId", **request_handler_args)
    EntityFollow.smart_delete(id, id_to_follow)

    resp.status = falcon.HTTP_200

def getUserFollowingsList(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    id = getIntPathParam("userId", **request_handler_args)

    resp.status = falcon.HTTP_200
    resp.body   = obj_to_json([_.to_dict() for _ in EntityFollow.get()
                      .filter_by(vdvid=id)
                      .filter(EntityFollow.permit >= EntityUser.PERMIT_ACCESSED).all()])


def getUserFollowersList(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    id = getIntPathParam("userId", **request_handler_args)

    resp.status = falcon.HTTP_200
    resp.body   = obj_to_json([_.to_dict() for _ in EntityFollow.get()
                            .filter_by(followingid=id).all()])
    

def getUserFollowersRequestList(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    id = getIntPathParam("userId", **request_handler_args)

    resp.status = falcon.HTTP_200
    resp.body   = obj_to_json([_.to_dict() for _ in EntityFollow.get()
                        .filter_by(followingid=id)
                        .filter(EntityFollow.permit == EntityUser.PERMIT_NONE).all()])
    

def userResolveFollowerRequest(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    e_mail = req.context['email']
    id = EntityUser.get_id_from_email(e_mail)

    id_to_resolve = getIntPathParam('followerId', **request_handler_args)
    accept = req.params['accept']

    if not accept:
        EntityFollow.smart_delete(id_to_resolve, id)
    else:
        EntityFollow.update(id_to_resolve, id, EntityUser.PERMIT_ACCESSED)

    resp.status = falcon.HTTP_200


def createMedia(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    e_mail = req.context['email']
    ownerid = EntityUser.get_id_from_email(e_mail)
    media_type = req.params['type']
    name = req.params['name'] if 'name' in req.params else ''
    desc = req.params['desc'] if 'desc' in req.params else ''

    results = []
    for key in (_ for _ in req._params.keys() if _.startswith('file')):
        data = req.get_param(key)
        try:
            resolver = MediaResolverFactory.produce(media_type, data.file.read())
            resolver.Resolve()

            #TODO:NO NULL HERE AS OWNER
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

    objects = EntityLocation.get().all()#PropLike.get_object_property(0, 0)#

    resp.body = obj_to_json([o.to_dict() for o in objects])
    resp.status = falcon.HTTP_200


def getPostById(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    id = getIntPathParam("postId", **request_handler_args)
    objects = EntityPost.get().filter_by(vdvid=id).all()

    wide_info = EntityPost.get_wide_object(id)
    result_arr = [o.to_dict() for o in objects]
    for item in result_arr:
        item['prop'] = wide_info

    resp.body = obj_to_json(result_arr)
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

    userId = EntityUser.get_id_from_email(req.context['email'])

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


def updatePost(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

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
    'getMyUser':              [getMyUser],
    'deleteUser':             [deleteUser],
    'getUserFollowingsList':        [getUserFollowingsList],
    'getUserFollowingsPosts':       [getUserFollowingsPosts],
    'userAddFollowing':             [userAddFollowing],
    'userDelFollowing':             [userDelFollowing],
    'getUserFollowersList':         [getUserFollowersList],
    'getUserFollowersRequestList':  [getUserFollowersRequestList],
    'userResolveFollowerRequest':   [userResolveFollowerRequest],

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

    #Post methods
    'getPostById':          [getPostById],
    'getAllPosts':          [getAllPosts],
    'createPost':           [createPost],
    'updatePost':           [updatePost],
    'deletePost':           [deletePost]
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
            error, res, email = auth.Validate(token, auth.PROVIDER.GOOGLE)
            if not error:
                req.context['email'] = email

                if not EntityUser.get_id_from_email(email) and not re.match('(/vdv/user).*', req.relative_uri):
                    raise falcon.HTTPUnavailableForLegalReasons(description=
                                                                "Requestor [%s] not existed as user yet" % email)

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

wsgi_app = api = falcon.API(middleware=[CORS(), Auth(), MultipartMiddleware()])

server = SpecServer(operation_handlers=operation_handlers)

if 'server_host' in cfg:
    with open('swagger.json') as f:
        swagger_json = json.loads(f.read(), object_pairs_hook=OrderedDict)

    server_host = cfg['server_host']
    swagger_json['host'] = server_host
    baseURL = '/marsrv'
    if 'basePath' in swagger_json:
        baseURL = swagger_json['basePath']

    json_string = json.dumps(swagger_json)

    with open('swagger_temp.json', 'wt') as f:
        f.write(json_string)

with open('swagger_temp.json') as f:
    server.load_spec_swagger(f.read())

api.add_sink(server, r'/')