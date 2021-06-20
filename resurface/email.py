from resurface.models import User
import random
from resurface import application, mail
from jinja2 import Template
from flask_mail import Message

def send_mail(email, num_items):
    with application.app_context():
        msg = Message('Resurface Reminders', recipients=[email])

        user = User.query.filter_by(email=email).first()
        items = user.items.all()
        if len(items) != 0:
            choices = random.sample(user.items.all(), num_items)
            msg.body = create_mail(choices)
            msg.html = create_mail(choices)
            mail.send(msg)

def create_mail(items):

    message_text = Template("""
        Hello,<br>
        <br>
        <ul>
          {% for item in items %}
            <li><a href="{{ item.url }}">{{ item.title }}</a></li>
          {% endfor %}
        </ul>
    """)

    message_text = message_text.render(items=items)

    return message_text
