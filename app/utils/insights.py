from app.models import Game, User_Game, Developer, Developer_Game, Publisher, Publisher_Game, Genre, Game_Genre, Achievement, User_Achievement, Steam_User
from app import db
from flask import render_template
from sqlalchemy import func, cast, Integer

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
        .join(Game, User_Game.app_id == Game.app_id)  # Join User_Game with Game
        .filter(User_Game.steam_id == steam_id)  # Filter by the user's Steam ID
        .scalar()  # Get the scalar value (total playtime)
    )

    if result:
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