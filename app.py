#Import dependencies
from flask import Flask, jsonify, redirect, request, render_template, session, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_required, login_user, current_user, LoginManager
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from sqlalchemy.dialects.postgresql import JSON

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

class Product(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(40), nullable = False, unique = True)
    summary = db.Column(db.String(100), nullable = False)
    description = db.Column(db.String(300), nullable = False)
    rating = db.Column(db.Float, nullable = False, default = 0.0)
    servings = db.Column(db.Integer, nullable = True)
    flavour = db.Column(db.String(30), nullable = True)
    weight = db.Column(db.Float, nullable = False)
    specs = db.Column(JSON, nullable = True)
    unitSold = db.Column(db.Integer, nullable=False, default = 0)
    image1 = db.Column(db.String(69), nullable = False)
    image2 = db.Column(db.String(69), nullable = False)
    image3 = db.Column(db.String(69), nullable = False)
    image4 = db.Column(db.String(69), nullable = False)
    nutritional_label_main = db.Column(db.String(69), nullable = False)
    nutritional_label_second = db.Column(db.String(69), nullable = True)
    discount = db.Column(db.Float, nullable=True, default = 0.0)
    allergy_label = db.Column(db.String(100), nullable = True, default = None)
    price = db.Column(db.Float, nullable=False, default = 0.0)

    def __init__(self, title, summary, description, rating=0.0, servings=None, flavour=None, 
                 specs=None, unitSold=0, image1='', image2='', image3='', image4='', 
                 nutritional_label_main='', nutritional_label_second=None, discount=0.0, allergy_label=None):
        self.title = title
        self.summary = summary
        self.description = description
        self.rating = rating
        self.servings = servings
        self.flavour = flavour
        self.specs = specs
        self.unitSold = unitSold
        self.image1 = image1
        self.image2 = image2
        self.image3 = image3
        self.image4 = image4
        self.nutritional_label_main = nutritional_label_main
        self.nutritional_label_second = nutritional_label_second
        self.discount = discount
        self.allergy_label = allergy_label

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'price': self.price,
            'rating': self.rating,
            'image1': self.image1,
            'summary': self.summary
        }

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
    print(current_user)
    return render_template('home.html', signedIn = current_user.is_authenticated)

@app.route("/templatetest")
def template():
    return render_template('baseTemplate.html', signedIn = current_user.is_authenticated)

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
        if 'Temporary_Cart' in session:
            session['cart'] = session['Temporary_Cart']
            session.pop('Temporary_Cart')
            return redirect(url_for('cart'))
        return redirect(url_for('home'))
    return render_template('signup.html')

@app.route("/login", methods = ['POST', 'GET'])
def login():
    if request.method == 'POST':
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

                print(session)
                login_user(registeredUser)
                print('logged in')

                print(session)
                if 'Temporary_Cart' in session:
                    print("Guest user had a temporary cart before logging in")
                    session['cart'] = session['Temporary_Cart']
                    session.pop('Temporary_Cart')
                    print("----REDIR: FROM LOGIN TO CART")
                    return redirect(url_for('cart'))
                
                print("No temporary cart found, redirecting to home")
                return redirect(url_for("home"))
            else:
                return jsonify({'authenticated' : False,
                                'message' : 'Invalid credentials'})
        else:
            return jsonify({'authenticated' : False,
                    'message' : 'No account with the given email address/phone number exists with Haki'})
    else:
        print("Rendering Login")
        return render_template('login.html')

@app.route("/products/view/id=<product_id>", methods=['POST', 'GET'])
def product(product_id):
    #Rendering the page
    requestedProduct = Product.query.filter_by(id = product_id).first()
    print(requestedProduct)
    print(current_user.is_authenticated)

    return render_template('productTemplate.html',signedIn = current_user.is_authenticated, id = requestedProduct.id,
                           title = requestedProduct.title, rating = requestedProduct.rating,
                           summary = requestedProduct.summary, description = requestedProduct.description,
                           servings = requestedProduct.servings, flavour = requestedProduct.flavour,
                           specs = requestedProduct.specs, unitSold = requestedProduct.unitSold,
                           img1 = requestedProduct.image1, img2 = requestedProduct.image2, img3 = requestedProduct.image3, img4 = requestedProduct.image4,
                           nutritionalLabel1 = requestedProduct.nutritional_label_main, nutritionalLabel2 = requestedProduct.nutritional_label_second,
                           allergy = requestedProduct.allergy_label)

@app.route('/cart')
def cart():
    print("Cart called")
    if 'cart' not in session:
        session['cart'] = {}
        session.permanent = True
    else:
        print("cart in session")
    return render_template("cart.html", cart = session['cart'])

@app.route('/addToCart', methods=['POST', 'GET'])
def addToCart():
    try:
        print(session['cart'])
    except:
        print("Cart doesm't exist")
    product_id = request.form['id']
    quantity = int(request.form['quantity'])
    print("Incoming product (API): ", product_id, quantity)

    #Now we add >:D
    if not(current_user.is_authenticated):
        print("Error: Not logged in")
        return jsonify({"message" : 'Please log in to place orders with Haki'})

    if 'cart' not in session:
        session['cart'] = {}
        session.permanent = True
        print("--------------------NEW CART MADE-------------------------")
    
    if product_id not in session['cart']:
        session['cart'][product_id] = quantity
        print("Not in cart, adding new")
    else:
        print("In cart, incrementing")
        session['cart'][product_id] += quantity

    print(session['cart'])
    
    print("pp")
    return jsonify({'message' : 'Product added to cart'})

@app.route('/purchaseThenCheckout', methods=['POST'])
def purchaseThenCheckout():
    if request.method == 'POST':
        product_id = request.form['id']
        quantity = int(request.form['quantity'])
        print("Incoming product (API): ", product_id, quantity)

        #Now we add >:D
        if current_user.is_authenticated == False:
            print("Creating temporary cart")
            session['Temporary_Cart'] = {}
            session['Temporary_Cart'][product_id] = [quantity]
            session.permanent = True
            print("Temp Session: ", session, "\nNow, we redirect to login-----------------------")
            return redirect(url_for('login'))

        if 'cart' not in session:
            session['cart'] = {}
            session.permanent = True
            print("--------------------NEW CART MADE-------------------------")
        
        if product_id not in session['cart']:
            session['cart'][product_id] = quantity
            print("Not in cart, adding new")
        else:
            print("In cart, incrementing")
            session['cart'][product_id] += quantity

        print(session['cart'])
        
        print("pp")
        return redirect(url_for('cart'))

@app.route("/catalogue")
def catalogue():
    return render_template("catalogue.html")

@app.route("/render-products", methods=['POST', 'GET'])
def render():
    if request.method == "GET":
        print("Hairy penis")

    products = Product.query.all()
    for item in products:
        print(item.title, item.price, item.rating, item.image1, item.summary, item.price)
    products_list = [item.to_dict() for item in products]
    return jsonify(products_list)

@app.route("/logout")
def amd():
    session.clear()
    print(session)
    return redirect(url_for('signup'))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port = 6900)