from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class DBConnection:
    s_owner_token = None

    s_dbParams = {
        'host': 'localhost',
        'port': 5432,
        'sid': 'vdv',
        'user': 'vdv_admin',
        'password': "asdfghjkl;'",
        'dbname': 'VDV',
        'direct': None
    }

    @classmethod
    def configure(cls, **kwargs):
        cls.s_dbParams.update(kwargs)
        #TODO: IMPROVE AUTH TO DB
        cls.engine = create_engine('postgresql://wjcjjdvt:XiZFxCaDuNg2b9z3MzBjDjMEnvF6clEF@horton.elephantsql.com:5432/wjcjjdvt', pool_size=20)
        # create a configured "Session" class
        cls.Session = sessionmaker(bind=cls.engine)

    def __init__(self, logger=None):
        p = self.s_dbParams
        p.update({'logger': logger})
        self.open()

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        self.close()

    def __acquire_connection(self):
        conn = self.engine.connect()
        session = self.Session(bind=conn)

        return session

    def __release_connection(self, conn):
        conn.close()

    def open(self):
        self.db = self.__acquire_connection()

    def close(self):
        self.__release_connection(self.db)
