from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base

from app import db

engine = db.get_engine()


def is_table_present(table_name):
    return engine.dialect.has_table(engine, table_name)


def create_table(table_name):

    class History(db.Model):
        __tablename__ = table_name
        id = db.Column(db.Integer, primary_key=True)
        status = db.Column(db.String(191))
        timestamp = db.Column(db.DateTime)

    db.create_all()
    return History


def get_table(table_name):
    class History(db.Model):
        __tablename__ = table_name
        __table_args__ = {'extend_existing': True}
        id = db.Column(db.Integer, primary_key=True)
        status = db.Column(db.String(191))
        timestamp = db.Column(db.DateTime)

    return History
