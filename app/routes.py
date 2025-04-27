from flask import render_template
from app import app

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/get')
def get():
    return render_template('get.html')

@app.route('/view')
def view():
    return render_template('view.html')

@app.route('/share')
def share():
    return render_template('share.html')

@app.route('/login')
def login():
    return render_template('login.html')