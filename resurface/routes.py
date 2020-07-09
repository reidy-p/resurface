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

@application.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@application.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('home'))
    return render_template('login.html', title='Sign In', form=form)

@application.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@application.route("/home")
def home():
    headers = {'Content-Type': "application/json; charset=UTF-8", "X-Accept": "application/json"}
    redirect_uri = url_for("callback", _external=True)
    data = {
        "redirect_uri": redirect_uri,
        "consumer_key": application.config['CONSUMER_KEY']
    }
    response = requests.post("https://getpocket.com/v3/oauth/request", headers=headers, json=data)
    authorization_code = response.json()['code']

    session['authorization_code'] = authorization_code
    pocket_auth_url = "https://getpocket.com/auth/authorize"
    url = pocket_auth_url + f"?request_token={authorization_code}&redirect_uri={redirect_uri}"
    return render_template('home.html', redirect_url=url)

@application.route("/callback")
def callback():
    headers = {'Content-Type': "application/json; charset=UTF-8", "X-Accept": "application/json"}
    data = {
        "code": session['authorization_code'],
        "consumer_key": application.config['CONSUMER_KEY']
    }
    response = requests.post("https://getpocket.com/v3/oauth/authorize", headers=headers, json=data)

    access_token = response.json()['access_token']
    data = {
        "access_token": access_token,
        "consumer_key": application.config['CONSUMER_KEY'],
        "favorite": 1
    }
    response = requests.get("https://getpocket.com/v3/get/", json=data)
    favourites = response.json()['list']
    choice = random.choice(list(favourites.keys()))
    return redirect(favourites[choice]["resolved_url"])
