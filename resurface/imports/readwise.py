import requests
from resurface import application, db
from flask_login import current_user, login_required
from resurface.forms import AccessTokenForm
from resurface.models import Item
from flask import render_template, url_for, redirect, flash
from sqlalchemy.exc import IntegrityError
from datetime import datetime

@application.route("/readwise", methods=['GET', 'POST'])
@login_required
def readwise():
    readwise_access_token = current_user.readwise_access_token
    if readwise_access_token is None:
        form = AccessTokenForm()
        if form.validate_on_submit():
            if validate_readwise_token(form.access_token.data):
                current_user.readwise_access_token = form.access_token.data
                db.session.merge(current_user)
                db.session.commit()
                return redirect(url_for('readwise'))
            else:
                flash("Invalid token!")
                return redirect(url_for('readwise'))

        return render_template('readwise.html', title='Readwise Import', form=form)

    highlights_response = requests.get(
            url="https://readwise.io/api/v2/highlights/",
            headers={
        "Authorization": f"Token {readwise_access_token}"},
    ).json()['results']

    books_response = requests.get(
        url="https://readwise.io/api/v2/books/",
        headers={"Authorization": f"Token {readwise_access_token}"},
    ).json()['results']

    for highlight in highlights_response:
        if highlight['highlighted_at'] is None:
            time_added = datetime.now()
        else:
            time_added = datetime.strptime(highlight['highlighted_at'], "%Y-%m-%dT%H:%M:%SZ")

        title = None
        for book in books_response:
            if book['id'] == highlight['book_id']:
                title = book['title']
                author = book['author']
                break

        # Remove default Readwise items
        if title is not None and title != "How to Use Readwise":
            db.session.add(
                Item(
                    user_id=current_user.id,
                    title="Readwise Highlight: " + title + ' - ' + author,
                    text=highlight['text'],
                    time_added=time_added,
                    source="readwise"
                )
            )
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()

    return redirect(url_for('home'))

def validate_readwise_token(token):
    response = requests.get(
            url="https://readwise.io/api/v2/auth/",
            headers={
        "Authorization": f"Token {token}"},
    )

    return response.status_code == 204