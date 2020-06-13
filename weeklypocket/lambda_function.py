import pickle
from email.mime.text import MIMEText
import base64
from urllib.error import HTTPError
import boto3

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def get_gmail_token(bucket, file_name):
    """Read the saved gmail tokens from S3"""
    # The file gmail_token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.

    creds = pickle.loads(boto3.client('s3').get_object(Bucket=bucket, Key=file_name)['Body'].read())

    # TODO: Check whether creds are valid using creds.valid

    return build('gmail', 'v1', credentials=creds)


def create_message(sender, to, subject, message_text):
  """Create a message for an email.

  Args:
    sender: Email address of the sender.
    to: Email address of the receiver.
    subject: The subject of the email message.
    message_text: The text of the email message.

  Returns:
    An object containing a base64url encoded email object.
  """
  message = MIMEText(message_text)
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

def my_handler(recipient, context):
    bucket = "weekly-pocket"
    file_name = "gmail_token.pickle"
    
    service = get_gmail_token(bucket, file_name)
    msg = create_message("me", recipient, "Weekly Pocket", "Hi Paul,\nThis is your Weekly Pocket e-mail. Click on the link below to view a randomly chosen e-mail from your Pocket favourites.\n\nhttp://127.0.0.1:5000")
    send_message(service, "me", msg)

    return { 
        'message' : 'ok'
    }  

