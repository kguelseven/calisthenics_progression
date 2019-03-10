from flask import render_template
from flask_mail import Message
from project.email import send_email
from project import app, mail
'''
def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email('[Calisthenics-Progression] Reset Your Password',
    sender=app.config['MAIL_DEFAULT_SENDER'][0],
    recipients=[user.email],
    text_body=render_template('email/reset_password.txt',
    user=user, token=token),
    html_body=render_template('email/reset_password.html',
    user=user, token=token))
'''
def send_email(to, subject, template):
    msg = Message(
        subject,
        recipients=[to],
        html=template,
        sender=app.config['MAIL_DEFAULT_SENDER']
    )
    mail.send(msg)
