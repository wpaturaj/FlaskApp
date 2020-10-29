# app/__init__.py
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker, Query
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import mapper, sessionmaker
from sqlalchemy.ext.automap import automap_base
from sqlalchemy_repr import RepresentableBase
# from database import init_db
db=SQLAlchemy()
bootstrap=Bootstrap()
Base = declarative_base(cls=RepresentableBase)


ok=engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=True)
db_session=scoped_session(sessionmaker(autocommit=False,autoflush=False,bind=ok))
Base.query = db_session.query_property()
Base.metadata.create_all(bind=engine)

def create_app(config_file):
    app = Flask(__name__)
    app.config.from_pyfile(configuration)
    db.init_app(app)
    Base = declarative_base(cls=RepresentableBase)
    Base.query = db_session.query_property()
    Base.metadata.create_all(bind=engine)
    bootstrap.init_app(app)
    #strona glowna
    from app.zamow import main
    app.register_blueprint(main) 
    # dodawanie zamowiend  
    from app.klient import dodanie
    app.register_blueprint(dodanie) 
    # #flota
    from app.flota import flota
    app.register_blueprint(flota) 
    # #firma
    from app.firma import firma
    app.register_blueprint(firma) 

    app.static_folder = 'static'  
    return app