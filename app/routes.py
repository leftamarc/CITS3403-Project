from flask import render_template
from app import app

@app.route('/')
@app.route('/home')
def home():
    return render_template('main/home.html')

@app.route('/get')
def get():
    return render_template('main/get.html')

@app.route('/view')
def view():
    return render_template('main/view.html')

@app.route('/share')
def share():
    return render_template('main/share.html')

@app.route('/login')
def login():
    return render_template('main/login.html')

@app.route('/register')
def register():
    return render_template('main/register.html')

@app.route('/generate')
def generate():
    return render_template('main/register.html')
    