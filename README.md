Resurface
--
With so much amazing content on the web it can be hard to remember to revisit your favourite articles, videos, or Tweets. Resurface gathers all of your favourite content from the web in one place and sends your regular reminders with samples of your favourites so you can rediscover the best of the web.

Try it at: https://getresurface.net

### Features
* Import your favourite content from popular sites like Pocket, YouTube, etc. to view them all in one place
* Receive periodic e-mails with reminders to rediscover a sample of these favourites
* [Planned] Quickly search across all of your favourite content

### Technologies
Built using:
* Flask Web Framework for Python
* [SendGrid E-mail API](https://sendgrid.com/) for automating e-mails
* SQLite
* [APScheduler](https://apscheduler.readthedocs.io/en/stable/) for scheduling reminders
* [Bootstrap](https://getbootstrap.com/) for styling
* AWS Route 53 for domain name registration
* [Zoho](https://zoho.com) for associating an e-mail address with the domain name

### Config File
Running the application requires a file called ``config.py`` in the root directory with the following values:

```python
class Config:
    SECRET_KEY=''
    # Pocket API key
    POCKET_CONSUMER_KEY=''
    # SendGrid API Key
    MAIL_PASSWORD=""
    MAIL_DEFAULT_SENDER=""
```

It also requires keys from Google's API with permissions to view your YouTube channel. This file should also be stored in the root directory and named ``google_api_secrets.json``.
