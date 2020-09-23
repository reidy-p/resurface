import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from email.mime.text import MIMEText
import base64
from urllib.error import HTTPError
from resurface.models import User, Item, InterestedUser
from resurface.tasks import sched
import random
from flask import make_response, jsonify
from resurface import application
from jinja2 import Template

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def gmail_authenticate():
    """Shows basic usage of the Gmail API."""
    creds = None
    # The file gmail_token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('gmail_token.pickle'):
        with open('gmail_token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'gmail_credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('gmail_token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('gmail', 'v1', credentials=creds)


def create_message(sender, to, subject, item):
  """Create a message for an email.

  Args:
    sender: Email address of the sender.
    to: Email address of the receiver.
    subject: The subject of the email message.
    item: The item to send in the email message.

  Returns:
    An object containing a base64url encoded email object.
  """

  message_text = Template("""
  Hello,<br>
  <br>
  <ul>
    {% for item in items %}
      <li><a href="{{ item.url }}">{{ item.title }}</a></li>
    {% endfor %}
  </ul>
  """)
  message_text = message_text.render(items=item)

  message = MIMEText(message_text, 'html')
  message['to'] = to
  message['from'] = sender
  message['subject'] = subject

  return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

def send_message(service, user_id, message):
  """Send an email message.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    message: Message to be sent.

  Returns:
    Sent Message.
  """
  try:
    message = (service.users().messages().send(userId=user_id, body=message)
               .execute())
    print('Message Id: %s' % message['id'])
    return message
  except HTTPError as error:
    print('An error occurred: %s' % error)

def send_email(email, num_items):
    with application.app_context():
        service = gmail_authenticate()
        user = User.query.filter_by(email=email).first()
        items = user.items.all()
        if len(items) != 0:
            choice = random.sample(user.items.all(), num_items)
            msg = create_message("me", email, "Resurface", choice)
            send_message(service, "me", msg)
        #data = {'message': 'Email sent', 'code': 'SUCCESS'}
        #return make_response(jsonify(data), 201)

