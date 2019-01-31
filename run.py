from app import create_app
from sqlalchemy.orm import scoped_session, sessionmaker, Query

# if __name__=='__main__':
flask_app=create_app('config')
flask_app.run()