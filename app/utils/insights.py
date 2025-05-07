from app.models import Game, User_Game, Developer, Developer_Game, Publisher, Publisher_Game, Genre, Game_Genre, Achievement, User_Achievement, Steam_User
from app import db
from flask import render_template
from sqlalchemy import func, cast, Integer
from datetime import datetime, timedelta

#################################################################################################################

''' The functions here make database queries to find interesting user data insights for a given steam user

    They all need to have a matching html/jinja template in templates/insights

    They should all return a tuple of the form (confidence, rendered_template) 
    
    Where: 
        Success is a reporting whether or not the insight could be found for an account
        
        Rendered_template is the result of render_template() for the matching template or None if insight 
        couldn't be found

    The original SQL queries behind each function are documented in notes/insights.txt'''

#################################################################################################################


''' Finds the users total account playtime'''
def total_hours(steam_id):
    result = (
        db.session.query(
            cast(func.round(func.sum(User_Game.playtime_total), 0), Integer).label("total_playtime")
        )
        .join(Game, User_Game.app_id == Game.app_id)  
        .filter(User_Game.steam_id == steam_id)
        .scalar()  
    )

    if result:
        print(str(result))
        return  (
            True,
            render_template(
                'insights/total_hours.html',
                total_hours=result
            )
        )
    else:
        return (False, None)


''' Finds the users most played genre'''
def most_played_genre(steam_id):
    result = (
        db.session.query(
            Genre.name,
            cast(func.round(func.sum(User_Game.playtime_total), 0), Integer).label("total_playtime"),
        )
        .join(Game_Genre, User_Game.app_id == Game_Genre.app_id)  
        .join(Genre, Game_Genre.genre_id == Genre.genre_id) 
        .filter(User_Game.steam_id == steam_id) 
        .group_by(Genre.name) 
        .order_by(func.sum(User_Game.playtime_total).desc())
        .limit(1)
        .first()
    )
    
    if result:
        return  (
            True,
            render_template(
                'insights/most_played_genre.html',
                genre=result.name,
                hours=result.total_playtime
            )
        )
    else:
        return (False, None)


''' Sees if the provided steam user has failed to acquire an achievement with a high global achievement rate
    in a game where they have atleast 10 hours of total playtime '''
def missed_easy_achievement(steam_id):
    MIN_PLAYTIME            =   10      #The minimum number of hours in the game 
    MIN_ACHIEVEMENT_RATE    =   85      #The minimum global achievement rate as a percentage

    result = (
        db.session.query(
            User_Achievement.app_id,
            Game.name.label("game_name"),
            Achievement.display_name.label("achievement_display_name"),
            Achievement.rate.label("achievement_rate"),
        )
        .join(
            User_Game,
            (User_Achievement.app_id == User_Game.app_id)
            & (User_Achievement.steam_id == User_Game.steam_id),
        ) 
        .join(
            Achievement,
            (User_Achievement.internal_name == Achievement.internal_name)
            & (User_Achievement.app_id == Achievement.app_id),
        ) 
        .join(Game, Game.app_id == User_Game.app_id)  
        .filter(
            User_Achievement.steam_id == steam_id,  
            User_Achievement.achieved == 0,             
            User_Game.playtime_total > MIN_PLAYTIME,                  
            Achievement.rate > MIN_ACHIEVEMENT_RATE, 
        )
        .order_by(Achievement.rate.desc())  
        .first()
    )

    if result:
        return  (
            True,
            render_template(
                "insights/missed_easy_achievement.html",
                achievement_display_name=result.achievement_display_name,
                achievement_rate=result.achievement_rate,
                game_name=result.game_name,
            )
        )
    else:
        return (False, None)


'''Finds the release year that the user has the most hours in i.e. sums playtime and groups by release year'''
def most_played_release_year(steam_id):
    result = (
        db.session.query(
            func.strftime('%Y', func.datetime(Game.release_date, 'unixepoch')).label("release_year"),
            cast(func.round(func.sum(User_Game.playtime_total), 0), Integer).label("total_playtime"),
        )
        .join(User_Game, Game.app_id == User_Game.app_id)  
        .filter(
            User_Game.steam_id == steam_id,  #
            Game.release_date != 0,  
        )
        .group_by(func.strftime('%Y', func.datetime(Game.release_date, 'unixepoch')))  
        .order_by(func.sum(User_Game.playtime_total).desc())  
        .limit(1)  
        .first()
    )

    if result:
        return (
            True,
            render_template(
                "insights/most_played_release_year.html",
                release_year=int(result.release_year),
                total_playtime=result.total_playtime,
            ),
        )
    else:
        return (False, None)

'''Finds the users most unloved game i.e. finds a game with atleast 10 hours of playtime with the oldest last played date'''
def most_unloved_game(steam_id):
    MIN_PLAYTIME = 10  # Minimum playtime in hours to consider a game

    result = (
        db.session.query(
            Game.name.label("game_name"),
            User_Game.last_played.label("last_played"),  
        )
        .join(Game, Game.app_id == User_Game.app_id)
        .filter(
            User_Game.steam_id == steam_id,
            User_Game.playtime_total >= MIN_PLAYTIME,
        )
        .order_by(User_Game.last_played.asc())  
        .first()
    )
 
    if result:
        days_since_last_played = (datetime.utcnow() - datetime.utcfromtimestamp(result.last_played)).days
        return (
            True,
            render_template(
                "insights/most_unloved_game.html",
                game_name=result.game_name,
                days_since_last_played=days_since_last_played,
            ),
        )
    else:
        return (False, None)