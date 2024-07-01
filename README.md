# Seneca: Where every story matters

## About
Seneca is a mini-project that I undertook as a way to practice Flask, SQLAlchemy, and APIs, among other skills that I wish to hone.
Inspired by Kindle, Seneca serves a simple purpose: To provide a platform to purchase and archive e-books. 

## Installation Guide
1) Clone this repository:
```sh
    git clone https://github.com/parthacharyaaaaa/seneca.git
```

2) Change directories to the project package:
```sh
  cd Seneca
```
3) Activate virtual environment:
```sh
  python -m venv venv
  venv\Scripts\activate
```
4) Install all dependencies:
```sh
pip install -r requirements.txt
```
Note: This installation assumes you already have Python and it's included modules, such as secrets, re, os, etc.

5) Set up database: This can be done either manually by creating an instance folder and making a database, using Flask-Migrate, or through run.py itself.
The second approach is as follows:
```sh
flask db upgrade
```
And the third approach will look like this:
```sh
from Seneca import app, db
if __name__ == "__main__":
  with app.app_context():
    db.create_all()
  app.run(port=2000)
#Port can, of course, be changed.
```
6) Configuration:
The relevan configurations for the Flask app have been written within the app factory itself. It is important to set the configurations under the config section in the ```__init__.py``` file before attempting to run the application

8) Run the application:
```sh
flask run
```
or
```sh
python (your directory name)/run.py
```

## Usage Instructions
Once you have set up the Seneca application, navigate to `http://127.0.0.1:2000` (change port 2000 if needed). You can then start using the platform, which includes browsing through books, placing orders, creating yout account, adding books to favourites, managing your cart, and even mailing your order to either yourself or to a friend :D

## Features
- Account creation
- User Authentication and Authorization
- Page Responsiveness to different screen sizes, all done through CSS3 media queries
- Browsing books on the catalogue page
- Searching, sorting and filtering of products based on a plethora of factors, such as price and number of pages.
- Adding books to a favourites list
- Adding books to a cart, which is stored either centrally like the favourites list, or for guest users, is stored using Flask session
- Feedback system to report bugs, ask for features, queries, legal, etc
- Review and rate products based on your experience, and read the reviews and ratings of different Seneca users
- Place orders, either directly downloading a .zip file of the books you have added to your cart, or mailing the .zip file to an email address.
- Email notifications, which include welcome messages sent upon account creation, as well as detailed email receipts of purchases for record-keeping

## Closing thoughts
Seneca is far from perfect, but through this project, I have improved considerably from the last Flask application I had made (which was my first ever 'project', per say). For any feedback about Seneca, either any suggestions, bug reports, or whatever it might be, my email is:
1008parth@gmail.com

(Please flag your email with ```Seneca-Review``` so it does not get lost)

Thank you
