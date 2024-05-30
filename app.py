#Import dependencies
from flask import Flask, jsonify, redirect, request, render_template, session, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_required, login_user, current_user, LoginManager
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate

from datetime import timedelta, datetime
import re as regex
    
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
        email = request.form['email_id']
        phone = str(request.form['phone_number'])

        #Handle existing user trying to sign up
        if User.query.filter_by(email_id = email).first() != None:
            print("User already exists (email)")
            flash("This email and/or phone number already exists")

            return jsonify({'exists' : True,
                            'message' : 'A Haki account with this email already exists'})
        elif User.query.filter_by(phone_number = phone).first() != None:
            print("User already exists (phone number)")
            flash("This phone number already exists")

            return jsonify({'exists' : True,
                            'message' : 'A Haki account with this phone number already exists'})
        
        #Register user into database
        fname = request.form['first_name']
        lname = request.form['last_name']
        age = request.form['age']
        password = request.form['password']
        confirmPassword = request.form['confirm_password']

        hashedPassword = bcrypt.generate_password_hash(password)
        newUser = User(fname, lname, age, phone, email, hashedPassword)

        db.session.add(newUser)
        db.session.commit()
        print('User added')

        login_user(newUser, remember=False, duration=timedelta(days=1))
        return redirect(url_for('home'))
    return render_template('signup.html')

@app.route("/login", methods = ['POST', 'GET'])
def login():
    if request.method == 'POST':
        print(request, request.url)
        # print(body)

        identity = request.form['emailPhone']
        password = request.form['password']

        email_regex = r"[^@]+@[^@]+\.[^@]+"
        phone_regex = r"^\+?[\d\s\-()]+$"

        #Check whether the given data matches first, before checking whether the user actually exists or not :3
        if regex.match(email_regex, identity):
            registeredUser = User.query.filter_by(email_id = identity).first()
        elif regex.match(phone_regex, identity):
            registeredUser = User.query.filter_by(phone_number = identity).first()
        else:
            print("Invalid identity data sent from client\nTERMINATING----------------------------")
            return jsonify({'authenticated' : False,
                            'message' : 'Error: Invalid identity syntax'})      #Ideally, this message should never pop up since input validation is performed at clinet-side itself
        
        if registeredUser:
            print("User found")
            if bcrypt.check_password_hash(registeredUser.password, password):
                print("Pass matches, authenticated")
                login_user(registeredUser)
                print('logged in')
                return redirect(url_for("home"))
            else:
                return jsonify({'authenticated' : False,
                                'message' : 'Invalid credentials'})
        else:
            return jsonify({'authenticated' : False,
                    'message' : 'No account with the given email address/phone number exists with Haki'})
        
    return render_template('login.html')

@app.route("/logout")
def amd():
    session.clear()
    return redirect(url_for('signup'))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port = 6900)