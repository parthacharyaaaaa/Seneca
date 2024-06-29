from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate

from datetime import timedelta
import os

from dotenv import load_dotenv
#App configuration
app = Flask(__name__)

env_path = os.path.join(os.path.dirname(__file__)[:-7], "instance", ".env")
load_dotenv(env_path)

#Configs
app.secret_key = os.environ.get('SENECA_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI', default="sqlite:///instance/test1.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.environ.get('TRAACK_MODIFICATIONS', default=False)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=int(os.environ.get('SESSION_LIFETIME')))

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
csrf = CSRFProtect(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)


login_manager.login_view = "login"

from Seneca import routes