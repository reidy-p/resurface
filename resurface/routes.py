from flask import render_template, url_for, redirect, request, send_file, Response
import requests
from resurface import application
import webbrowser
import yaml
import random
from flask import session

with open("config.yml", 'r') as keys_file:
    config = yaml.safe_load(keys_file)

CONSUMER_KEY = config['consumer_key']

@application.route("/")
def home():
    headers = {'Content-Type': "application/json; charset=UTF-8", "X-Accept": "application/json"}
    redirect_uri = url_for("callback", _external=True)
    data = {"redirect_uri": redirect_uri, "consumer_key": CONSUMER_KEY}
    r = requests.post("https://getpocket.com/v3/oauth/request", headers=headers, json=data)
    authorization_code = r.json()['code']

    session['authorization_code'] = authorization_code
    url = f"https://getpocket.com/auth/authorize?request_token={authorization_code}&redirect_uri={redirect_uri}"
    return render_template('login.html', redirect_url=url)

@application.route("/callback")
def callback():
    headers = {'Content-Type': "application/json; charset=UTF-8", "X-Accept": "application/json"}
    data = {"code": session['authorization_code'], "consumer_key": CONSUMER_KEY}
    r = requests.post("https://getpocket.com/v3/oauth/authorize", headers=headers, json=data)

    access_token = r.json()['access_token']
    data = {"access_token": access_token, "consumer_key": CONSUMER_KEY, "favorite": 1}
    r = requests.get("https://getpocket.com/v3/get/", json=data)
    favourites = r.json()['list']
    choice = random.choice(list(favourites.keys()))
    return redirect(favourites[choice]["resolved_url"])

