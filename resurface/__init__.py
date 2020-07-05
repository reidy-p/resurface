from flask import Flask, session
from flask_executor import Executor
import yaml

application = Flask(__name__)
executor = Executor(application)

with open("config.yml", 'r') as keys_file:
    config = yaml.safe_load(keys_file)

application.secret_key = config['secret_key']

from resurface import routes
