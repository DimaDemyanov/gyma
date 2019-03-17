from collections import OrderedDict

from sqlalchemy import Column, Boolean, Integer, Sequence

from vdv.db import DBConnection

class PropBase:
    id = Column(Integer, Sequence('vdv_prop_seq'), primary_key=True)
    vdvid = Column(Integer)
    propid = Column(Integer)
    value = Column(Integer)

    def to_dict(self):
        res = OrderedDict([(key, self.__dict__[key]) for key in ['vdvid', 'propid', 'value']])
        return res

    def __init__(self, vdvid, propid, value):

        self.vdvid = vdvid
        self.propid = propid
        self.value = value

    def add(self, session=None, no_commit=False):
        def proseed(session):
            session.db.add(self)
            if not no_commit:
                session.db.commit()
                return self.vdvid
            return None

        if session:
            return proseed(session)

        with DBConnection() as session:
            return proseed(session)

        return None

    # def update(self, session, no_commit=False):
    #     def proseed(session):
    #         entities = self.__class__.get().filter_by(vdvid=self.vdvid, propid=self.propid).all()
    #         for _ in entities:
    #             _.value = self.value
    #
    #         if not no_commit:
    #             session.db.commit()
    #
    #     if session:
    #         proseed(session)
    #
    #     with DBConnection() as session:
    #         proseed(session)

    def update(self, session, no_commit=False):
        def proseed(session):
            entities = self.__class__.get().filter_by(vdvid=self.vdvid, propid=self.propid).all()
            for _ in entities:
                _.value = self.value

            if not no_commit:
                session.db.commit()

        if session:
            proseed(session)

        with DBConnection() as session:
            proseed(session)


    @classmethod
    def delete(cls, vdvid, propid, raise_exception=True):
        with DBConnection() as session:
            res = session.db.query(cls).filter_by(vdvid=vdvid, propid=propid).all()

            if len(res):
                [session.db.delete(_) for _ in res]
                session.db.commit()
            # else:
            #     if raise_exception:
            #         raise FileNotFoundError('(vdvid, propid)=(%i, %i) was not found' % (vdvid, propid))

    @classmethod
    def delete_one(cls, vdvid, value, raise_exception=True):
        with DBConnection() as session:
            res = session.db.query(cls).filter_by(vdvid=vdvid, value=value).all()

            if len(res):
                [session.db.delete(_) for _ in res]
                session.db.commit()

    @classmethod
    def delete_value(cls, value, raise_exception=True):
        with DBConnection() as session:
            res = session.db.query(cls).filter_by(value=value).all()

            if len(res):
                [session.db.delete(_) for _ in res]
                session.db.commit()
            else:
                if raise_exception:
                    raise FileNotFoundError('(value)=(%s) was not found' % str(value))

    @classmethod
    def get(cls):
        with DBConnection() as session:
            return session.db.query(cls)

    @classmethod
    def get_object_property(cls, vdvid, propid):
        with DBConnection() as session:
            return [_.value for _ in session.db.query(cls).filter_by(vdvid=vdvid, propid=propid).all()]

    @classmethod
    def get_objects(cls, value, propid):
        with DBConnection() as session:
            return [_.vdvid for _ in session.db.query(cls).filter_by(value=value, propid=propid).all()]
