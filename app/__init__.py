import os

STEAM_API_KEY = os.getenv("STEAM_API_KEY")


from flask import Flask

app = Flask(__name__)

from app import routes