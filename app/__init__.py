from flask import Flask
from flask_bootstrap import Bootstrap
app = Flask(__name__, static_folder='./public')
app.config['SECRET_KEY'] = 'hunter2'

from app import routes

Bootstrap(app)
