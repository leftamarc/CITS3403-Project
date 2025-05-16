from flask import render_template, request, redirect, url_for, flash, session, jsonify
from app import db
from app.utils.insights import *
from app.utils.fetch_player_data import *
from app.utils.save_a_collection import *
from app.utils.share_a_collection import *
from app.utils.delete_wrapped_data import *
from app.utils.api import PrivateAccount
import random
from werkzeug.security import check_password_hash
from app.security import *
from app.models import User, Steam_User, saved_collections, saved_cards, shared_collections
from app.__init__ import limiter
from app.blueprint import blueprint


@blueprint.route('/')
@blueprint.route('/home')
def home():
    return render_template('main/home.html', username=session.get('username'))


@blueprint.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute", error_message="Too many logins, please try again in a minute.")
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        remember_me = form.remember.data
        print(f"Remember Me checked? {remember_me}")


        user = User.query.filter_by(username=username).first()
        if not user:
            flash('Username does not exist.', 'danger')
            return redirect(url_for('main.login'))  

        if not check_password_hash(user.password_hash, password):
            flash('Incorrect password.', 'danger')
            return redirect(url_for('main.login')) 
        
        session['user_id'] = user.id
        session['username'] = user.username
        session.permanent = remember_me 

        return redirect(url_for('main.home'))  

    return render_template('main/login.html', form=form)  # Show login page if method is GET


@blueprint.route('/register', methods=['GET', 'POST'])
@limiter.limit("20 per hour", error_message="Too many registrations, please try again in a hour.")
def register():
    if session.get('user_id'):
        flash('You are already logged in.', 'info')
        return redirect(url_for('main.home'))
    
    form = RegisterForm()
     
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        confirm_password = form.confirm_password.data
        
        # Check if passwords match
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('main.register'))
        
        if not is_strong_password(password):
            flash('Password must be at least 8 characters long and include letters, numbers, and special characters.', 'danger')
            return redirect(url_for('main.register'))
        
        # Check if username already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
            return redirect(url_for('main.register'))

        # Create new user instance
        new_user = User(username=username)
        new_user.set_password(password)

        # Add the new user to the database
        db.session.add(new_user)
        db.session.commit()
        
        flash('Account creation successful', 'success')
        return redirect(url_for('main.login'))

    return render_template('main/register.html', form=form)


@login_needed
@blueprint.route('/logout', methods = ['POST'])
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('main.profile'))


@login_needed
@blueprint.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    
    user_id = session['user_id']
    user_saved_collections = db.session.query(
        saved_collections, Steam_User.image
    ).join(
        Steam_User, saved_collections.steam_id == Steam_User.steam_id
    ).filter(
        saved_collections.id == user_id
    ).all()

    user_shared_collections = db.session.query(
        shared_collections.saved_id,
        saved_collections.title,
        saved_collections.date_created,
        saved_collections.steam_id,
        User.username.label("creator_username"),  # Get the creator's username
        Steam_User.image
    ).join(
        saved_collections, shared_collections.saved_id == saved_collections.saved_id
    ).join(
        User, saved_collections.id == User.id  # Join with creator's user row
    ).join(
        Steam_User, saved_collections.steam_id == Steam_User.steam_id
    ).filter(
        shared_collections.id == user_id  # Only show shared collections for this user
    ).all()

    # Pass the username and saved collections to the template
    return render_template(
        'main/profile.html', 
        username=User.query.get(user_id).username,
        saved_collections=user_saved_collections,
        shared_collections=user_shared_collections
    )


@blueprint.route('/get')
@login_needed
def get():

    steam_user = Steam_User.query.filter_by(id=User.id).first()
    return render_template('main/get.html',steam_id=steam_user.steam_id if steam_user else None)


@login_needed
@blueprint.route('/generate', methods=['POST'])
def generate():

    # Get the Steam ID from the form
    
    steam_id = request.form.get('steamid')
    
    if not steam_id.isdigit() or len(steam_id) != 17:
        flash("Invalid Steam ID. Please enter a 17-digit numerical Steam ID.", "danger")
        return render_template('main/get.html')

    try:
        FetchPlayerData(steam_id) 
    except PrivateAccount:
        flash("The steam account associated with the provided steam ID is set to private. Please make it public to generate insights.", "danger")
        return render_template('main/get.html')
    


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
        rarest_achievement(steam_id),
        preference_for_game_age(steam_id),
        taste_breaker(steam_id),
        favorite_publisher(steam_id),
        least_fav_genre(steam_id),
        genre_synergy(steam_id),
        metacritic_vs_playtime(steam_id), 
        genre_metacritic_influence(steam_id), 
        never_achieve(steam_id),
        they_got_stuck_at_the_tutorial(steam_id),
        most_skilled_genre(steam_id)
        
    ]

   
    # Remove insights that failed
    successful_insights = [insight[1] for insight in insights if insight[0]]

    # Randomly select up to 8 successful insights
    selected_insights = random.sample(successful_insights, min(len(successful_insights), 8))
    session['cards'] = selected_insights
    session['steam_id'] = steam_id

    ''' TODO: If there are less than 8 successful insights, flash a message about account not having enough
        steam data'''

    current_time = datetime.now()

    # Render the template with the selected insights
    return render_template('main/wrapped.html', cards=selected_insights, steam_id=steam_id, current_time=current_time)


@login_needed
@blueprint.route('/save_cards', methods=['POST'])
def save_collection_route():
    id = session.get('user_id')
    steam_id = session['steam_id']
    cards = session.get('cards')
    title = request.form.get('title')

    response = save_a_collection(id, steam_id, cards, title)
    flash(response['message'], 'success' if response['status'] == 'success' else 'danger')
    return redirect(url_for('main.profile'))  # Redirect to a relevant page after saving


@login_needed
@blueprint.route('/share_cards', methods=['POST'])
def share_collection_route():
    creator_id = session.get('user_id')

    recipient_username = request.form.get('search_username')

    recipient_user = User.query.filter_by(username=recipient_username).first()
    if not recipient_user:
        flash("Could not find a user with that username.", "danger")
        return redirect(url_for('main.profile'))
    
    recipient_id = recipient_user.id
    saved_id = request.form.get('saved_id')
    
    if creator_id == recipient_id:
        flash("You cannot share your collection with yourself.", "warning")
        return redirect(url_for('main.profile'))

    response = share_a_collection(recipient_id, saved_id)
    # Check the status of the response
    if response['status'] == 'error' or response == 'warning':
        flash(response['message'], response['status'])
        return redirect(url_for('main.profile'))
    
    flash(response['message'], response['status'])
    return redirect(url_for('main.profile'))

@login_needed
@blueprint.route('/view_saved/<int:saved_id>', methods=['GET'])
def view_saved(saved_id):
    # Fetch the saved collection by its ID and ensure it belongs to the logged-in user
    collection = saved_collections.query.filter_by(saved_id=saved_id, id=session['user_id']).first()
    if not collection:
        flash("Collection not found or you do not have permission to view it.", "danger")
        return redirect(url_for('main.profile'))

    # Fetch all cards associated with this collection
    cards = saved_cards.query.filter_by(saved_id=saved_id).all()

    # Check if the 'share' query parameter is present in the URL
    share_modal = request.args.get('share') == 'true'

    # Render the card in a similar design to wrapped.html
    return render_template(
        'main/view_saved.html',
        collection=collection,
        cards=cards,
        current_time=collection.date_created.strftime('%Y-%m-%d %H:%M:%S'),
        share_modal=share_modal,  # Pass the share_modal flag
    )


@login_needed
@blueprint.route('/view_shared/<int:saved_id>', methods=['GET'])
def view_shared(saved_id):
    # Fetch the saved collection and join to get the creator's username
    result = db.session.query(
        saved_collections,
        User.username.label("creator_username")
    ).join(
        User, saved_collections.id == User.id
    ).filter(
        saved_collections.saved_id == saved_id
    ).first()

    if not result:
        flash("Collection not found or you do not have permission to view it.", "danger")
        return redirect(url_for('main.profile'))

    collection = result.saved_collections
    creator_username = result.creator_username

    # Fetch all cards associated with this collection
    cards = saved_cards.query.filter_by(saved_id=saved_id).all()

    return render_template(
        'main/view_shared.html',
        collection=collection,
        cards=cards,
        creator_username=creator_username,
        current_time=collection.date_created.strftime('%Y-%m-%d %H:%M:%S'),
    )



@login_needed
@blueprint.route('/search_users', methods=['GET'])
def search_users():
    query = request.args.get('query', '').strip()
    if not query:
        return jsonify([])  # Return an empty list if no query is provided

    # Search for users in the database (adjust based on your ORM)
    users = User.query.filter(User.username.ilike(f"%{query}%")).all()
    results = [{'id': user.id, 'username': user.username} for user in users]

    return jsonify(results)


@blueprint.route('/delete_wrapped', methods=['POST'])
@login_needed
def delete_wrapped_route():
    user_id = session.get('user_id')
    saved_id = request.form.get('saved_id')

    # Call the function from utils.py to delete the collection and its associated data
    if delete_wrapped_data(saved_id, user_id):
        return redirect(url_for('main.profile'))
    else:
        return redirect(url_for('main.profile'))