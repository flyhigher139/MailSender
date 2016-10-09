#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import os
from flask import Flask, request, redirect, url_for, current_app
from flask.views import MethodView
from flask_mail import Mail, Message

app = Flask(__name__)
mail = Mail()

class Config(object):
    # email server
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

USER_PASSWORD_PAIRS = os.environ.get('USER_PASSWORD_PAIRS') or 'admin,admin, gevin,gevin'


#########################
# initialization
#########################

app.config.from_object(Config)
mail.init_app(app)


#########################
# functions
#########################

def get_user_passwords():
    user_password_pairs = USER_PASSWORD_PAIRS
    user_password_list = [pair.strip() for pair in user_password_pairs.split(',')]
    users = user_password_list[0::2]
    passwords = user_password_list[1::2]

    user_dict = dict(zip(users, passwords))

    return user_dict



def send_mails(recipients, cc, mail_title, mail_body):
    msg = Message(mail_title)
    msg.body = mail_body

    msg.sender = current_app._get_current_object().config['MAIL_USERNAME']
    msg.recipients = recipients
    msg.cc = cc

    mail.send(msg)


##########################
# Views and APIs
##########################

auth = get_user_passwords()

@app.route('/')
def index():
    return 'This is a mail server'

@app.route('/mail/', methods=['GET', 'POST'])
def mail_view():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if password != auth.get(username):
            return 'Username or Password error', 401

        recipients = request.form.get('recipients')
        recipients = [recipient.strip() for recipient in recipients.split(',')]

        cc = request.form.get('cc')
        cc = [cc.strip() for cc in cc.split(',')]

        title = request.form.get('title')
        body = request.form.get('body')

        send_mails(recipients, cc, title, body)
        return redirect(url_for('mail_view'))
    return '''
    <!DOCTYPE html>
    <html>
        <head>
            <title>Mail</title>
            <link href="//maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body>
            <div class="container">
                <div class="col-md-10 col-md-offset-1">
                <h3>Send Mails</h3><hr/>
                <form method="POST">
                    <div class="form-group">
                        <label>Receivers:</label><input type="text", name="recipients" class="form-control" >
                    </div>
                    <div class="form-group">
                        <label>Cc:</label><input type="text", name="cc" class="form-control" >
                    </div>
                    <div class="form-group">
                        <label>Title:</label>
                        <input type="text", name="title" class="form-control" >
                    </div>
                    <div class="form-group">
                        <label>Body:</label>
                        <textarea class="form-control" rows="6" name="body"></textarea>
                    </div>
                    <div class="form-group">
                        <label>Username:</label><input type="text", name="username" class="form-control" >
                        <label>Password:</label><input type="password", name="password" class="form-control" >
                    </div>
                    <div class="form-group">
                        <button type="submit" value="Submit" class="btn btn-primary">Submit</button>
                    </div>
                </form>
                </div>
            </div>
        </body>
    </html>
    '''

class SendMailView(MethodView):
    def get(self):
        return 'Send mails by `POST` method'

    def post(self):
        auth_info = request.authorization
        if not auth_info or auth_info.password != auth.get(auth_info.username):
            return 'Username or Password error', 401

        data = request.get_json()

        recipients = data.get('recipients')

        cc = data.get('cc')

        title = data.get('title')
        body = data.get('body')

        send_mails(recipients, cc, title, body)

        return 'Succeed to send mails'

app.add_url_rule('/mail/api/', view_func=SendMailView.as_view('send_mail_view'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
