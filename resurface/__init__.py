from flask import Flask, session
from flask_executor import Executor
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from config import Config

application = Flask(__name__)
application.config.from_object(Config)
db = SQLAlchemy(application)
login = LoginManager(application)
executor = Executor(application)
bootstrap = Bootstrap(application)

from resurface import routes, models
db.create_all()
db.session.commit()
