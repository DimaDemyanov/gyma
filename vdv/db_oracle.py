import logging
import time
from contextlib import contextmanager
import cx_Oracle

ORACLE_MAX_STRLEN = 4000
CURSOR_ARRAY_SIZE = 1000
MAX_CONNECTION_RETRIES = 5
LOCKNAME = 'MARS2'

class DBConnectionError(Exception):
    pass

class OracleConnection:
    @property
    def hasDirect(self):
        return (self.dbparams['direct'] != None)

    def __init__(self, **kwargs):
        self.db = None
        self.cursor = None
        self.dbparams = dict(**kwargs)
        self.logger = kwargs.get('logger')
        if not self.logger:
            self.logger = logging.getLogger()

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        self.close()

    def __acquire_connection(self):
        dsn = cx_Oracle.makedsn(self.dbparams['host'], self.dbparams['port'], self.dbparams['sid'])
        return cx_Oracle.connect(self.dbparams['user'], self.dbparams['password'], dsn)

    def __release_connection(self, conn):
        conn.close()

    def open(self):
        self.db = self.__acquire_connection()
        self.cursor = self.db.cursor()
        self.cursor.arraysize = CURSOR_ARRAY_SIZE
        self.cursor.execute("ALTER SESSION SET NLS_LANGUAGE = 'AMERICAN'")
        self.cursor.execute("ALTER SESSION SET NLS_TERRITORY = 'AMERICA'")

    def close(self):
        if self.cursor:
            self.cursor.close()
            self.cursor = None
        if self.db:
            self.__release_connection(self.db)
            self.db = None

    def transaction(self, callable):
        if not self.db:
            raise DBConnectionError()

        num_retries = 0
        while num_retries < MAX_CONNECTION_RETRIES:
            try:
                if num_retries:
                    self.open()
                res = callable()
                self.db.commit()
                return res
            except (cx_Oracle.DatabaseError, cx_Oracle.OperationalError) as exc:
                err, = exc.args
                if not isinstance(err, str) and err.code in [12152, 12592, 3113, 3114, 3135]:
                    # connection lost, retry
                    self.logger.warning('DB disconnect -- retrying...')
                    self.cursor = None
                    self.db = None
                    time.sleep(5)
                else:
                    raise

            num_retries += 1

        raise DBConnectionError()

    def execute(self, *args, **kwargs):
        def body():
            self.cursor.execute(*args, **kwargs)

        return self.transaction(body)

    def fetchone(self, *args, **kwargs):
        def body():
            self.cursor.execute(*args, **kwargs)
            return self.cursor.fetchone()

        return self.transaction(body)

    def fetchmany(self, numRows, *args, **kwargs):
        def body():
            self.cursor.execute(*args, **kwargs)
            return self.cursor.fetchmany(numRows=numRows)

        return self.transaction(body)

    def fetchall(self, *args, **kwargs):
        def body():
            self.cursor.execute(*args, **kwargs)
            return self.cursor.fetchall()

        return self.transaction(body)

    @contextmanager
    def lock(self):
        handle = self.cursor.var(cx_Oracle.STRING)
        self.cursor.callproc('DBMS_LOCK.allocate_unique', parameters=[LOCKNAME, handle])
        r = self.cursor.callfunc('DBMS_LOCK.request', cx_Oracle.NUMBER,
                                 keywordParameters={'lockhandle': handle})
        if r:
            raise Exception('Failed to acquire DB lock (result code = %d)' % r)

        yield handle

        r = self.cursor.callfunc('DBMS_LOCK.release', cx_Oracle.NUMBER,
                                 keywordParameters={'lockhandle': handle})
        if r:
            raise Exception('Failed to release DB lock (result code = %d)' % r)
