from flask import render_template, url_for, redirect, session, flash, jsonify, make_response
import requests
from resurface import application, db
from resurface.models import User, Item, InterestedUser
from flask_login import current_user
from sqlalchemy.exc import IntegrityError
from datetime import datetime

def pocket_import():
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
    return pocket_auth_url + f"?request_token={authorization_code}&redirect_uri={redirect_uri}"

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
    favourites = [favourite for favourite in response.json()['list'].values()]
    for favourite in favourites:
        if favourite['resolved_title'] != '':
            title = favourite['resolved_title']
        else:
            title = favourite['given_title']
        db.session.add(
            Item(
                user_id=current_user.id,
                title=title,
                url=favourite['resolved_url'],
                word_count=favourite['word_count'],
                time_added=datetime.fromtimestamp(int(favourite['time_added']))
            )
        )
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
    return redirect(url_for('home'))

