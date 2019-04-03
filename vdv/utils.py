import os
import logging
import datetime
import argparse
import base64
import requests

from . import __path__ as ROOT_PATH
CONFIG_PATH = (ROOT_PATH[0] + "/../config.json")


def _DateToString(datetime):
    return datetime.ctime()

def batch(iterable, batch_size):
    b = []
    for item in iterable:
        b.append(item)
        if len(b) == batch_size:
            yield b
            b = []

    if len(b) > 0:
        yield b


# def ReadEntireLobs(entire_tuple):
#     result = []
#     for item in entire_tuple:
#         if isinstance(item, cx_Oracle.LOB):
#             item = item.read()
#         result.append(item)
#     return tuple(result)

def GetAuthProfile(jso, profile_name="local", args=None):
    ret = None
    if "profiles" in jso:
        for item in jso["profiles"]:
            if item["name"] == profile_name:
                ret = item
    elif "vdv_db" in jso and "oidc" in jso:
        ret = jso

    if not ret:
        raise ConnectionAbortedError('Config file format is wrong')

    if args:
        ret['vdv_db']['user']      = ret['vdv_db']['user']        if not args.dbuser else args.dbuser
        ret['vdv_db']['sid']       = ret['vdv_db']['sid']         if not args.dbsid  else args.dbsid
        ret['vdv_db']['password']  = ret['vdv_db']['password']    if not args.dbpswd else args.dbpswd
        ret['vdv_db']['host']      = ret['vdv_db']['host']        if not args.dbhost else args.dbhost
        ret['vdv_db']['port']      = ret['vdv_db']['port']        if not args.dbport else args.dbport

    return ret

def RegisterLaunchArguments():
    parser = argparse.ArgumentParser(description='Serve the vdv server')
    parser.add_argument('--profile', help='clarify the profile in config.json to use', default='local_on_dev')
    parser.add_argument('--cfgpath', help='overrides the default path to config.json', default=CONFIG_PATH)
    parser.add_argument('--dbsid', help='overrides the DB SID in config.json')
    parser.add_argument('--dbuser', help='overrides the DB USER in config.json')
    parser.add_argument('--dbpswd', help='overrides the DB PASSWORD in config.json')
    parser.add_argument('--dbhost', help='overrides the DB HOST in config.json')
    parser.add_argument('--dbport', help='overrides the DB PORT in config.json')

    return parser.parse_args()

class IterStream(object):
    "File-like streaming iterator."

    def __init__(self, generator):
        self.generator = generator
        self.iterator = iter(generator)
        self.leftover = b''

    def __len__(self):
        return self.generator.__len__()

    def __iter__(self):
        return self.iterator

    def __next__(self):
        return next(self.iterator)

    def read(self, size):
        data = self.leftover
        count = len(self.leftover)
        try:
            while count <= size:
                chunk = next(self)
                data += chunk
                count += len(chunk)
        except StopIteration:
            self.leftover = b''
            return data

        if count > size:
            self.leftover = data[size:]

        return data[:size]


def to_base64_safe(str):
    return base64.b64encode(str.encode()).decode("UTF-8")

def from_base64_safe(str):
    try:
        res = base64.b64decode(str.encode()).decode("UTF-8")
    except:
        res = str

    return res

def GetItemByPath(dic, path):
    v = dic
    for k in path.split("/"):
        if not v or not isinstance(v, dict):
            return
        v = v.get(k)

    return v

