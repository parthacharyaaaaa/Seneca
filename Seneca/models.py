from datetime import datetime
from flask_login import UserMixin
from flask import url_for
import os
from Seneca import db
from sqlalchemy import Index, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import JSON

class User(UserMixin, db.Model):
    __tablename__ = 'users'

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

    __table_args__ = (
        Index('users_email_id', 'email_id'),
        CheckConstraint('age > 8 AND age < 100', name = 'check_age_range'),
    )

    def __init__(self, fname, lname, age, phone, email, password) -> None:
        self.first_name = fname
        self.last_name = lname
        self.age = age
        self.phone_number = phone
        self.email_id = email
        self.password = password
        self.time_created = datetime.now()
        self.last_seen = datetime.now()
    
    def __repr__(self) -> str:
        return f'<User {self.email_id}>'
    
    def to_dict(self) -> dict:
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
    __tablename__ = 'products'

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

    __table_args__ = (
        CheckConstraint('discount <= price', name = 'check_discount_against_price'),
        CheckConstraint('rating <= 5', name = 'check_max_possible_rating'),
    )


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
    
    def to_dict(self) -> dict:
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
            'cover': url_for('static', filename=f"{os.environ.get('library')}{self.cover}"),
            'genre' : self.genre,
            'discount' : self.discount,
            'reviews' : self.total_reviews,
            'sold' : self.units_sold,
            'language' : self.language
        }
    def loadInfo(self) -> dict:
        return {
            'id': self.id,
            'title': self.title,
            'price': self.price,
            'author' : self.author,
            'publisher' : self.publisher,
            'publication_date' : self.publication_date,
            'price' : self.price,
            'file_format' : self.file_format,
            'rating': round(self.rating,2),
            'cover': url_for('static', filename=f"{os.environ.get('library')}{self.cover}"),
            'genre' : self.genre,
            'discount' : self.discount,
            'reviews' : self.total_reviews,
            'sold' : self.units_sold,
            'summary' : self.summary,
            'pages' : self.pages,
            'language' : self.language
        }

class Order_History(db.Model):
    __tablename__ = 'order_history'

    id = db.Column(db.Integer, primary_key = True)
    user = db.Column(db.String(64), ForeignKey('users.id'), nullable = True)
    order_time = db.Column(db.DateTime, nullable = False)
    status = db.Column(db.String(32), nullable = False, default = 'Not Processed')
    total_price = db.Column(db.Float, nullable = False)
    billing_address = db.Column(db.String(256), nullable = False)
    order_type = db.Column(db.String(16), nullable = False, default = 'Download')
    order_quantity = db.Column(db.Integer, nullable = False)
    mail_to = db.Column(db.String(64), nullable = True)
    mail_message = db.Column(db.Text, nullable = True)

    #Retrieval Tokens
    token = db.Column(db.JSON, nullable = False, default = {})

    #Keep track of whether order has been requested
    email_requested = db.Column(db.Boolean, nullable = False, default = 0)

    __table_args__ = (
        CheckConstraint('order_quantity > 0', name = 'check_order_quantity'),
        # CheckConstraint('total_price > 0', name = 'check_order_price')
    )

    def __init__(self, user, date, status, price, bill, method, quantity, mail_to = None, mail_message = None):
        self.user = user
        self.order_time = date
        self.status = status
        self.total_price = price
        self.billing_address = bill
        self.order_type = method
        self.order_quantity = quantity
        self.mail_to = mail_to
        self.mail_message = mail_message

    def __repr__(self) -> str:
        return f"<Order_History {self.id}>"
    
    def to_dict(self) -> dict:
        return {
            "order_id" : self.id,
            "order_time" : self.order_time,
            "order_quantity" : self.order_quantity,
            "order_type" : self.order_type,
            "order_price" : self.total_price
        }

class Order_Item(db.Model):
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key = True)
    order_id = db.Column(db.Integer, db.ForeignKey('order_history.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    price = db.Column(db.Integer, nullable = False)

    def __init__(self, orderID, productID, price):
        self.order_id = orderID
        self.product_id = productID
        self.price = price

    def __repr__(self) -> str:
        return f"<Order_Item {self.id}>"
    
    def to_dict(self) -> dict:
        return {
            "order_id" : self.order_id,
            "product_id" : self.product_id,
            "price" : self.price
        }

class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key = True)
    time = db.Column(db.DateTime, nullable = False)
    user = db.Column(db.Integer, db.ForeignKey("users.id"), nullable = False)
    product = db.Column(db.Integer, db.ForeignKey("products.id"), nullable = False)
    rating = db.Column(db.Integer, nullable = False, default = 5)
    title = db.Column(db.String(33), nullable = False)
    body = db.Column(db.Text, nullable = False)


    __table_args__ = (
        CheckConstraint('rating <= 5', name = 'check_rating_max_value'),
    )

    def __init__(self, user, product, rating, title, body, time=datetime.now()):
        self.user = user
        self.product = product
        self.rating = rating
        self.title = title
        self.body = body
        self.time = time

    def __repr__(self):
        return f"<Review: {self.id} - {self.rating}>"
    
    def to_dict(self) -> dict:
        return{
            "user" : self.user,
            "product" : self.product,
            "rating" : self.rating,
            "body" : self.body,
            "title" : self.title,
            "time" : self.time
        }

class Feedback(db.Model):
    __tablename__ = "feedbacks"

    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(33), nullable = False)
    description = db.Column(db.Text, nullable = False)
    email = db.Column(db.String(32), nullable = False)
    flag = db.Column(db.String(16), nullable = True, default = "support")
    time = db.Column(db.DateTime, nullable = False)

    def __init__(self, title, description, email, flag):
        self.email = email
        self.title = title
        self.description = description
        self.flag = flag
        self.time = datetime.now()
