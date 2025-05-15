import os
import sys
from flask import Flask, session
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from app.config import Config
 


# Initialise extensions
db = SQLAlchemy()
migrate = Migrate()
limiter = Limiter(key_func=get_remote_address, default_limits=["600 per day", "300 per hour"])

# Checks for STEAM_API_KEY
STEAM_API_KEY = os.getenv("STEAM_API_KEY")
if not STEAM_API_KEY:
    print("Error: STEAM_API_KEY environment variable is not set.")
    sys.exit(1)


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # set secret key
    app.config['SECRET_KEY'] = b'\x07\xce]\x8fC\xe0\x17\xae6\xfd\xff\x1b\xe5yZd\x88z`\x88\t+O\x0b'

    db.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)

    # Define the user_loader function
    from app.models import User
    
    from app.blueprint import blueprint
    app.register_blueprint(blueprint)
    

    return app




