from flask import url_for, redirect, session
import requests
from resurface import application, db
from resurface.models import Item
from resurface.tasks import sched
from flask_login import current_user
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import os
import pickle

def pocket_import():
    headers = {'Content-Type': "application/json; charset=UTF-8", "X-Accept": "application/json"}
    redirect_uri = url_for("callback", _external=True)
    data = {
        "redirect_uri": redirect_uri,
        "consumer_key": application.config['POCKET_CONSUMER_KEY']
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
        "consumer_key": application.config['POCKET_CONSUMER_KEY']
    }
    response = requests.post("https://getpocket.com/v3/oauth/authorize", headers=headers, json=data)

    access_token = response.json()['access_token']

    if not os.path.exists('pocket_access_token.pickle'):
        with open('pocket_access_token.pickle', 'wb') as token:
            pickle.dump(access_token, token)

    data = {
        "access_token": access_token,
        "consumer_key": application.config['POCKET_CONSUMER_KEY'],
        "favorite": 1
    }
    headers = {'Content-Type': "application/json;"}
    response = requests.post("https://getpocket.com/v3/get/", json=data, headers=headers)
    favourites = [favourite for favourite in response.json()['list'].values()]

    add_items(current_user.id, favourites)

    sched.add_job(
        check_pocket_updates,
        kwargs={'user_id': current_user.id},
        trigger='interval',
        hours=1
    )

    return redirect(url_for('home'))

def check_pocket_updates(user_id):
    with open('pocket_access_token.pickle', 'rb') as token:
        access_token = pickle.load(token)

    data = {
        "access_token": access_token,
        "consumer_key": application.config['POCKET_CONSUMER_KEY'],
        "favorite": 1
    }
    response = requests.get("https://getpocket.com/v3/get/", json=data)
    favourites = [favourite for favourite in response.json()['list'].values()]

    add_items(user_id, favourites)

def add_items(user_id, items):
    for item in items:
        if item['resolved_title'] != '':
            title = item['resolved_title']
        else:
            title = item['given_title']
        db.session.add(
            Item(
                user_id=user_id,
                title=title,
                url=item['resolved_url'],
                word_count=item['word_count'],
                time_added=datetime.fromtimestamp(int(item['time_added'])),
                source="pocket"
            )
        )
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()

