from application.modules import *
import string
import random

from itsdangerous import URLSafeTimedSerializer

# msg = Message()
# msg.recipients = ["ronald@accentcom-cm.com"]
# msg.subject = 'Notification FDT'
# msg.sender = ('Application FDT', 'no_reply@accentcom.agency')
#
# msg.html = render_template('mail/notification_mail.html')
# mail.send(msg)


def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])


def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt=app.config['SECURITY_PASSWORD_SALT'],
            max_age=expiration
        )
    except:
        return False
    return email


def id_generator(size, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))