from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

def init_db(engine,db_session):
	Base = declarative_base()
	Base.query = db_session.query_property()
	Base.metadata.create_all(bind=engine)