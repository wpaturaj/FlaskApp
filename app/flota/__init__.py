from flask import Blueprint

flota=Blueprint('flota',__name__,template_folder='templates')

from app.flota import routes 