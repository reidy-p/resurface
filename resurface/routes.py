from flask import render_template, url_for, redirect, session, flash
import requests
from resurface import application, db
import random
from flask_login import current_user, login_user, logout_user
from resurface.models import User, InterestedUser
from resurface.forms import LoginForm, RegistrationForm, InterestForm
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

