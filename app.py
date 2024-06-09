#Import dependencies
from flask import Flask, jsonify, redirect, request, render_template, session, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_required, login_user, current_user, LoginManager, logout_user
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy import ForeignKey
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy.orm import load_only

from datetime import timedelta, datetime
import re as regex
    
#App configuration
app = Flask(__name__)
app.secret_key = 'ABCD'
app.permanent_session_lifetime = timedelta(hours=6)

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

    cart = db.Column(JSON, nullable = False, default = [])
    favourites = db.Column(JSON, nullable = True, default= [])

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
    
    def to_dict(self):
        return{
        "first_name" : self.first_name,
        "last_name" : self.last_name,
        "phone_number" : self.phone_number,
        "email_id" : self.email_id,
        "time_created" : self.time_created
        }
    
    def getItemsTotal(self) -> float:
        print("Calulating bill total: backend")
        total = 0.0
        for items in self.cart.values():
            total += items['price']
            if items['discount']:
                total -= items['discount']
        print(total)
        return total

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
            'cover': url_for('static', filename=self.cover),
            'genre' : self.genre,
            'discount' : self.discount,
            'reviews' : self.total_reviews,
            'sold' : self.units_sold
        }

class Order_History(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user = db.Column(db.String(64), ForeignKey('user.id'), nullable = True)
    order_time = db.Column(db.DateTime, nullable = False)
    status = db.Column(db.String(32), nullable = False, default = 'Not Processed')
    total_price = db.Column(db.Float, nullable = False)
    receipt_email = db.Column(db.String(256), nullable = True)
    billing_address = db.Column(db.String(256), nullable = False)
    order_type = db.Column(db.String(16), nullable = False, default = 'Personal')
    order_quantity = db.Column(db.Integer, nullable = False)

    def __init__(self, user, date, status, price, receipt, bill, method, quantity):
        self.user = user
        self.order_time = date
        self.status = status
        self.total_price = price
        self.receipt_email = receipt
        self.billing_address = bill
        self.order_type = method
        self.order_quantity = quantity

    def __repr__(self) -> str:
        return f"<Order_History {self.id}>"
    
    def to_dict(self):
        return {
            "order_id" : self.id,
            "order_time" : self.order_time,
            "order_quantity" : self.order_quantity,
            "order_type" : self.order_type,
            "order_price" : self.total_price
        }

class Order_Item(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    order_id = db.Column(db.Integer, db.ForeignKey('order__history.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    price = db.Column(db.Integer, nullable = False)

    def __init__(self, orderID, productID, price):
        self.order_id = orderID
        self.product_id = productID
        self.price = price

    def __repr__(self) -> str:
        return f"<Order_Item {self.id}>"
    
    def to_dict(self):
        return {
            "order_id" : self.order_id,
            "product_id" : self.product_id,
            "price" : self.price
        }

#Auxillary Functions
def loadCart() -> dict:
    if current_user.is_authenticated:
        itemKeys = current_user.cart
    else:
        itemKeys = session['cart']

    cart = {}
    for itemKey in itemKeys:
        item = Product.query.filter_by(id = int(itemKey)).first()
        cart.update({str(item.id) : item.to_dict()})
    print(cart)
    return cart

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
    targetUser.cart = list(set(targetUser.cart + session['cart']))

    flag_modified(targetUser, 'cart')
    db.session.commit()

def validateCart() -> bool:
    print("ValidateCart called")
    if 'cart' not in session:
        return True
    
    for productID in session['cart']:
        print(productID)
        cleanProduct = Product.query.filter_by(id = int(productID)).first()
        
        if cleanProduct:
            print(f"Product {productID} exists")
        else:
            print(f"Product not found in database. Outdated/Tampered data detected")
            session['cart'].pop(productID)
            return False
    print("ValidateCart ended")
    return True

def setLastSeen(time) -> None:
    print(time, datetime.now())
    date_format = "%m/%d/%Y, %I:%M:%S %p"
    time = datetime.strptime(time, date_format)
    current_user.last_seen = time
    db.session.commit()
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
        time = request.form['formattedDateTime']

        #Handle existing user trying to sign up
        if User.query.filter_by(email_id = email).first() != None:
            print("User already exists (email)")
            flash("This email and/or phone number already exists")

            return jsonify({'exists' : True,
                            'alert' : 'A Haki account with this email already exists'})
        elif User.query.filter_by(phone_number = phone).first() != None:
            print("User already exists (phone number)")

            return jsonify({'exists' : True,
                            'alert' : 'A Haki account with this phone number already exists'})
        
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
        setLastSeen(time)
        #Guest user had a cart before creating an account
        if 'cart' in session:
            if not validateCart():
                print("Session cart data has been tampered with (Signup)")
                return({'alert' : "Some data in your cart seems to be either outdated or tampered with. Although this may be an issue on our servers, for security measures we have removed the data in question. Please check your newly updated cart and refresh the page.", "redirect_url" : url_for('cart')})
            else:
                persistNewCart()
                print("Cart updated: New user <- Guest Cart")
                session.pop('cart')
                print(session)
                return jsonify({'alert' : 'Welcome to Seneca! Your temporary cart has been stored in our database. Happy reading :)', 'redirect_url' : url_for('home')})
       
        return jsonify({'alert' : 'Welcome to Seneca!', 'redirect_url' : url_for('home')})
    return render_template('signup.html')

@app.route("/login", methods = ['POST', 'GET'])
def login():
    if request.method == 'POST':
        identity = request.form['emailPhone']
        password = request.form['password']
        time = request.form['formattedDateTime']

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
                            'alert' : 'Error: Invalid identity syntax'})      #Ideally, this message should never pop up since input validation is performed at clinet-side itself
        
        if registeredUser:
            print("User found")
            if bcrypt.check_password_hash(registeredUser.password, password):
                print("Pass matches, authenticated")

                print(session)
                login_user(registeredUser)
                setLastSeen(time)
                
                print('logged in')
                #If guest user had a cart prior to loggin in, we need to merge both of them too
                if 'cart' in session:
                    if not validateCart():
                        print("Session cart data has been tampered with (Login)")
                        mergeCarts()
                        session.pop('cart')
                        print(session)
                        return({'alert' : "Some data in your cart seems to be either outdated or tampered with. Although this may be an issue on our servers, for security measures we have removed the data in question. Please check your newly updated cart and refresh the page.", "redirect_url" : url_for('cart')})
                    else:
                        mergeCarts()
                        session.pop('cart')
                        print(session)
                        return({'alert' : f'Your cart has been updated! Welcome back, {registeredUser.first_name}', "redirect_url" : url_for('home')})

                return({'alert' : f' Welcome back, {registeredUser.first_name}', "redirect_url" : url_for('home')})

            else:
                return jsonify({'authenticated' : False,
                                'alert' : 'Invalid credentials'})
        else:
            return jsonify({'authenticated' : False,
                    'alert' : 'No account with the given email address/phone number exists with Haki'})
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
    fallback = loadCart()
    backup_price = 0.0
    for items in fallback.values():
        print(items)
        backup_price += items['price'] - items['discount']
    backup_quantity = len(fallback)
    if current_user.is_authenticated:
        if current_user.cart == []:
            return render_template('cart.html', signedIn = current_user.is_authenticated, isEmpty = True, backup_price = backup_price, backup_quantity = backup_quantity)
        else:
            return render_template('cart.html', signedIn = current_user.is_authenticated, isEmpty = False, receiptEmail = current_user.email_id , backup_price = backup_price, backup_quantity = backup_quantity)
    else:
        if 'cart' not in session or session['cart'] == []:
            return render_template('cart.html', signedIn = current_user.is_authenticated, isEmpty = True, backup_price = backup_price, backup_quantity = backup_quantity)
        else:
            return render_template('cart.html', signedIn = current_user.is_authenticated, isEmpty = False, backup_price = backup_price, backup_quantity = backup_quantity)

@app.route("/get-catalogue", methods = ["POST", "GET"])
def getCatalogue():
    books = Product.query.all()
    if request.method == "GET":
        print("Normal catalogue, page just loaded")
        # print(books)
        # books = [item.to_dict() for item in books]
        # print(books)

    elif request.method == "POST":
        print(request.form)

        price_range_lower = request.form.get('price-range-lower')
        price_range_upper = request.form.get('price-range-upper')
        page_range_lower = request.form.get('page-range-lower')
        page_range_upper = request.form.get('page-range-upper')
        author = request.form.get('authors')
        sort_option = request.form.get('sort-option')
        print(sort_option, author)

        #Managing filtering
        #Price filters
        if price_range_lower:
            books = [item for item in books if int(price_range_lower) <= item.price]
        if price_range_upper:
            books = [item for item in books if int(price_range_upper) >= item.price]
        #Page filters
        if page_range_lower:
            books = [item for item in books if int(price_range_lower) <= item.pages]
        if page_range_upper:
            books = [item for item in books if int(price_range_upper) >= item.pages]
        #Author filter
        if author:
            books = [item for item in books if author == item.author]
        
        print("Post filter: ", books)
        
        if sort_option == '1':
            books.sort(key=lambda x: x.title.lower())
        elif sort_option == '2':
            books.sort(key=lambda x: x.title.lower(), reverse=True)
        elif sort_option == '3':
            books.sort(key= lambda x: x.price)
        elif sort_option == '4':
            books.sort(key=lambda x:x.price, reverse=True)
        elif sort_option == '5':
            books.sort(key= lambda x: x.publication_date, reverse=True)
        elif sort_option == '6':
            books.sort(key=lambda x:x.publication_date)
        elif sort_option == '7':
            books.sort(key= lambda x: x.author)
        elif sort_option == '8':
            books.sort(key=lambda x:x.author, reverse=True)
        elif sort_option == '9':
            books.sort(key= lambda x: x.pages, reverse=True)
        elif sort_option == '10':
            books.sort(key=lambda x:x.pages, reverse=False)
        else:
            pass
        
        print("Sorted List: ", books)

    books = [item.to_dict() for item in books]
    if current_user.is_authenticated:
        return jsonify({"books": books, "favourites" : current_user.favourites})
    else:
        return jsonify({"books" : books})

@app.route('/addToCart', methods=['POST', 'GET'])
def addToCart():
    if request.method == 'POST':
        product_id = str(request.form['id'])
        print("Incoming product (API): ", product_id)

        product = Product.query.filter_by(id = product_id).first()
        if not product:
            return jsonify({"message" : "Error in validating product authenticity :/"})
        #Guest user:
        if not(current_user.is_authenticated):
            print("Error: Not logged in")
            if 'cart' not in session:
                session.permanent = True
                session['cart'] = []
                session['cart'].append(product_id)
                session.modified = True  
                return jsonify({'message' : "It appears you are using Seneca as a guest. While we do allow guest purchases, please note that your session data, including your cart, is only stored temporarily and will be deleted after inactivity :)"})

            elif product_id in session['cart']:
                print("Guest's cart already has all this shit")
                return jsonify({"message" : "Item exists in cart (temp)"})

            session['cart'].append(product_id)
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
            targetUser.cart.append(product_id)
            print(targetUser.cart)

            flag_modified(targetUser, 'cart')
            db.session.commit()
            print(User.query.get(current_user.id).cart)

        return jsonify({'message' : 'Product added to cart'})

@app.route('/purchaseThenCheckout', methods=['POST', 'GET'])
def purchaseThenCheckout():
    if request.method == 'POST':
        #Get product details and query it from the database
        product_id = str(request.form['id'])
        product = Product.query.filter_by(id = product_id).first()

        #Handle case when product id is invalid
        if not product:
            return jsonify({"message" : "Error in validating product authenticity :/"})
        
        #Guest user:
        if not(current_user.is_authenticated):
            print("Error: Not logged in")
            if 'cart' not in session:
                session.permanent = True
                session['cart'] = []

            elif product_id in session['cart']:
                print("Guest's cart already has all this shit")
                return jsonify({"message" : "Item exists in cart (temp)"})

            session['cart'].append(product_id)

        #Logged in user:
        else:
            targetUser = User.query.filter_by(id = current_user.id).first()
            print(targetUser.cart)
            print("/Direct Purchase: Current Cart")

            if product_id in targetUser.cart:
                print("This item already exists in your cart")
                return jsonify({'message' : 'Product already in cart'})
            else:
                targetUser.cart.append(product_id)
                print(targetUser.cart)

                flag_modified(targetUser, 'cart')
                db.session.commit()
                print(User.query.get(current_user.id).cart)

        return redirect(url_for('checkout'))

@app.route("/catalogue")
def catalogue():
    return render_template("catalogue.html", signedIn = current_user.is_authenticated)

@app.route("/render-products", methods=['POST', 'GET'])
def render():
    products = Product.query.all()
    products_list = [item.to_dict() for item in products]
    return jsonify(products_list)

@app.route("/get-cart", methods = ['POST', 'GET'])
def getCart():
    billItems = loadCart()
    print("Final bill: ", billItems)
    return jsonify(billItems)
        
@app.route("/process-order", methods = ['POST', 'GET'])
def processOrder():
    data = request.get_json()
    print(data)
    receiptEmail = data.get('receipt_email')
    print(receiptEmail)

    email_regex = r"[^@]+@[^@]+\.[^@]+"
    if receiptEmail != "" and not regex.match(email_regex, receiptEmail):
        return jsonify({"alert" : "Invalid receipt email provided"})
    if data.get('validation') != "True":
        print("API call dirty >:(")
        return jsonify({"alert" : "Error processing order", "redirect_url" : url_for('home')})
    else:
        temp_storage = loadCart()                   #Load cart items
        #Calculate total price
        price = 0.0
        for items in temp_storage.values():
            print(items)
            price += items['price'] - items['discount']

        if current_user.is_authenticated:
            print("Processing order: user")
            order = Order_History(current_user.id, datetime.now(), "Processed", price, receiptEmail, current_user.email_id, "Personal", len(temp_storage))
            db.session.add(order)
            db.session.commit()
            print(temp_storage)
            for item in temp_storage.keys():
                orderItem = Order_Item(order.id, int(item), temp_storage[item]['price'] - temp_storage[item]['discount'])
                db.session.add(orderItem)
            current_user.cart = []
            flag_modified(current_user, 'cart')
            db.session.commit()
            print("Order committed")

            return jsonify({"message" : "Your order has been processed", "redirect_url" : url_for('download'), "flag" : "valid"})
        #Guest Transaction
        else:
            if receiptEmail != "" and not regex.match(email_regex, receiptEmail):
                return jsonify({"alert" : "Invalid receipt email provided"})
            billingEmail = data.get('billing_email')
            if receiptEmail != "" and not regex.match(email_regex, receiptEmail):
                return jsonify({"alert" : "Invalid billing email provided"})
            if validateCart():
                print("Processing order: guest")

                order = Order_History(None, datetime.now(), "Processed", price, receiptEmail, billingEmail, "(Guest) Personal", len(temp_storage))
                db.session.add(order)
                db.session.commit()

                for item in temp_storage.keys():
                    orderItem = Order_Item(order.id, int(item), temp_storage[item]['price'] - temp_storage[item]['discount'])
                    db.session.add(orderItem)
                db.session.commit()
                print("Order committed")
                session['cart'] = []

                return jsonify({"alert" : "Your order has been processed", "redirect_url" : url_for('download'), "flag" : "valid"})
            else:
                return jsonify({"alert" : "There seems to be an error with processing the items in your cart. They may be outdated, or tampered with.", "redirect_url": url_for('cart'), "flag" : "invalid"})
            
@app.route("/checkout/download", methods = ['GET'])
def download():
    return render_template('download.html', signedIn = current_user.is_authenticated)
@app.route("/gift", methods = ['GET', 'POST'])
def gift():
    data = request.get_json()
    print(data)
    receiver_email = data.get('giftEmail')
    print(receiver_email)
    return jsonify({'message' : 'called'})

@app.route("/logout", methods = ['POST'])
def logout():
    if request.method == 'POST':
        print("Logging Out user")
        if not current_user.is_authenticated:
            return jsonify({"alert" : "Error: User not logged in"})
        else:
            setLastSeen(request.get_json().get('formattedDateTime'))
            logout_user()
            session.clear()
            
            print(session)
            return jsonify({"redirect_url" : url_for('home')})

@app.route("/add-favourite", methods=["POST"])
def addFav():
    if request.method == "POST":
        print("Adding favourite")
        if not current_user.is_authenticated:
            return jsonify({"alert" : "You must have an account to add items to favourites"})
        productID = str(request.get_json().get('id'))
        if productID in current_user.favourites:
            return jsonify({"alert" : "Item already in favourites"})
        print(current_user.favourites)
        try:
            product = Product.query.filter_by(id=int(productID)).first()
        except:
            print("Item not found in db, terminating")
            return jsonify({"alert" : "error in adding item to favourites"})
        current_user.favourites.append(productID)
        
        flag_modified(current_user, 'favourites')
        db.session.commit()
        return jsonify({"alert" : "Item added"})

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template('dashboard.html', signedIn = current_user.is_authenticated)

@app.route("/get-user-info", methods = ["GET"])
@login_required
def getUserInfo():
    if request.method == "GET":
        print("Loading dashboard")

        target = User.query.filter_by(id = current_user.id).first()
        userInfo = target.to_dict()
        favourites = target.favourites
        favourites = {}
        for item in target.favourites:
            product = Product.query.filter_by(id = int(item)).first()
            favourites.update({int(item):product.to_dict()})
        # print(favourites)

        orderHolder = {}
        orderHistory = Order_History.query.filter_by(user = target.id).all()
        for orders in orderHistory:
            orderHistoryItems = Order_Item.query.filter_by(order_id = orders.id).all()

            orderHolder[orders.id] = {
                'order_id': orders.id,
                'time_of_purchase': orders.order_time,
                'total_items': orders.order_quantity,
                'total_amount': orders.total_price,
                'items': [item.to_dict() for item in orderHistoryItems]
            }
        # print(orderHolder)
        return jsonify({"user_info" : userInfo, "order_info" : orderHolder, "fav_info" : favourites})
    
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port = 6900)