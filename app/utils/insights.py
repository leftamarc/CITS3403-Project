from app.models import Game, User_Game, Developer, Developer_Game, Publisher, Publisher_Game, Genre, Game_Genre, Achievement, User_Achievement, Steam_User
from app import db
from flask import render_template

# Given a steam_id, uses the database to find the user's total account playtime
def total_hours(steam_id):
    # Query the database to sum up the total playtime for the user
    total_playtime_hours = (
        User_Game.query.with_entities(db.func.sum(User_Game.playtime_total))
        .filter_by(steam_id=steam_id)
        .scalar()
    )

    # Use the total playtime in hours directly
    total_hours = round(total_playtime_hours or 0)

    return render_template(
        'insights/total_hours.html',
        total_hours=total_hours
    )

def most_played_genre(steam_id):
    # Query to find the most played genre by joining User_Game, Game_Genre, and Genre tables
    most_played_genre = (
        db.session.query(
            Genre.name, db.func.sum(User_Game.playtime_total).label('total_playtime')
        )
        .join(Game_Genre, Game_Genre.genre_id == Genre.genre_id)
        .join(User_Game, User_Game.app_id == Game_Genre.app_id)
        .filter(User_Game.steam_id == steam_id)
        .group_by(Genre.name)
        .order_by(db.desc('total_playtime'))
        .first()
    )

    # Extract the genre and total playtime
    genre = most_played_genre.name if most_played_genre else "Unknown"
    total_playtime = round(most_played_genre.total_playtime) if most_played_genre else 0

    return render_template(
        'insights/most_played_genre.html',
        genre=genre,
        hours=total_playtime
    )

def missed_easy_achievement(steam_id):
    # Query to find an easy achievement the user doesn't have
    missed_achievement = (
        db.session.query(
            Achievement.display_name,
            Achievement.description,
            Achievement.rate,
            Game.name.label("game_name"),
        )
        .join(User_Game, User_Game.app_id == Achievement.app_id)
        .join(Game, Game.app_id == Achievement.app_id)
        .outerjoin(
            User_Achievement,
            (User_Achievement.internal_name == Achievement.internal_name)
            & (User_Achievement.steam_id == steam_id),
        )
        .filter(
            User_Game.steam_id == steam_id,
            User_Game.playtime_total >= 5 * 60,  # At least 5 hours of playtime (in minutes)
            Achievement.rate >= 90,  # Global achievement rate of 90% or higher
            User_Achievement.achieved == 0,  # User hasn't achieved it
        )
        .order_by(Achievement.rate.desc())  # Order by highest achievement rate
        .first()
    )

    # Check if an achievement was found
    if missed_achievement:
        message = f"Wow you sure suck, **{missed_achievement.display_name}** in **{missed_achievement.game_name}** ({missed_achievement.description}) with a global rate of {missed_achievement.rate}%."
    else:
        message = "Guess you're not too bad, you haven't missed out on any easy achievements."

    return render_template(
        "insights/missed_easy_achievement.html",
        message=message,
    )