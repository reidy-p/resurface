from logging import log
from flask import render_template, url_for, redirect, flash, request as flask_request, abort
from requests.api import request
from resurface import application, db
from flask_login import current_user, login_user, logout_user
from resurface.models import User, Item, Reminder
from resurface.forms import LoginForm, RegistrationForm, ReminderForm, ManualItemForm
from resurface.email import send_mail
from resurface.tasks import sched
from resurface.imports.pocket import pocket_import
from resurface.imports.youtube import youtube_import
from resurface.imports.readwise import readwise
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from functools import wraps

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if current_user.is_authenticated:
            return f(*args, **kwargs)
        else:
            flash("Login required")
            return redirect(url_for('login'))

    return wrap

@application.route('/', methods=['GET'])
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
@login_required
def home():
    items = current_user.items.all()
    return render_template(
        'home.html',
        num_saved_items=len(items),
        saved_items=sorted(items, key=lambda item: item.time_added, reverse=True)
    )

@application.route('/reminders', methods=['GET', 'POST'])
@login_required
def reminders():
    form = ReminderForm()
    if form.validate_on_submit():
        sched.add_job(
            send_mail,
            kwargs={'email': current_user.email, 'num_items': form.num_items.data},
            trigger='cron',
            day_of_week=form.reminder_day.data,
            hour=form.reminder_time.data.hour,
            minute=form.reminder_time.data.minute
        )
        reminder_data = Reminder(
            user_id = current_user.id,
            reminder_day = form.reminder_day.data,
            reminder_time = form.reminder_time.data,
            reminder_items = form.num_items.data
        )
        db.session.add(reminder_data)
        db.session.commit()
        flash('Reminders succesfully changed!')
        return redirect(url_for('home'))
    return render_template(
                            'reminders.html',
                            form=form,
                            reminders=current_user.reminders.all()
                            )

@application.route("/import-items", methods=['GET', 'POST'])
@login_required
def import_items():
    form = ManualItemForm()
    if form.validate_on_submit():
        db.session.add(
            Item(
                user_id=current_user.id,
                title=form.title.data,
                url=form.url.data,
                time_added=datetime.now(),
                source="manual"
            )
        )
        try:
            db.session.commit()
            flash('Item added successfully!')
        except IntegrityError:
            db.session.rollback()
            flash('Item already exists!')
        return redirect(url_for('import_items'))
    pocket_url = pocket_import()
    youtube_url = youtube_import()
    readwise_url = url_for('readwise')
    return render_template('import.html', pocket_url=pocket_url, youtube_url=youtube_url, readwise_url=readwise_url, form=form)

@application.route('/delete-item')
@login_required
def delete_item():
    user_id = flask_request.args.get('user', type=str)
    title = flask_request.args.get('title', type=str)
    item = Item.query.filter_by(user_id=user_id, title=title).first()

    if item is None:
        abort(404)

    db.session.delete(item)
    db.session.commit()
    flash('Item deleted')
    return redirect(url_for('home'))

@application.route('/delete-reminder/<int:id>')
@login_required
def delete_reminder(id):
    reminder = Reminder.query.get(id)

    if reminder is None:
        abort(404)

    db.session.delete(reminder)
    db.session.commit()
    flash('Reminder deleted')
    return redirect(url_for('home'))

@application.route("/privacy-policy")
def privacy():
    return render_template("privacy.html")