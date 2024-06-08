#Import dependencies
from flask import Flask, jsonify, redirect, request, render_template, session, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_required, login_user, current_user, LoginManager
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

    cart = db.Column(JSON, nullable = False, default = {})
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
            'discount' : self.discount
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
    product_title = db.Column(db.String(128), nullable = False)
    product_price = db.Column(db.Float, nullable = False)

    def __init__(self, orderID, productID, productTitle, price):
        self.order_id = orderID
        self.product_id = productID
        self.product_title = productTitle
        self.product_price = price
    
    def __repr__(self) -> str:
        return f"<Order_Item {self.id}>"
    
    def to_dict(self):
        return {
            "product_id" : self.product_id,
            "product_title" : self.product_title,
            "product_price" : self.product_price,
        }

#Auxillary Functions
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

    product = Product.query.get(productID)
    session['cart'].update({productID : {"title" : product.title, "author" : product.author, "isbn" : product.isbn, "file format" : product.file_format, "price" : product.price, "discount" : product.discount}})
    session.modified = True   

def validateCart() -> bool:
    if 'cart' not in session:
        return True
    
    for productID, productDetails in session['cart'].items():
        print(productID, productDetails)
        cleanProduct = Product.query.filter_by(
            id = productID,
            title = productDetails['title'],
            author = productDetails['author'],
            file_format = productDetails['file format'],
            price = productDetails['price']
        ).first()
        
        if cleanProduct:
            print(f"Product {productID} exists")
        else:
            print(f"Product not found in database. Outdated/Tampered data detected")
            del session['cart'][productID]
            return False
    return True
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
            if not validateCart():
                print("Session cart data has been tampered with (Signup)")
                return({'message' : "Some data in your cart seems to be either outdated or tampered with. Although this may be an issue on our servers, for security measures we have removed the data in question. Please check your newly updated cart and refresh the page.", "redirect_url" : url_for('cart')})
            else:
                persistNewCart()
                print("Cart updated: New user <- Guest Cart")
                session.pop('cart')
                print(session)
                return jsonify({'alert' : 'Welcome to Seneca! Your temporary cart has been stored in our database. Happy reading :)', 'redirect_url' : url_for('home')})
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
    if current_user.is_authenticated:
        if current_user.cart == {}:
            return render_template('cart.html', signedIn = current_user.is_authenticated, isEmpty = True)
        else:
            return render_template('cart.html', signedIn = current_user.is_authenticated, isEmpty = False, cart = current_user.cart)
    else:
        if 'cart' not in session or session['cart'] == {}:
            return render_template('cart.html', signedIn = current_user.is_authenticated, isEmpty = True)
        else:
            return render_template('cart.html', signedIn = current_user.is_authenticated, isEmpty = False, cart = session['cart'])

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
        #Guest user:
        if not(current_user.is_authenticated):
            print("Error: Not logged in")
            if 'cart' not in session:
                session.permanent = True
                session['cart'] = {}
                addToGuestCart(product_id)
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

            elif product_id in session['cart']:
                print("Guest's cart already has all this shit")
                return jsonify({"message" : "Item exists in cart (temp)"})

            addToGuestCart(product_id)

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
    return render_template("catalogue.html", signedIn = current_user.is_authenticated)

@app.route("/render-products", methods=['POST', 'GET'])
def render():
    products = Product.query.all()
    products_list = [item.to_dict() for item in products]
    return jsonify(products_list)

@app.route("/get-bill", methods = ['POST', 'GET'])
def getBill():
    print("Generating bill")
    billItems = []
    if current_user.is_authenticated:
        print(current_user.cart)
        for item in current_user.cart.values():
            billItems.append(item)
    else:
        print(session['cart'])
        for item in session['cart'].values():
            billItems.append(item)

    print("Reached flag 2")
    print(billItems)
    return jsonify(billItems)
        
@app.route("/process-order", methods = ['POST', 'GET'])
def processOrder():
    data = request.get_json()
    print(data)
    receiptEmail = data.get('receipt_email')
    print(receiptEmail)
    if data.get('validation') != "True":
        print("API call dirty >:(")
        return jsonify({"alert" : "Error processing order", "redirect_url" : url_for('home')})
    else:
        if current_user.is_authenticated:
            print("Processing order: user")
            price = current_user.getItemsTotal()
            order = Order_History(current_user.id, datetime.now(), "Processed", price, receiptEmail, current_user.email_id, "Personal", len(current_user.cart))
            db.session.add(order)
            db.session.commit()

            for items in current_user.cart.keys():
                orderItem = Order_Item(order.id, int(items), current_user.cart[items]['title'], current_user.cart[items]['price'] - current_user.cart[items]['discount'])
                db.session.add(orderItem)
            current_user.cart = {}
            flag_modified(current_user, 'cart')
            db.session.commit()
            print("Order committed")

            return jsonify({"message" : "Your order has been processed", "redirect_url" : url_for('download'), "flag" : "valid"})
        else:
            billingEmail = data.get('billing_email')
            if validateCart():
                print("Processing order: user")
                price = 0.0
                for items in session['cart'].values():
                    price += items['price']
                    if items['discount']:
                        price -= items['discount']
                print(price)

                order = Order_History(None, datetime.now(), "Processed", price, receiptEmail, billingEmail, "Standard")
                db.session.add(order)
                db.session.commit()

                for items in session['cart'].keys():
                    orderItem = Order_Item(order.id, int(items), session['cart'][items]['title'])
                    db.session.add(orderItem)
                db.session.commit()
                print("Order committed")

                del session['cart']

                return jsonify({"alert" : "Your order has been processed", "redirect_url" : url_for('download'), "flag" : "valid"})
            else:
                return jsonify({"alert" : "There seems to be an error with processing the items in your cart. They may be outdated, or tampered with.", "redirect_url": url_for('cart'), "flag" : "invalid"})
            
@app.route("/checkout/download", methods = ['GET'])
def download():
    return render_template('download.html')

@app.route("/gift", methods = ['GET', 'POST'])
def gift():
    data = request.get_json()
    print(data)
    receiver_email = data.get('giftEmail')
    print(receiver_email)
    return jsonify({'message' : 'called'})

@app.route("/logout")
def amd():
    session.clear()
    print(session)
    return redirect(url_for('signup'))

@app.route("/checkout", methods = ['POST', 'GET'])
def checkout():
    #Logged in users
    if current_user.is_authenticated:
        return render_template("checkout.html", cart = User.query.get(current_user.id).cart, receiptEmail = current_user.email_id, signedIn = current_user.is_authenticated)
    else:
        try:
            return render_template("checkout.html", cart = session['cart'])
        except KeyError as k:
            return jsonify({"Error" : f"No cart. err_msg: {k}"})

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
        print(favourites)

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
        print(orderHolder)
        return jsonify({"user_info" : userInfo, "order_info" : orderHolder, "fav_info" : favourites})
    
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port = 6900)