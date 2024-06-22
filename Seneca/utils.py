from zipfile import ZipFile as zipf
import os
import re
from datetime import datetime, timedelta
import secrets
from Seneca import db
from Seneca.models import Product, User
from flask_login import current_user
from flask import session
from sqlalchemy.orm.attributes import flag_modified

def format_receipt(book_dict, orderID, orderQuantity, orderTime, orderPrice):
    receipt_lines = []
    
    for book_id, book_info in book_dict.items():
        receipt_lines.append(f'Book ID: {book_id}')
        receipt_lines.append(f'Title: {book_info["title"]}')
        receipt_lines.append(f'Author: {book_info["author"]}')
        receipt_lines.append(f'Publisher: {book_info["publisher"]}')
        receipt_lines.append(f'Publication Date: {book_info["publication_date"]}')
        receipt_lines.append(f'File Format: {book_info["file_format"]}')
        receipt_lines.append('Genre: ')
        for items in book_info["genre"]:
            receipt_lines.append(f'{items}')
        receipt_lines.append('--------------------------------')
        receipt_lines.append(f'Price: ${book_info["price"]:.2f}')
        receipt_lines.append(f'Discount: ${book_info["discount"]:.2f}')
        receipt_lines.append('-' * 40)  # Add a separator for each book

    # Join all the lines into a single string with newlines
    receipt_string = '\n'.join(receipt_lines)
    receipt_string = f"Thank you for purchasing with Seneca! For record keeping, your order is as follows:\nOrder ID: {orderID}\tOrder Time: {orderTime}\nOrder Quantity: {orderQuantity}\tOrder Price: {orderPrice}\n" + receipt_string
    print(receipt_string)
    
    return receipt_string

def createZip(filename, contents):
    pathPrefix = os.environ.get('books')
    zipPathPrefix = os.environ.get('zip dumps')

    if not pathPrefix:
        raise ValueError("CRITICAL: ENVIRONMENT VARIABLE FOR BOOKS IS NOT SET")
    if not zipPathPrefix:
        raise ValueError("CRITICAL: ENVIRONMENT VARIABLE FOR ZIP FOLDER IS NOT SET")
    
    print(pathPrefix, zipPathPrefix)
    zip_path = os.path.join(zipPathPrefix, filename) + ".zip"
    print(zip_path)

    with zipf(zip_path, "w") as zipPackage:
        for file in contents:
            full_path = os.path.join(pathPrefix, file[1:])
            arcname = os.path.basename(full_path)
            zipPackage.write(filename=full_path, arcname=arcname)
    return zip_path

#Input validation
def validateSignup(form) -> bool:
    return (
        form['first_name'].isalpha() and
        form['last_name'].isalpha() and
        re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', form['email_id']) is not None and
        form['phone_number'].isdigit() and
        form['age'].isdigit() and
        len(form['password']) >= 8 and
        form['password'] == form['confirm_password']
    )

def valdiateLogin(form) -> bool:
    return (
        (re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', form['emailPhone']) or 
        form['phone_number'].isdigit()) and
        len(form['password']) >= 8 
    )
#Download tokens
def generateDownloadToken(orderID, userID = 'guest'):
    download_url = secrets.token_urlsafe(16)
    expiration_time = datetime.now() + timedelta(minutes=30)
    return{
        "order_id" : orderID,
        "user_id" : userID,
        "download_url" : download_url,
        "expiration_time" : expiration_time.isoformat(),
        "used" : 0
    }

#Logout function
def setLastSeen(time) -> None:
    print(time, datetime.now())
    date_format = "%m/%d/%Y, %I:%M:%S %p"
    time = datetime.strptime(time, date_format)
    current_user.last_seen = time
    db.session.commit()

#Cart Management
def loadCart() -> dict:
    if current_user.is_authenticated:
        itemKeys = current_user.cart
    else:
        try:
            itemKeys = session['cart']
        #Handle uninitialized session
        except KeyError as k:
            itemKeys = []

    cart = {}
    for itemKey in itemKeys:
        item = Product.query.filter_by(id = int(itemKey)).first()
        cart.update({str(item.id) : item.to_dict()})
    print(cart)
    return cart

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

def mergeCarts() -> None:
    ("-----------MERGING DATABASE CART WITH TEMPORARY (GUEST) CART OF EXISTING USER------------")
    targetUser = User.query.get(current_user.id)
    targetUser.cart = list(set(targetUser.cart + session['cart']))

    flag_modified(targetUser, 'cart')
    db.session.commit()

def persistNewCart() -> None:
    print("--------------OVERWRITING DATABASE CART WITH GUEST CART (NEW USER)------------------")
    updateUser = User.query.filter_by(id = current_user.id).first()
    cart_data = session['cart']
    updateUser.cart = cart_data

    flag_modified(updateUser, 'cart')
    db.session.commit()