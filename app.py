#Import dependencies
from flask import Flask, jsonify, redirect, request, render_template, session, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_required, login_user, current_user, LoginManager
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy import ForeignKey
from sqlalchemy.orm.attributes import flag_modified

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
    last_seen = db.Column(db.DateTime, nullable = False, default = datetime.now())

    cart = db.Column(JSON, nullable = False, default = {})

    def __init__(self, fname, lname, age, phone, email, password) -> None:
        self.first_name = fname
        self.last_name = lname
        self.age = age
        self.phone_number = phone
        self.email_id = email
        self.password = password
        self.time_created = datetime.now()
        self.last_seen = datetime.now()
    
    def __repr__(self):
        return f'<User {self.email_id}>'

class Product(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(100), nullable = False, unique = True)
    author = db.Column(db.String(64), nullable = False)
    publisher = db.Column(db.String(100), nullable = False)
    publication_date = db.Column(db.String(32), nullable = False, default = "Not Available")
    isbn = db.Column(db.String(20), nullable = True)
    genre = db.Column(JSON, nullable = False)
    pages = db.Column(db.Integer, nullable = False)
    language = db.Column(db.String(16), nullable = False, default = "English")
    file_format = db.Column(db.String(4), nullable = False)
    cover = db.Column(db.String(69), nullable = False)
    url = db.Column(db.String(255), nullable = False, unique = True)
    summary = db.Column(db.Text, nullable = False)
    price = db.Column(db.Float, nullable=False, default = 0.0)
    discount = db.Column(db.Float, nullable=True, default = 0.0)
    rating = db.Column(db.Float, nullable = False, default = 0.0)
    total_reviews = db.Column(db.Integer, nullable = False, default = 0)
    units_sold = db.Column(db.Integer, nullable=False, default = 0)


    def __init__(self, title, author, publisher, publication_date, genre, isbn, pages, language, file_format, cover, url, summary, price, discount, rating, total_reviews, units_sold):
        self.title = title
        self.author = author
        self.publisher = publisher
        self.publication_date = publication_date
        self.genre = genre
        self.isbn = isbn
        self.pages = pages
        self.language = language
        self.file_format = file_format
        self.cover = cover
        self.url = url
        self.summary = summary
        self.price = price
        self.discount = discount
        self.rating = rating
        self.total_reviews = total_reviews
        self.units_sold = units_sold

    def __repr__(self) -> str:
        return f"Product: {self.title}"
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'price': self.price,
            'author' : self.author,
            'publisher' : self.publisher,
            'publication_date' : self.publication_date,
            'price' : self.price,
            'file_format' : self.file_format,
            'rating': self.rating,
            'cover': self.cover,
        }

class Order_History(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user = db.Column(db.String(64), ForeignKey('user.id'), nullable = False)
    order_time = db.Column(db.DateTime, nullable = False)
    status = db.Column(db.String(32), nullable = False, default = 'Not Processed')
    total_price = db.Column(db.Float, nullable = False)
    shipping_address = db.Column(db.String(256), nullable = False)
    billing_address = db.Column(db.String(256), nullable = False)
    shipping_method = db.Column(db.String(16), nullable = False, default = 'Standard')

    def __init__(self, user, date, status, price, ship, bill, method):
        self.user = user
        self.order_time = date
        self.status = status
        self.total_price = price
        self.shipping_address = ship
        self.billing_address = bill
        self.shipping_method = method

    def __repr__(self) -> str:
        return f"<Order_History {self.id}>"

class Order_Item(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    order_id = db.Column(db.Integer, db.ForeignKey('order__history.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    product_title = db.Column(db.String(128), nullable = False)

    def __init__(self, orderID, productID, productTitle, quantity):
        self.order_id = orderID
        self.product_id = productID
        self.product_title = productTitle
    
    def __repr__(self) -> str:
        return f"<Order_Item {self.id}>"

#Auxillary Functions
#TO-DO: Implement a check of the session's cart with the database before any merges are made, preferably through a function that would either return an error in case the product details don't match, or modifies the session with proper details while also notifying the user of any discrepencies. This is important because we need to ensure that in case data is tampered, we have a system to deal with it.
def persistNewCart() -> None:
    print("--------------OVERWRITING DATABASE CART WITH GUEST CART (NEW USER)------------------")
    updateUser = User.query.filter_by(id = current_user.id).first()
    cart_data = session['cart']
    updateUser.cart = cart_data

    flag_modified(updateUser, 'cart')
    db.session.commit()

def mergeCarts() -> None:
    ("-----------MERGING DATABASE CART WITH TEMPORARY (GUEST) CART OF EXISTING USER------------")
    targetUser = User.query.get(current_user.id)
    targetUser.cart.update(session['cart'])

    flag_modified(targetUser, 'cart')
    db.session.commit()

def addToGuestCart(productID) -> None:
    print("Adding item to guest (Temporary) cart")

    if 'Temporary_Cart' not in session:
        session['Temporary_Cart'] = []
    item = Product.query.get(productID)
    session['Temporary_Cart'].append({"id" : item.id, "title" : item.title, "author" : item.author})        

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
        #Guest user had a cart before creating an account
        if 'cart' in session:
            persistNewCart()
            print("Cart updated: New user <- Guest Cart")
            session.pop('cart')
            print(session)
            return jsonify({'message' : 'Welcome to Seneca! Your temporary cart has been stored in our database. Happy reading :)', 'redirect_url' : url_for('home')})
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
                #If guest user had a cart prior to loggin in, we need to merge both of them too
                if session['cart']:
                    mergeCarts()
                    session.pop('cart')
                    print(session)

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
                           summary = requestedProduct.summary, author = requestedProduct.author,
                           publisher = requestedProduct.publisher, publication_date = requestedProduct.publication_date,
                           isbn = requestedProduct.isbn, genre = requestedProduct.genre, pages = requestedProduct.pages, language = requestedProduct.language, file_format = requestedProduct.file_format,
                           discount = requestedProduct.discount, price = requestedProduct.price,
                           total_reviews = requestedProduct.total_reviews, url = requestedProduct.url, units_sold = requestedProduct.units_sold)

@app.route('/cart')
def cart():
    print("Cart called")
    print(session['cart'])
    return render_template("cart.html", cart = session['cart'])

@app.route('/addToCart', methods=['POST', 'GET'])
def addToCart():
    if request.method == 'POST':
        product_id = str(request.form['id'])
        print("Incoming product (API): ", product_id)

        product = Product.query.filter_by(id = product_id).first()
        #Guest user:
        if not(current_user.is_authenticated):
            print("Error: Not logged in")
            if 'cart' not in session:
                session.permanent = True
                session['cart'] = {}
                session['cart'].update({product_id : {"title" : product.title, "author" : product.author, "isbn" : product.isbn, "file format" : product.file_format, "price" : product.price, "discount" : product.discount}})
                session.modified = True
                return jsonify({'message' : "It appears you are using Seneca as a guest. While we do allow guest purchases, please note that your session data, including your cart, is only stored temporarily and will be deleted after inactivity :)"})

            elif product_id in session['cart']:
                print("Guest's cart already has all this shit")
                return jsonify({"message" : "Item exists in cart (temp)"})

            session['cart'].update({product_id : {"title" : product.title, "author" : product.author, "isbn" : product.isbn, "file format" : product.file_format, "price" : product.price, "discount" : product.discount}})
            print(session)
            session.modified = True

            return jsonify({"message" : 'Ye le bc guest saala mkc teri'})
        
        #Logged in user:
        targetUser = User.query.filter_by(id = current_user.id).first()
        print(targetUser.cart)
        print("/addToCart: Current Cart")

        if product_id in targetUser.cart:
            print("This item already exists in your cart")
            return jsonify({'message' : 'Product already in cart'})
        else:
            targetUser.cart.update({product_id : {"title" : product.title, "author" : product.author, "isbn" : product.isbn, "file format" : product.file_format, "price" : product.price, "discount" : product.discount}})
            print(targetUser.cart)

            flag_modified(targetUser, 'cart')
            db.session.commit()
            print(User.query.get(current_user.id).cart)

        return jsonify({'message' : 'Product added to cart'})

@app.route('/purchaseThenCheckout', methods=['POST', 'GET'])
def purchaseThenCheckout():
    if request.method == 'POST':
        product_id = str(request.form['id'])
        product = Product.query.filter_by(id = product_id).first()
        #Guest user:
        if not(current_user.is_authenticated):
            print("Error: Not logged in")
            if 'cart' not in session:
                session.permanent = True
                session['cart'] = {}
                # session['cart'].update({product_id : {"title" : product.title, "author" : product.author, "isbn" : product.isbn, "file format" : product.file_format, "price" : product.price, "discount" : product.discount}})
                # return redirect(url_for('cart'))

            elif product_id in session['cart']:
                print("Guest's cart already has all this shit")
                return jsonify({"message" : "Item exists in cart (temp)"})

            session['cart'].update({product_id : {"title" : product.title, "author" : product.author, "isbn" : product.isbn, "file format" : product.file_format, "price" : product.price, "discount" : product.discount}})
            print(session)
            session.modified = True

            return redirect(url_for('cart'))
        
        #Logged in user:
        targetUser = User.query.filter_by(id = current_user.id).first()
        print(targetUser.cart)
        print("/Direct Purchase: Current Cart")

        if product_id in targetUser.cart:
            print("This item already exists in your cart")
            return jsonify({'message' : 'Product already in cart'})
        else:
            targetUser.cart.update({product_id : {"title" : product.title, "author" : product.author, "isbn" : product.isbn, "file format" : product.file_format, "price" : product.price, "discount" : product.discount}})
            print(targetUser.cart)

            flag_modified(targetUser, 'cart')
            db.session.commit()
            print(User.query.get(current_user.id).cart)

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
        print(item.title, item.price, item.rating, item.cover, item.summary, item.price)
    products_list = [item.to_dict() for item in products]
    return jsonify(products_list)

@app.route("/logout")
def amd():
    session.clear()
    print(session)
    return redirect(url_for('signup'))

@app.route("/checkout", methods = ['POST', 'GET'])
def checkout():
    return render_template("checkout.html", cart = session['cart'])
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port = 6900)