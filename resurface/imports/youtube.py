import google_auth_oauthlib.flow
import googleapiclient.discovery
from flask import url_for, redirect, request
from resurface import application, db
from resurface.models import Item
import os
from flask_login import current_user
from datetime import datetime

def google_auth_flow():
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
    client_secrets_file = "google_api_secrets.json"
    
    # Get credentials and create an API client
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        client_secrets_file, 
        scopes,
        redirect_uri=url_for("youtube_callback", _external=True)
    )

    return flow

def youtube_import():
    flow = google_auth_flow()

    auth_url, _ = flow.authorization_url(prompt='consent')

    return auth_url

@application.route("/youtube-callback")
def youtube_callback():
    flow = google_auth_flow()

    code = request.args.get('code')
    flow.fetch_token(code=code)
    credentials = flow.credentials

    api_service_name = "youtube"
    api_version = "v3"
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials
    )

    youtube_request = youtube.videos().list(
        part="snippet,contentDetails,statistics",
        myRating="like"
    )
    response = youtube_request.execute()

    for item in response['items']:
        db.session.add(
            Item(
                user_id=current_user.id,
                title=item['snippet']['title'],
                url=f"https://youtube.com/watch?v={item['id']}",
                word_count=0,
                time_added=datetime.now(),
                source="youtube"
            )
        )

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
    
    return redirect(url_for('home'))
