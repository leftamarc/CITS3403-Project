import os
import sys
from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from app.config import Config
from flask_login import LoginManager 



#Checks for STEAM_API_KEY
STEAM_API_KEY = os.getenv("STEAM_API_KEY")
if not STEAM_API_KEY:
    print("Error: STEAM_API_KEY environment variable is not set.")
    sys.exit(1)

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Initialise flask-login
login_manager = LoginManager()
login_manager.login_view = '/login'  # Set default login view
login_manager.init_app(app)


# Generate secret key 
app.config['SECRET_KEY'] = os.urandom(24)


# Define the user_loader function
from app.models import User
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))  

# Initialise limiter
limiter = Limiter(
    key_func=get_remote_address,
    app =app,
    default_limits=["200 per day", "50 per hour"],
)
limiter.init_app(app)
from app import routes, models
