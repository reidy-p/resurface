from flask import render_template, url_for, redirect, request, send_file, Response
import requests
from weeklypocket import app
import webbrowser
import yaml
import random

with open("config.yml", 'r') as keys_file:
    config = yaml.safe_load(keys_file)

CONSUMER_KEY = config['consumer_key']

@app.route("/")
def home():
    headers = {'Content-Type': "application/json; charset=UTF-8", "X-Accept": "application/json"}
    redirect_uri = "http://127.0.0.1:5000/authorized"
    data = {"redirect_uri": redirect_uri, "consumer_key": CONSUMER_KEY}
    r = requests.post("https://getpocket.com/v3/oauth/request", headers=headers, json=data)
    authorization_code = r.json()['code']
    return redirect(f"https://getpocket.com/auth/authorize?request_token={authorization_code}&redirect_uri={redirect_uri}/{authorization_code}")


@app.route("/authorized/<code>")
def authorized(code):
    headers = {'Content-Type': "application/json; charset=UTF-8", "X-Accept": "application/json"}
    data = {"code": code, "consumer_key": CONSUMER_KEY}
    r = requests.post("https://getpocket.com/v3/oauth/authorize", headers=headers, json=data)
    if r.ok:
        access_token = r.json()['access_token']
        data = {"access_token": access_token, "consumer_key": CONSUMER_KEY, "favorite": 1}
        r = requests.get("https://getpocket.com/v3/get/", json=data)
        favourites = r.json()['list']
        choice = random.choice(list(favourites.keys()))
        return redirect(favourites[choice]["resolved_url"])
    else:
        return 'Failed'

