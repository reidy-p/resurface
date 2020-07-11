from flask import render_template, url_for, redirect, session, flash
import requests
from resurface import application, db
import random
from flask_login import current_user, login_user, logout_user
from resurface.models import User
from resurface.forms import LoginForm, RegistrationForm

@application.route('/')
def index():
    return render_template("index.html")

