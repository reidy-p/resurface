from flask import render_template, url_for, redirect, session, flash, jsonify, make_response
import requests
from resurface import application, db
import random
from flask_login import current_user, login_user, logout_user
from resurface.models import User, Item, InterestedUser
from resurface.forms import LoginForm, RegistrationForm, InterestForm, ReminderForm
from resurface.email import gmail_authenticate, create_message, send_message
from sqlalchemy.exc import IntegrityError

@application.route('/', methods=['GET', 'POST'])
def index():
    form = InterestForm()
    if form.validate_on_submit():
        interestedUser = InterestedUser(email = form.email.data)
        db.session.add(interestedUser)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
        flash('Thanks for registering your interest!')
        return redirect(url_for('index'))
    return render_template("index.html", form=form)

@application.route('/send-email', methods=['POST'])
def send_email():
    service = gmail_authenticate()
    users = User.query.all()
    for user in users:
        items = user.items.all()
        if len(items) != 0:
            choice = random.choice(user.items.all())
            msg = create_message("me", "paul_reidy@outlook.com", "Weekly Pocket", """<a href="{}">link</a>""".format(choice.url))
            send_message(service, "me", msg)
    data = {'message': 'Email sent', 'code': 'SUCCESS'}
    return make_response(jsonify(data), 201)

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
    return render_template('home.html', num_saved_items=len(current_user.items.all()))

@application.route('/reminders', methods=['GET', 'POST'])
def reminders():
    form = ReminderForm()
    if form.validate_on_submit():
        print(form.reminderDay.data)
    return render_template('reminders.html', form=form)

@application.route("/import-items")
def import_items():
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
    return render_template('import.html', redirect_url=url)

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
    favourites = {favourite['resolved_url'] for favourite in response.json()['list'].values()}
    for favourite in favourites:
        db.session.add(Item(user_id = current_user.id, url = favourite))
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
    return redirect(url_for('home'))
