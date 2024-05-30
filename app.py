#Import dependencies
from flask import Flask, jsonify, redirect, request, render_template, session, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_required, login_user, current_user, LoginManager
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate

from datetime import timedelta, datetime
    
#App configuration
app = Flask(__name__)
app.secret_key = 'ABCD'
app.permanent_session_lifetime = timedelta(days=1)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///test1.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

#Database definition
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True)
    first_name = db.Column(db.String(30), nullable = False)
    last_name = db.Column(db.String(30), nullable = False)
    age = db.Column(db.Integer, nullable = False)
    phone_number = db.Column(db.String(256), nullable = False, unique = True)
    email_id = db.Column(db.String(256), nullable = False, unique=True)
    password = db.Column(db.String(128), nullable=False)
    time_created = db.Column(db.DateTime, nullable = False, default = datetime.now())


    def __init__(self, fname, lname, age, phone, email, password) -> None:
        self.first_name = fname
        self.last_name = lname
        self.age = age
        self.phone_number = phone
        self.email_id = email
        self.password = password
        self.time_created = datetime.now()

        
#Login management
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def loadUser(user_id):
    return User.query.get(int(user_id))

#Endpoints
@app.route("/")
def home():
    return render_template('home.html')

@app.route("/templatetest")
def template():
    return render_template('baseTemplate.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['last_name']
        phone = request.form['phone_number']

        if User.query.filter_by(email_id = email).first() != None or User.query.filter_by(phone_number = phone).first() != None:
            print("User already exists")
            flash("This email and/or phone number already exists")
            return redirect(url_for("signup"))

        password = request.form['password']
    return render_template('signup.html')
@app.route("/login")
def login():
    pass
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port = 6900)