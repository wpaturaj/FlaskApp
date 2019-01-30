from flask import Blueprint

dodanie=Blueprint('dodanie',__name__,template_folder='templates')

from app.klient import routes