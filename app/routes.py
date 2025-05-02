from flask import render_template, request, redirect, url_for, flash, session
from app import app, db 
from app.models import User
from werkzeug.security import generate_password_hash, check_password_hash
from app.security import *


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

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        flash('You are already logged in.', 'info')
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        #check if user exists
        user = User.query.filter_by(username=username).first()
        if not user:
            flash('Username does not exist.' , 'danger')
            return redirect(url_for('login'))
        
        if not check_password(user.password_hash, password):
            flash('Incorrect password.', 'danger')
            return redirect(url_for('login'))
        
        #successful login
        else:
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Login successful', 'success')
            return redirect(url_for('home'))
            
        

    return render_template('main/login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        flash('You are already logged in.', 'info')
        return redirect(url_for('home'))
     
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        #check if passwords match
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('register'))
        
        #check if username already exist
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists.', 'danger')
            return redirect(url_for('register'))
        
        #new user instance
        new_user = User(username=username)
        new_user.set_password(password)

        #add the new user to the database
        db.session.add(new_user)
        db.session.commit()
        flash('Account creation successful', 'success')
        return redirect(url_for('login'))
    return render_template('main/register.html')

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        flash("Please log in to access your profile.", "warning")
        return redirect(url_for('login'))

    return render_template('main/profile.html', username=session['username'])


@app.route('/logout', methods = ['POST'])
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('home'))

@app.route('/generate')
def generate():
    return render_template('main/home.html')
    
