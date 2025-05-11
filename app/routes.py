from flask import render_template, request, redirect, url_for, flash, session, jsonify
from app import app, db
from app.utils.insights import *
from app.utils.fetch_player_data import *
from app.utils.api import PrivateAccount
import random
from werkzeug.security import generate_password_hash, check_password_hash
from app.security import *
from flask_login import login_user, login_required
from app.models import User, Steam_User
from app.__init__ import limiter

@app.route('/')
@app.route('/home')
def home():
    return render_template('main/home.html', username=session.get('username'))

@app.route('/get')
def get():
    if 'user_id' not in session:
        flash("Please log in to access SteamWrapped's features.", "warning")
        return redirect(url_for('login'))
    
    steam_user = Steam_User.query.filter_by(id=User.id).first()
    return render_template('main/get.html',steam_id=steam_user.steam_id if steam_user else None)


@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute", error_message="Too many logins, please try again in a minute.")
def login():
    if 'user_id' in session:
        flash('You are already logged in.', 'info')
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        remember_me = request.form.get('rememberMe')

        user = User.query.filter_by(username=username).first()
        if not user:
            flash('Username does not exist.', 'danger')
            return redirect(url_for('login'))  # Stay on the same page

        if not check_password_hash(user.password_hash, password):
            flash('Incorrect password.', 'danger')
            return redirect(url_for('login'))  # Stay on the same page

        login_user(user, remember=(remember_me == 'on'))
        session['user_id'] = user.id
        session['username'] = user.username

        flash('Login successful', 'success')
        return redirect(url_for('home'))  # Redirect after successful login

    return render_template('main/login.html')  # Show login page if method is GET


@app.route('/register', methods=['GET', 'POST'])
@limiter.limit("20 per hour", error_message="Too many registrations, please try again in a hour.")
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
        
        if not is_strong_password(password):
            flash('Password must be at least 8 characters long and include letters, numbers, and special characters.', 'danger')
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

    # Pass the steam_id to the template
    return render_template(
        'main/profile.html', username=User.query.get(session['user_id']).username
    )


@app.route('/logout', methods = ['POST'])
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('home'))

@app.route('/generate', methods=['POST'])
def generate():

    # Get the Steam ID from the form
    
    steam_id = request.form.get('steamid')

    #Uncomment this after merge I cbf'd setting up sessions when I know its in main
    '''try:
        FetchPlayerData(steam_id) 
    except PrivateAccount:
        flash("The Steam account is set to private. Please make it public to generate insights.", "error")
        return render_template('main/get.html') '''
    
    FetchPlayerData(steam_id) #delete this line during merge and uncomment above

    # Run all insight functions
    insights = [
        total_hours(steam_id),
        most_played_genre(steam_id),
        missed_easy_achievement(steam_id),
        most_played_release_year(steam_id),
        most_unloved_game(steam_id),
        avg_metacritic_score(steam_id),
        achievement_completion_rate(steam_id),
        backlog_size(steam_id),
        highest_achievements_to_hours(steam_id),
        rarest_achievement(steam_id)
    ]

    # Remove insights that failed
    successful_insights = [insight[1] for insight in insights if insight[0]]

    # Randomly select up to 8 successful insights
    selected_insights = random.sample(successful_insights, min(len(successful_insights), 8))

    ''' TODO: If there are less than 8 successful insights, flash a message about account not having enough
        steam data'''

    # Render the template with the selected insights
    return render_template('main/wrapped.html', cards=selected_insights)


@app.route('/search_users', methods=['GET'])
def search_users():
    query = request.args.get('query', '').strip()
    if not query:
        return jsonify([])  # Return an empty list if no query is provided

    # Search for users in the database (adjust based on your ORM)
    users = User.query.filter(User.username.ilike(f"%{query}%")).all()
    results = [{'id': user.id, 'username': user.username} for user in users]

    return jsonify(results)
