from flask import render_template, request
from app import app
from app.utils.insights import total_hours, most_played_genre, missed_easy_achievement
from app.utils.fetch_player_data import FetchPlayerData

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

    #FetchPlayerData(steam_id)

    return render_template('main/wrapped.html', cards=[total_hours(steam_id), most_played_genre(steam_id), missed_easy_achievement(steam_id)])
    