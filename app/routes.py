from flask import render_template, request, redirect, url_for, flash, session
from app import app, db
from app.utils.insights import *
from app.utils.fetch_player_data import *
from app.utils.api import PrivateAccount
import random
from werkzeug.security import generate_password_hash, check_password_hash
from app.security import *
from flask_login import login_user, login_required
from app.models import User, Steam_User


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

@app.route('/view')
def view():
    if 'user_id' not in session:
        flash("Please log in to access SteamWrapped's features.", "warning")
        return redirect(url_for('login'))
    return render_template('main/view.html')

@app.route('/share')
def share():
    if 'user_id' not in session:
        flash("Please log in to access SteamWrapped's features.", "warning")
        return redirect(url_for('login'))
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

    # Pass the steam_id to the template
    return render_template(
        'main/profile.html'
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
