from flask import current_app, render_template

from blog.email import send_email


def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email('[Blog] Reset Your Password', sender=current_app.config['ADMIN'],
               recipients=[user.email],
               text_body=render_template('email/reset_password.txt', user=user, token=token),
               html_body=render_template('email/reset_password_mail.html', user=user, token=token))
