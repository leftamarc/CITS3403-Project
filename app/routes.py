from flask import render_template, request
from app import app
from app.utils.insights import *
from app.utils.fetch_player_data import FetchPlayerData
import random


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

@app.route('/generate', methods=['POST'])
def generate():
    
    # Get the Steam ID from the form
    steam_id = request.form.get('steamid')

    #Update the database with all player info
    #FetchPlayerData(steam_id) #commented out while I test since it takes ages

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