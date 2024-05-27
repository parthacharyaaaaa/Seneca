#Import dependencies
from flask import Flask, jsonify, redirect, request, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_required, login_user, current_user, LoginManager
from datetime import timedelta
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate

#Database definition

#App configuration
app = Flask(__name__)
app.secret_key = 'ABCD'
app.permanent_session_lifetime = timedelta(days=1)

#Login management
# login_manager = LoginManager()
# login_manager.init_app(app)
# login_manager.login_view = "login"

# @login_manager.user_loader
# def loadUser(user_id):
#     return User.query.get(int(user_id))

if __name__ == "__main__":
    app.run(debug=True, port = 2000)

#Endpoints
@app.route("/")
def home():
    return render_template('home.html')