import logging
import time
import asyncio
import asyncpg

MAX_CONNECTION_RETRIES = 5
MAX_CONNECTIONS_POOL = 10
MIN_CONNECTIONS_POOL = 3


class DBConnectionError(Exception):
    pass


class PostgreSQLConnection:

    def __init__(self, pool, connection, logger):
        self.connection = connection
        self.pool = pool
        self.logger = logger.getChild("PostgreSQLConnection")
        self.current_cursor = None

    def __del__(self):
        try:
            if self.connection:
                loop = asyncio.get_event_loop()
                loop.create_task(self.pool.__release_connection(self.connection))
        except AttributeError as error:
            self.logger.info("Connection has been deleted!!!")

    async def transaction(self, callable):
        if not self.connection:
            raise DBConnectionError()

        num_retries = 0
        while num_retries < MAX_CONNECTION_RETRIES:
            try:
                if num_retries:
                    try:
                        self.connection = await self.pool.__get_connection()
                    except AttributeError:
                        self.logger.error("PostgreSQLPoolConnections has been deleted!!!")
                        break
                res = await callable()
                return res
            except asyncpg.exceptions.NoActiveSQLTransactionError as exc:
                time.sleep(5)
                # err, = exc.args
                # if not isinstance(err, str) and err.code in [12152, 12592, 3113, 3114, 3135]:
                #    # connection lost, retry
                self.logger.warning('DB disconnect -- retrying...')
                #    self.cursor = None
                #    self.db = None
                #    time.sleep(5)
                # else:
                #    raise
            num_retries += 1

        raise DBConnectionError()

    def execute(self, *args, **kwargs):
        async def body():
            await self.connection.execute(*args, **kwargs)

        return self.transaction(body)

    def fetchall(self, *args, **kwargs):
        async def body():
            return await self.connection.fetch(*args, **kwargs)

        return self.transaction(body)

    async def __get_cursor(self, *args, **kwargs):
        self.current_cursor = await self.connection.cursor(*args, **kwargs)

    def fetchone(self, *args, **kwargs):
        async def body():
            async with self.connection.transaction():
                await self.__get_cursor(*args, **kwargs)
                return await self.current_cursor.fetchrow()

        return self.transaction(body)

    def fetchmany(self, numRows, *args, **kwargs):
        async def body():
            async with self.connection.transaction():
                await self.__get_cursor(*args, **kwargs)
                return await self.current_cursor.fetch(numRows)

        return self.transaction(body)

    async def fetchmany_iter(self, numRows, *args, **kwargs):
        async with self.connection.transaction():
            await self.__get_cursor(*args, **kwargs)
            while True:
                result = await self.current_cursor.fetch(numRows)
                if not result:
                    break

                yield result

    async def fetchone_iter(self, *args, **kwargs):
        async with self.connection.transaction():
            await self.__get_cursor(*args, **kwargs)
            while True:
                result = await self.current_cursor.fetchrow()
                if not result:
                    break

                yield result


class PostgreSQLPoolConnections:
    def __init__(self, **kwargs):
        try:
            self.db_params = dict(**kwargs)
        except...:
            message = "DataBase params didn't find! PostgreSQLConnection will not be create!!!"
            logging.log(logging.CRITICAL, message)
            return

        self.logger = kwargs.get('logger')
        if not self.logger:
            self.logger = logging.getLogger("PostgreSQLPoolConnections")

    @classmethod
    async def create(cls, **kwargs):
        self = PostgreSQLPoolConnections(**kwargs)
        self.pool_db = await self.__get_pool()

        return self

    def __del__(self):
        loop = asyncio.get_event_loop()
        loop.create_task(self.__close_pool())

    async def __get_pool(self):
        return await asyncpg.create_pool(min_size=MIN_CONNECTIONS_POOL, max_size=MAX_CONNECTIONS_POOL,
                                         user=self.db_params['user'], password=self.db_params['password'],
                                         database=self.db_params['database'], host=self.db_params['host'])

    async def __close_pool(self):
        await self.pool_db.close()

    async def __acquire_postgresql_connection(self):
        """
        :return: An instance of PostgreSQLConnection
        """
        conn = await self.__get_connection()
        return PostgreSQLConnection(self, conn, self.logger)

    async def __release_postgresql_connection(self, conn):
        """
        :param PostgreSQLConnection conn: exits connection
        """
        if conn is PostgreSQLConnection:
            await self.__release_connection(conn.connection)

    async def __get_connection(self):
        return await self.pool_db.acquire()

    async def __release_connection(self, conn):
        if conn is asyncpg.Connection:
            await self.pool_db.release(conn)

    async def open_connection(self):
        current_connection = await self.__acquire_postgresql_connection()
        return current_connection

    async def close_connection(self, conn):
        """
            :param PostgreSQLConnection conn: exits connection
        """
        if conn is PostgreSQLConnection:
            self.__release_postgresql_connection(conn)

# Exmple
# s_dbParams = {
#     'host': 'localhost',
#     'port': 5432,
#     'sid': 'vdv',
#     'user': 'vdv_admin',
#     'password': "asdfghjkl;'",
#     'database': 'VDV',
#     'direct': None
# }
# async def run():
#     m = await PostgreSQLPoolConnections.create(**s_dbParams)
#     conn = await m.open_connection()
#     # print(await conn.execute("INSERT INTO public.films(code, title, did, date_prod, kind, len) VALUES (5, '1231', 123, NULL, NULL, NULL);"))
#     print(await conn.fetchmany(2, "SELECT code, title, did, date_prod, kind, len FROM public.films;"))
#     async for i in conn.fetchone_iter("SELECT code, title, did, date_prod, kind, len FROM public.films;"):
#         print(i)
#
#     async for i in conn.fetchone_iter("SELECT code, title, did, date_prod, kind, len FROM public.films;"):
#         print(i)
#
#
# loop = asyncio.get_event_loop()
# loop.run_until_complete(run())
