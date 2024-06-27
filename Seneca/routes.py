from Seneca.models import User, Product, Feedback, Review, Order_History, Order_Item
from flask import jsonify, redirect, request, render_template, session, url_for, send_file
from flask_login import login_required, login_user, current_user, logout_user
from sqlalchemy import or_
from sqlalchemy.orm.attributes import flag_modified

from Seneca.mail_sender import sendReceipt, sendSalutation, sendOrder
from Seneca.utils import *
from Seneca.models import User, Product, Review, Feedback, Order_History, Order_Item
from Seneca.forms import SignupForm, LoginForm, FeedbackForm, ReviewForm

from Seneca import db
from Seneca import app
from Seneca import bcrypt
from Seneca import login_manager

from datetime import timedelta, datetime
import re as regex
import concurrent.futures

#Login redirection endpoint
@login_manager.user_loader
def loadUser(user_id):
    return User.query.filter_by(id=user_id).first()

#Endpoints
@app.route("/templatetest")
def template():
    return render_template('baseTemplate.html', signedIn = current_user.is_authenticated)

@app.route("/")
def home(): 
    print(current_user)
    bestSellers = Product.query.order_by(Product.units_sold.desc()).limit(6)
    bestSellers = [item.to_dict() for item in bestSellers]
    print(bestSellers)
    return render_template('home.html', signedIn = current_user.is_authenticated, bestSellers = bestSellers)

#---------------------------------------------------------------User Management
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    signupForm = SignupForm()
    if request.method == 'POST':
        if not signupForm.validate_on_submit():
            print(signupForm.errors)
            return jsonify({"alert": signupForm.errors})
        else:
            email = request.form['email_id']
            phone = str(request.form['phone_number'])
            time = request.form['formattedDateTime']

            #Handle existing user trying to sign up
            if User.query.filter_by(email_id = email).first() != None:
                return jsonify({'exists' : True,'alert' : 'A Seneca account with this email already exists'})

            elif User.query.filter_by(phone_number = phone).first() != None:
                return jsonify({'exists' : True,'alert' : 'A Seneca account with this phone number already exists'})
            
            #Register user into database
            fname = request.form['first_name']
            lname = request.form['last_name']
            age = request.form['age']
            password = request.form['password']

            hashedPassword = bcrypt.generate_password_hash(password)
            newUser = User(fname, lname, age, phone, email, hashedPassword)

            db.session.add(newUser)
            db.session.commit()

            login_user(newUser, remember=False, duration=timedelta(days=1))
            setLastSeen(time)
            
            #Sending Salutations
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(sendSalutation(current_user))

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
            else:
                print("Account made")
                return jsonify({'alert' : 'Welcome to Seneca!', 'redirect_url' : url_for('home')})
    else:
        return render_template('signup.html', form=signupForm)

@app.route("/login", methods = ['POST', 'GET'])
def login():
    loginForm = LoginForm()
    if request.method == 'POST':
        print(request.form)
        if not loginForm.validate_on_submit():
            print("Login validation failed: Backend")
            print(loginForm.errors)
            return jsonify({'alert' : 'Invalid details submitted'})
        
        identity = request.form['emailPhone']
        password = request.form['password']
        time = request.form['formattedDateTime']

        registeredUser = User.query.filter_by(email_id = identity).first() or User.query.filter_by(phone_number = identity).first()
        
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
                    'alert' : 'No account with the given email address/phone number exists with Seneca'})
    else:
        print("Rendering Login")
        return render_template('login.html', loginForm = loginForm)

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

        orderHolder = {}
        orderHistory = Order_History.query.filter_by(user = target.id).all()
        for orders in orderHistory:
            orderHistoryItems = Order_Item.query.filter_by(order_id = orders.id).all()
            orderItemHolder = [item.to_dict() for item in orderHistoryItems]
            for item in orderItemHolder:
                x = Product.query.filter_by(id = item['product_id']).first()
                item.update({"title" : x.title,"author": x.author, "isbn" : x.isbn})

            orderHolder[orders.id] = {
                'order_id': orders.id,
                'time_of_purchase': orders.order_time,
                'total_items': orders.order_quantity,
                'total_amount': orders.total_price,
                'items': orderItemHolder
            }
        return jsonify({"user_info" : userInfo, "order_info" : orderHolder, "fav_info" : favourites})

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

#------------------------------------------------------------------Cart Management
@app.route("/products", methods=['GET'])
def product():
    reviewForm = ReviewForm()
    id = request.args.get('viewkey')
    print(id)
    requestedProduct = Product.query.filter_by(id = id).first().loadInfo()
    print(requestedProduct)
    print(current_user.is_authenticated)

    return render_template('productTemplate.html',signedIn = current_user.is_authenticated, product=requestedProduct, reviewForm = reviewForm)

@app.route('/cart')
def cart():
    fallback = loadCart()
    backup_price = 0.0
    for items in fallback.values():
        backup_price += items['price'] - items['discount']
    backup_quantity = len(fallback)
    if current_user.is_authenticated:
        if current_user.cart == []:
            return render_template('cart.html', signedIn = current_user.is_authenticated, isEmpty = True, backup_price = backup_price, backup_quantity = backup_quantity)
        else:
            return render_template('cart.html', signedIn = current_user.is_authenticated, isEmpty = False, billingEmail = current_user.email_id , backup_price = backup_price, backup_quantity = backup_quantity)
    else:
        if 'cart' not in session or session['cart'] == []:
            return render_template('cart.html', signedIn = current_user.is_authenticated, isEmpty = True, backup_price = backup_price, backup_quantity = backup_quantity)
        else:
            return render_template('cart.html', signedIn = current_user.is_authenticated, isEmpty = False, backup_price = backup_price, backup_quantity = backup_quantity)

@app.route("/remove-from-cart", methods = ['POST'])
def removeFromCart():
    if request.method == 'POST':
        productID = request.get_json().get('id')
        print(productID)
        # Logged in user
        if current_user.is_authenticated:
            current_user.cart.remove(productID)

            flag_modified(current_user, 'cart')
            db.session.commit()

        else:
            session['cart'].remove(productID)
            session.modified = True
        product = Product.query.filter_by(id = productID).first()
        return jsonify({"valid" : 1, 'new_total' : product.price - product.discount})

@app.route('/addToCart', methods=['POST'])
def addToCart():
    if request.method == 'POST':
        # print("ID: ", type(request.form['id']))
        product_id = request.form['id']
        try:
            int(product_id)
        except:
            return jsonify({"message" : "Invalid product ID"})
        product = Product.query.filter_by(id = product_id).first()
        if not product:
            return jsonify({"message" : "Error in validating product authenticity :/"})
        #Guest user:
        if not(current_user.is_authenticated):
            if 'cart' not in session:
                session.permanent = True
                session['cart'] = []
                session['cart'].append(product_id)
                session.modified = True  
                return jsonify({'message' : "It appears you are using Seneca as a guest. While we do allow guest purchases, please note that your session data, including your cart, is only stored temporarily and will be deleted after inactivity :)"})

            elif product_id in session['cart']:
                return jsonify({"message" : "Item exists in cart"})

            session['cart'].append(product_id)
            session.modified = True

            return jsonify({'added' : 1})
        
        #Logged in user:
        targetUser = User.query.filter_by(id = current_user.id).first()
        print(targetUser.cart)

        if product_id in targetUser.cart:
            return jsonify({'message' : 'Product already in cart'})
        else:
            targetUser.cart.append(product_id)
            print(targetUser.cart)

            flag_modified(targetUser, 'cart')
            db.session.commit()
            print(User.query.get(current_user.id).cart)

        return jsonify({'added' : 1})

@app.route("/get-cart", methods = ['GET'])
def getCart():
    if request.args.get('flag') == "id":
        if current_user.is_authenticated:
            return jsonify(current_user.cart)
        else:
            try:
                return jsonify(session['cart'])
            except:
                return jsonify([])
    else:
        billItems = loadCart()
        print("Final bill: ", billItems)
        return jsonify(billItems)

#-------------------------------------------------------------------Favourites Management
@app.route("/toggle-favourites", methods = ['POST'])
def toggleFav():
    if not current_user.is_authenticated:
        return jsonify({'alert' : 'You must have an account to keep favourites'})
    
    item = request.get_json().get('id')
    try:
        int(item)
    except:
        return jsonify({"message" : "Invalid product ID"})
    if item in current_user.favourites:
        (current_user.favourites).remove(item)
        print(current_user.favourites)
        flag_modified(current_user, 'favourites')
        db.session.commit()
        return jsonify({'alert' : 'Item removed from favourites', 'action' : 'remove'})
    
    else:
        (current_user.favourites).append(item)
        flag_modified(current_user, 'favourites')
        db.session.commit()
        return jsonify({'alert' : 'Item added to favourites', 'action' : 'add'})

@app.route("/get-favourites", methods = ['GET'])
def getFavs():
    if not current_user.is_authenticated:
        return jsonify({"isGuest" : 1})
    else:
        return jsonify({'favs' : current_user.favourites})
#--------------------------------------------------------------------Product Management
@app.route("/catalogue", methods=['GET'])
def catalogue():
    return render_template('catalogue.html', signedIn=current_user.is_authenticated)
     
@app.route("/get-catalogue", methods = ["GET"])
def getCatalogue():
    page=request.args.get('page', 1, type=int)
    query = Product.query
    if len(request.args) != 0:
        print(request.args)
        search = request.args.get('search')
        try:
            sort = int(request.args.get('sort_by'))
        except (TypeError, ValueError):
            sort = None
        minPrice = request.args.get('min-price')
        maxPrice = request.args.get('max-price')
        minPages = request.args.get('min-pages')
        maxPages = request.args.get('max-pages')
        if search:
            query = query.filter(
                or_(
                    Product.title.ilike(f"%{search}%"),
                    Product.author.ilike(f"%{search}%"),
                    Product.genre.ilike(f"%{search}%")
                )
            )

        if minPrice:
            query = query.filter(Product.price >= (minPrice))
        if maxPrice:
            query = query.filter(Product.price <= maxPrice)
        if minPages:
            query = query.filter(Product.pages >= minPages)
        if maxPages:
            query = query.filter(Product.pages <= maxPages)
        
        if sort == 1:
            query = query.order_by(Product.title.asc())
        elif sort == 2:
            query = query.order_by(Product.title.desc())
        elif sort == 3:
            query = query.order_by(Product.price.asc())
        elif sort == 4:
            query = query.order_by(Product.price.desc())
        elif sort == 5:
            query = query.order_by(Product.publication_date.asc())
        elif sort == 6:
            query = query.order_by(Product.publication_date.desc())
        elif sort == 7:
            query = query.order_by(Product.author.asc())
        elif sort == 8:
            query = query.order_by(Product.author.desc())
        elif sort == 9:
            query = query.order_by(Product.pages.asc())
        elif sort == 10:
            query = query.order_by(Product.pages.desc())
        
    paginatedQuery = query.paginate(page=page, per_page=8)
    books = [item.loadInfo() for item in paginatedQuery]
    print(paginatedQuery.pages, paginatedQuery.items)
    return jsonify({"books" : books,
                    "total_pages" : paginatedQuery.pages,
                    "current_page" : page,
                    "has_next" : paginatedQuery.has_next,
                    "has_prev" : paginatedQuery.has_prev,
                    "next_page" : paginatedQuery.next_num if paginatedQuery.has_next else None,
                    "prev_page" : paginatedQuery.prev_num if paginatedQuery.has_prev else None
                    })

#Order Management
@app.route("/process-order", methods = ['POST'])
def processOrder():
    data = request.get_json()
    print(data)
    action = data.get("action")
    email_regex = r"[^@]+@[^@]+\.[^@]+"

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
            order = Order_History(current_user.id, datetime.now(), "Processed", price, current_user.email_id, "Download" if action == "download" else "Mail", len(temp_storage), None if action == "download" else data.get("recipient"), None if action == "download" else data.get("message"))
            db.session.add(order)
            db.session.commit()
            # print(temp_storage)
            for item in temp_storage.keys():
                orderItem = Order_Item(order.id, int(item), temp_storage[item]['price'] - temp_storage[item]['discount'])
                Product.query.filter_by(id = int(item)).first().units_sold += 1
                db.session.add(orderItem)
            current_user.cart = []
            flag_modified(current_user, 'cart')
            db.session.commit()
            print("Order committed")

            #Generating download token
            token = generateDownloadToken(orderID=order.id, userID=current_user.id)
            order.token = token
            flag_modified(order, 'token')
            db.session.commit()

            #Sending receipt
            with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(sendReceipt(current_user.email_id, temp_storage, order))

            return jsonify({"message" : "Your order has been processed", "redirect_url" : url_for("download", order_id = order.id, download_url = token["download_url"]) if action == "download" else url_for("sendMail", order_id = order.id, download_url = token["download_url"]), "flag" : "valid"})
        #Guest Transaction
        else:
            billingEmail = data.get('billing_email')
            if billingEmail == "" or not regex.match(email_regex, billingEmail) or billingEmail == None:
                return jsonify({"alert" : "Error: Invalid billing email provided"})
            if validateCart():
                print("Processing order: guest")

                order = Order_History(None, datetime.now(), "Processed", price, billingEmail, "(Guest) Download" if action == "download" else "(Guest) Mail", len(temp_storage), None if action == "download" else data.get("recipient"), None if action == "download" else data.get("message")) 
                db.session.add(order)
                db.session.commit()

                for item in temp_storage.keys():
                    orderItem = Order_Item(order.id, int(item), temp_storage[item]['price'] - temp_storage[item]['discount'])
                    Product.query.filter_by(id = int(item)).first().units_sold += 1
                    db.session.add(orderItem)
                db.session.commit()
                print("Order committed")
                session['cart'] = []

                token = generateDownloadToken(orderID=order.id)
                order.token = token
                flag_modified(order, 'token')
                db.session.commit()

                #Sending receipt
                sendReceipt(str(billingEmail), temp_storage, order)

                return jsonify({"alert" : "Your order has been processed", "redirect_url" : url_for('download', order_id = order.id, download_url = token['download_url']) if action == "download" else url_for("sendMail", order_id = order.id, download_url = token["download_url"]), "flag" : "valid"})
            else:
                return jsonify({"alert" : "There seems to be an error with processing the items in your cart. They may be outdated, or tampered with.", "redirect_url": url_for('cart'), "flag" : "invalid"})

@app.route("/sendMail/id=<order_id>/<download_url>")
def sendMail(order_id, download_url):
    print("Final Step: Verifying Download")
    print(session)
    print(order_id, download_url)

    order = Order_History.query.filter_by(id = order_id).first()
    token = order.token
    print(token)

    if token['expiration_time'] < datetime.now().isoformat():
        print("Expired Token")
        return jsonify({'error' : "Expired Token"})
    
    if token['used'] != 0:
        print("Used token")
        return jsonify({"error" : "This token has already been redeemed"})

    if order_id != str(token['order_id']) or download_url != token['download_url']:
        print("Invalid token")
        print(type(order_id), type(token['order_id']))
        return jsonify({'error' : 'Invalid Token'})
    
    print("Processing download")

    #Creating zip file
    packageItems = Order_Item.query.filter_by(order_id = order.id).all()
    zipList = []
    print(packageItems)
    for packageItem in packageItems:
        zipList.append(Product.query.filter_by(id = packageItem.product_id).first().url)
    print(zipList)
    package = createZip(f"Seneca: Order-{order_id}", zipList)
    # print(package)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        sentOrder = executor.submit(sendOrder(order.mail_to, package, order.mail_message))
    token["used"] = 1
    flag_modified(order, "token")
    db.session.commit()
    return redirect(url_for('mailConfirmation', recipient = order.mail_to, order=order))

@app.route("/order-success")
def mailConfirmation():
    recipient = request.args.get('recipient')
    order = request.args.get('order')
    return render_template('mailSuccess.html', recipient = recipient, order = order, signedIn = current_user.is_authenticated, sender = current_user.first_name if current_user.is_authenticated else "Guest")

@app.route('/download/id=<order_id>/<download_url>')
def download(order_id, download_url):
        return render_template('download.html', signedIn = current_user.is_authenticated)

@app.route('/validate-download')
def validateDownload():
    print("Final Step: Verifying Download")
    print(session)
    order_id = str(request.args.get('order_id'))
    token_download_url = request.args.get('token_download_url')
    print(order_id, token_download_url)

    order = Order_History.query.filter_by(id = order_id).first()
    token = order.token
    print(token)

    if token['expiration_time'] < datetime.now().isoformat():
        print("Expired Token")
        return jsonify({'error' : "Expired Token"})
    
    if token['used'] != 0:
        print("Used token")
        return jsonify({"error" : "This token has already been redeemed"})

    if order_id != str(token['order_id']) or token_download_url != token['download_url']:
        print("Invalid token")
        print(type(order_id), type(token['order_id']))
        return jsonify({'error' : 'Invalid Token'})
    
    print("Processing download")

    #Creating zip file
    packageItems = Order_Item.query.filter_by(order_id = order.id).all()
    zipList = []
    print(packageItems)
    for packageItem in packageItems:
        zipList.append(Product.query.filter_by(id = packageItem.product_id).first().url)
    print(zipList)
    package = createZip(f"Seneca: Order-{order_id}", zipList)
    # print(package)
    token["used"] = 1
    flag_modified(order, "token")
    db.session.commit()
    return send_file(package, as_attachment=True, download_name=f"Seneca: Order-{order_id}.zip")

@app.route('/get-reviews', methods = ['GET'])
def getReviews():
    print("Getting reviews")
    target = int(request.args.get('id'))
    offset = int(request.args.get('offset'))

    hasMore = 0
    print(target, offset)
    reviews = Review.query.filter_by(product = target).order_by(Review.time.desc()).offset(offset*3).limit(4).all()
    if not reviews:
        return jsonify({"isEmpty" : 1})
    if len(reviews) > 3:
        hasMore = 1
    reviews = reviews[:3]
    reviews = [item.to_dict() for item in reviews]
    for item in reviews:
        item["user"] = User.query.filter_by(id = item["user"]).first().first_name 
    return jsonify({"reviews" : reviews, 'hasMore' : hasMore})

@app.route('/add-review', methods = ["POST"])
def addReview():
    print("Adding review")
    if not current_user.is_authenticated:
        return jsonify({"error" : "penis man"})
    
    targetID = int(request.form.get("id"))
    body = request.form.get("review-body")
    title = request.form.get("review-title")
    rating = float(request.form.get("rating3"))

    newReview = Review(current_user.id, targetID, rating, title, body)
    db.session.add(newReview)

    targetProduct = Product.query.filter_by(id = targetID).first()
    targetProduct.total_reviews += 1
    targetProduct.rating = (targetProduct.rating*targetProduct.total_reviews + rating)/(targetProduct.total_reviews+1)
    db.session.commit()

    return jsonify({"alert" : "review added"})

@app.route("/contact", methods=['GET', 'POST'])
def contact():
    feedbackForm = FeedbackForm()
    if request.method == "POST":
        print(feedbackForm.data)
        if feedbackForm.validate_on_submit():
            title = request.form["title"]
            email = request.form["email"]
            flag = request.form["flag"]
            query = request.form["query"]

            newFeedback = Feedback(title, query, email, flag)
            db.session.add(newFeedback)
            db.session.commit()
        return jsonify({"flag" : 1, "alert" : "Submitted Successfully"})

    else:
        return render_template("contact.html", feedbackForm=feedbackForm)
