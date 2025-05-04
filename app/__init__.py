import os
import sys
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from app.config import Config

#Checks for STEAM_API_KEY
STEAM_API_KEY = os.getenv("STEAM_API_KEY")
if not STEAM_API_KEY:
    print("Error: STEAM_API_KEY environment variable is not set.")
    sys.exit(1)

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#generate secret key 
app.config['SECRET_KEY'] = os.urandom(24)
from app import routes, models
