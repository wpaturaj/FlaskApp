from app import create_app
from sqlalchemy.orm import scoped_session, sessionmaker, Query
import os
# if __name__=='__main__':
flask_app=create_app('config')
flask_app.run()
port = int(os.environ.get("PORT", 5000))
flask_app.run(host='0.0.0.0', port=port)