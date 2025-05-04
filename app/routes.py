from flask import render_template, request, redirect, url_for, flash, session
from app import app, db 
from app.models import User, Steam_User
from werkzeug.security import generate_password_hash, check_password_hash
from app.security import *
from flask_login import login_user, login_required
from app.utils.steam_utils import GetPlayerSummaries


@app.route('/')
@app.route('/home')
def home():
    return render_template('main/home.html', username=session.get('username'))

@app.route('/get')
def get():
    steam_user = Steam_User.query.filter_by(id=User.id).first()
    return render_template('main/get.html',steam_id=steam_user.steam_id if steam_user else None)

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
        remember_me = request.form.get('rememberMe')  # Get the value of the 'remember me' checkbox
        
        # Check if the user exists
        user = User.query.filter_by(username=username).first()
        if not user:
            flash('Username does not exist.', 'danger')
            return redirect(url_for('login'))
        
        # Check if password matches
        if not check_password_hash(user.password_hash, password):
            flash('Incorrect password.', 'danger')
            return redirect(url_for('login'))
        
        # Successful login
        else:
            # Log the user in and remember them if selected
            login_user(user, remember=(remember_me == 'on'))
            
            session['user_id'] = user.id  # You can still set session data as needed
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
        
        # Check if passwords match
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('register'))
        
        # Check if username already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
            return redirect(url_for('register'))

        # Create new user instance
        new_user = User(username=username)
        new_user.set_password(password)

        # Add the new user to the database
        db.session.add(new_user)
        db.session.commit()
        
        flash('Account creation successful', 'success')
        return redirect(url_for('login'))

    return render_template('main/register.html')


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        flash("Please log in to access your profile.", "warning")
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])

    # Check if the user has a linked Steam ID
    steam_user = Steam_User.query.filter_by(id=user.id).first()

    if request.method == 'POST':
        steam_id = request.form['steam_id']
        
        # Call GetPlayerSummaries to fetch the profile data for the given Steam ID
        try:
            steam_id, username, avatar_url = GetPlayerSummaries(steam_id)
        except Exception as e:
            flash(f"Error fetching Steam profile data: {e}", "danger")
            return redirect(url_for('profile'))
        
        # Check if Steam ID already exists (if enforcing uniqueness)
        existing_steam_user = Steam_User.query.filter_by(steam_id=steam_id).first()
        if existing_steam_user:
            flash('Steam ID is already linked to another account.', 'danger')
            return redirect(url_for('profile'))
        
        # If there is no existing linked Steam ID, create a new one
        if not steam_user:
            # Create a new Steam user instance and link it to the current user
            bound_steam_id = Steam_User(steam_id=steam_id, username=username, avatar_url=avatar_url, id=user.id)
            db.session.add(bound_steam_id)
            db.session.commit()
            flash('Steam ID link successful', 'success')
        else:
            # If a Steam ID is already linked, update it
            steam_user.steam_id = steam_id
            steam_user.username = username
            steam_user.avatar_url = avatar_url
            db.session.commit()
            flash('Steam ID updated successfully', 'success')

        return redirect(url_for('profile'))

    # Pass the steam_id and user info from the database if available
    return render_template('main/profile.html', steam_id=steam_user.steam_id if steam_user else None, 
                           username=user.username if steam_user else None)



@app.route('/logout', methods = ['POST'])
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('home'))

@app.route('/generate')
def generate():
    return render_template('main/home.html')
    
