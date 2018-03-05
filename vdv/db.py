import gzip
import base64

import cx_Oracle

from vdv import utils, db_pool
from vdv.db_oracle import *

IMPORT_BATCH_SIZE = 1000
CURSOR_ARRAY_SIZE = 1000

def _z64encode(src):
    return base64.b64encode(gzip.compress(src.encode('latin'))).decode('latin') if src else None

def _z64decode(src):
    return gzip.decompress(base64.b64decode(src)).decode('latin') if src else None

def _MakeBindList(size, start=0):
    return '(' + ','.join([':'+str(start + i) for i in range(0,size)]) + ')'

def _MakeBindListGroups(size, groupsize):
    return '(' + ','.join([_MakeBindList(groupsize, groupsize * i) for i in range(0,size)]) + ')'

def _MakeInsertSQL(table, fixed=None, binds=None):
    columns = []
    values = []
    if fixed:
        for k in fixed.keys():
            columns.append(k)
            values.append(str(fixed[k]))
    if binds:
        columns += binds
        values += [':%d' % i for i in range(1, len(binds)+1)]
    return 'INSERT INTO %s (%s) VALUES (%s)' % (table, ','.join(columns), ','.join(values))


class DBConnection(OracleConnection):
    s_owner_token = None
    s_dbParams = {
        'host': 'localhost',
        'port': 1521,
        'sid': 'vdv',
        'user': 'vdv',
        'password': 'vdv',
        'direct': None
    }

    @classmethod
    def configure(cls, **kwargs):
        cls.s_dbParams.update(kwargs)
        dsn = cx_Oracle.makedsn(cls.s_dbParams['host'], cls.s_dbParams['port'], cls.s_dbParams['sid'])
        cls.s_pool = db_pool.DBSessionPool(cls.s_dbParams['user'], cls.s_dbParams['password'], dsn,
                                           min=0, max=20, increment=1, threaded=True)

    def __acquire_connection(self):
        return self.s_pool.acquire()

    def __release_connection(self, conn):
        self.s_pool.release(conn)

    def __init__(self, logger=None):
        p = self.s_dbParams
        p.update({'logger': logger})
        super().__init__(**p)

    @classmethod
    def TakeOwnership(cls, **kwargs):
        with DBConnection() as db:
            cls.s_owner_token = str(db.GetUniqueIds()[0])
            db.SetVar('OWNER', cls.s_owner_token)

    def fetchitermany(self):
        while True:
            result = self.cursor.fetchmany(CURSOR_ARRAY_SIZE)
            if not result:
                break

            yield result

    def ResultIterOneByOne(self):
        'An iterator that uses fetchmany to keep memory usage down'
        while True:
            result = self.cursor.fetchone()
            if not result:
                break

            yield result