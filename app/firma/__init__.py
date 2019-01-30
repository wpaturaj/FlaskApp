from flask import Blueprint

firma=Blueprint('firma',__name__,template_folder='templates')

from app.firma import routes 