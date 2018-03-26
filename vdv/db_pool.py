import time
import concurrent.futures as ftr
from psycopg2 import pool


class DBSessionPool(pool.ThreadedConnectionPool):
    s_executor = ftr.ThreadPoolExecutor(max_workers=1)

    def __acquire(self):
        return super().getconn()

    def acquire(self):
        f = self.s_executor.submit(self.__acquire)
        return f.result()

    def release(self, conn):
        conn.close()
