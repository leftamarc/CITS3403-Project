from app.models import Game, User_Game, Developer, Developer_Game, Publisher, Publisher_Game, Genre, Game_Genre, Achievement, User_Achievement, Steam_User
from app import db
from flask import render_template
from sqlalchemy import func, cast, Integer
from datetime import datetime, timedelta

#################################################################################################################

''' The functions here make database queries to find interesting user data insights for a given steam user

    They all need to have a matching html/jinja template in templates/insights

    They should all return a tuple of the form (success, rendered_template) 
    
    Where: 
        Success is boolean a reporting whether or not the insight could be found for an account
        
        Rendered_template is the result of render_template() for the matching template or None if insight 
        couldn't be found'''

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
    MIN_PLAYTIME         = 10   #The minimum number of hours in the game 
    MIN_ACHIEVEMENT_RATE = 85   #The minimum global achievement rate as a percentage

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
    MIN_PLAYTIME = 10   # Minimum playtime in hours to consider a game

    result = (
        db.session.query(
            Game.name.label("game_name"),
            User_Game.last_played.label("last_played"),  
        )
        .join(Game, Game.app_id == User_Game.app_id)
        .filter(
            User_Game.steam_id == steam_id,
            User_Game.playtime_total >= MIN_PLAYTIME,
            User_Game.last_played > 0
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


'''Finds the average metacritic score for the persons library'''
def avg_metacritic_score(steam_id):
    result = (
        db.session.query(
            cast(func.round(func.avg(Game.metacritic), 0), Integer).label("average_metacritic")
        )
        .join(User_Game, Game.app_id == User_Game.app_id)
        .filter(
            User_Game.steam_id == steam_id,  
            Game.metacritic.isnot(None),  
        )
        .scalar()  
    )

    if result:
        return (
            True,
            render_template(
                "insights/avg_metacritic_score.html",
                average_metacritic=result,
            ),
        )
    else:
        return (False, None)

'''Calculates the percentage of unplayed games in the user's library based on hours played'''
def backlog_size(steam_id):
    total_games = (
        db.session.query(func.count(User_Game.app_id).label("total_games"))
        .filter(User_Game.steam_id == steam_id)
        .scalar()  # Total number of games in the library
    )

    unplayed_games = (
        db.session.query(func.count(User_Game.app_id).label("unplayed_games"))
        .filter(
            User_Game.steam_id == steam_id,
            User_Game.playtime_total == 0,  # Only include games with 0 hours played
        )
        .scalar()  # Total number of unplayed games
    )

    if total_games > 0 and unplayed_games is not None:
        backlog_percentage = (unplayed_games / total_games) * 100
        return (
            True,
            render_template(
                "insights/backlog_size.html",
                backlog_percentage=int(round(backlog_percentage, 0)),
            ),
        )
    else:
        return (False, None)

'''Calculates the average achievement completion rate per game for the user'''
def achievement_completion_rate(steam_id):
    subquery = (
        db.session.query(
            (func.sum(User_Achievement.achieved) * 100.0 / func.count(User_Achievement.achieved)).label("completion_rate")
        )
        .filter(
            User_Achievement.steam_id == steam_id,  
        )
        .group_by(User_Achievement.app_id)  
        .subquery()  
    )

    result = (
        db.session.query(
            func.avg(subquery.c.completion_rate).label("average_completion_rate")  
        )
        .scalar()  
    )

    if result is not None:
        return (
            True,
            render_template(
                "insights/achievement_completion_rate.html",
                completion_rate=round(result, 2),  
            ),
        )
    else:
        return (False, None)

'''Finds the game with the highest ratio of achievements unlocked to hours played'''
def highest_achievements_to_hours(steam_id):
    MIN_PLAYTIME = 5  # Minimum playtime in hours
    MIN_ACHIEVEMENTS = 2  # Minimum number of achievements unlocked

    playtime_subquery = (
        db.session.query(
            User_Game.app_id.label("app_id"),
            func.sum(User_Game.playtime_total).label("total_hours"),
        )
        .filter(
            User_Game.steam_id == steam_id,  
        )
        .group_by(User_Game.app_id)  
        .subquery()
    )

    result = (
        db.session.query(
            Game.name.label("game_name"),
            func.count(User_Achievement.achieved).label("total_achievements"),
            playtime_subquery.c.total_hours.label("total_hours"),
            (func.count(User_Achievement.achieved) * 1.0 / playtime_subquery.c.total_hours).label("achievement_to_hours_ratio"),
        )
        .join(User_Game, User_Achievement.app_id == User_Game.app_id)
        .join(Game, User_Game.app_id == Game.app_id)
        .join(playtime_subquery, User_Game.app_id == playtime_subquery.c.app_id)  
        .filter(
            User_Achievement.steam_id == steam_id,  
            playtime_subquery.c.total_hours >= MIN_PLAYTIME,  
            User_Achievement.achieved == 1,  
        )
        .group_by(User_Achievement.app_id, Game.name, playtime_subquery.c.total_hours)  
        .having(
            func.count(User_Achievement.achieved) >= MIN_ACHIEVEMENTS 
        )
        .order_by((func.count(User_Achievement.achieved) * 1.0 / playtime_subquery.c.total_hours).desc())  
        .first()  
    )

    if result and result.total_hours > 0:
        return (
            True,
            render_template(
                "insights/highest_achievements_to_hours.html",
                game_name=result.game_name,
                total_achievements=int(result.total_achievements),
                total_hours=round(result.total_hours, 2),  
                achievement_to_hours_ratio=round(result.achievement_to_hours_ratio, 2),
            ),
        )
    else:
        return (False, None)

'''Finds the rarest achievement the user has unlocked (lowest global achievement rate)'''
def rarest_achievement(steam_id):
    # First query to find the rarest achievement
    achievement_result = (
        db.session.query(
            Achievement.app_id.label("app_id"),
            Achievement.display_name.label("achievement_name"),
            Achievement.rate.label("global_unlock_rate"),
        )
        .join(User_Achievement, (Achievement.app_id == User_Achievement.app_id) & (Achievement.internal_name == User_Achievement.internal_name))
        .filter(
            User_Achievement.steam_id == steam_id,  # Filter by the user's Steam ID
            User_Achievement.achieved == 1,  # Only include achievements the user has unlocked
            Achievement.rate.isnot(None),  # Ensure the achievement has a global unlock rate
        )
        .order_by(Achievement.rate.asc())  # Order by the lowest global unlock rate
        .first()  # Get the rarest achievement
    )

    if achievement_result:
        # Second query to get the game's name using the app_id
        game_result = (
            db.session.query(Game.name.label("game_name"))
            .filter(Game.app_id == achievement_result.app_id)
            .first()
        )

        if game_result:
            return (
                True,
                render_template(
                    "insights/rarest_achievement.html",
                    achievement_name=achievement_result.achievement_name,
                    global_unlock_rate=round(achievement_result.global_unlock_rate, 2),
                    game_name=game_result.game_name,
                ),
            )
    return (False, None)

def preference_for_game_age(steam_id):
    """
    Determines whether the user prefers older or more modern games based on playtime using regression with default Python libraries.
    """
    # Query to get release years and playtime for the user's games
    result = (
        db.session.query(
            func.strftime('%Y', func.datetime(Game.release_date, 'unixepoch')).label("release_year"),
            func.sum(User_Game.playtime_total).label("total_playtime"),
        )
        .join(User_Game, Game.app_id == User_Game.app_id)
        .filter(
            User_Game.steam_id == steam_id,  # Filter by the user's Steam ID
            Game.release_date != 0,  # Exclude games with no release date
            User_Game.playtime_total > 0,  # Exclude games with no playtime
        )
        .group_by(func.strftime('%Y', func.datetime(Game.release_date, 'unixepoch')))
        .all()
    )

    # Ensure we have enough data points for regression
    if len(result) < 2:
        return (False, None)

    # Prepare data for regression
    release_years = [int(row.release_year) for row in result]
    playtimes = [row.total_playtime for row in result]

    # Calculate means
    x_mean = sum(release_years) / len(release_years)
    y_mean = sum(playtimes) / len(playtimes)

    # Calculate the slope of the regression line
    numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(release_years, playtimes))
    denominator = sum((x - x_mean) ** 2 for x in release_years)

    if denominator == 0:
        return (False, None)  # Avoid division by zero

    slope = numerator / denominator

    # Interpret the slope
    if slope > 0:
        preference = "modern games"
    elif slope < 0:
        preference = "older games"
    else:
        preference = "no clear preference"

    # Render the result
    return (
        True,
        render_template(
            "insights/preference_for_game_age.html",
            slope=round(slope, 2),
            preference=preference,
        ),
    )

def taste_breaker(steam_id):
    """
    Finds a game where the user has an unusually high number of hours in a genre they typically don't play much.
    """
    from math import sqrt

    MIN_PLAYTIME = 10  # Minimum playtime in hours to consider a game

    # Query to get total playtime for each genre and each game in the user's library
    genre_playtime = (
        db.session.query(
            Genre.name.label("genre_name"),
            func.sum(User_Game.playtime_total).label("total_genre_playtime"),
            func.count(Game.app_id).label("total_games_in_genre"),
        )
        .join(Game_Genre, Game.app_id == Game_Genre.app_id)
        .join(Genre, Game_Genre.genre_id == Genre.genre_id)
        .join(User_Game, Game.app_id == User_Game.app_id)
        .filter(
            User_Game.steam_id == steam_id,  # Filter by the user's Steam ID
            User_Game.playtime_total >= MIN_PLAYTIME,  # Exclude games with less than 10 hours of playtime
        )
        .group_by(Genre.name)
        .all()
    )

    # Create a dictionary to store average playtime per genre
    genre_avg_playtime = {
        row.genre_name: row.total_genre_playtime / row.total_games_in_genre
        for row in genre_playtime
    }

    # Query to get playtime for each game and its genre
    game_playtime = (
        db.session.query(
            Game.name.label("game_name"),
            Genre.name.label("genre_name"),
            func.sum(User_Game.playtime_total).label("game_playtime"),
        )
        .join(Game_Genre, Game.app_id == Game_Genre.app_id)
        .join(Genre, Game_Genre.genre_id == Genre.genre_id)
        .join(User_Game, Game.app_id == User_Game.app_id)
        .filter(
            User_Game.steam_id == steam_id,  # Filter by the user's Steam ID
            User_Game.playtime_total >= MIN_PLAYTIME,  # Exclude games with less than 10 hours of playtime
        )
        .group_by(Game.name, Genre.name)
        .all()
    )

    # Detect the game with the highest deviation from the genre average
    outlier_game = None
    max_deviation = -float("inf")

    for row in game_playtime:
        genre_name = row.genre_name
        game_name = row.game_name
        game_playtime = row.game_playtime

        # Calculate deviation from the genre average
        if genre_name in genre_avg_playtime:
            avg_playtime = genre_avg_playtime[genre_name]
            deviation = game_playtime - avg_playtime

            # Check if this game has the highest deviation
            if deviation > max_deviation:
                max_deviation = deviation
                outlier_game = {
                    "game_name": game_name,
                    "genre_name": genre_name,
                    "game_playtime": game_playtime,
                    "avg_playtime": avg_playtime,
                    "deviation": deviation,
                }

    # If no outlier is found, return failure
    if not outlier_game:
        return (False, None)

    # Render the result
    return (
        True,
        render_template(
            "insights/taste_breaker.html",
            game_name=outlier_game["game_name"],
            genre_name=outlier_game["genre_name"],
            game_playtime=round(outlier_game["game_playtime"], 2),
            avg_playtime=round(outlier_game["avg_playtime"], 2),
            deviation=round(outlier_game["deviation"], 2),
        ),
    )

def favorite_publisher(steam_id):
    """
    Finds the user's favorite publisher by calculating the percentage increase in hours played
    for games published by that publisher compared to games published by other studios.
    Only considers publishers where the user has played at least 2 games with at least 10 hours of playtime each.
    """
    MIN_PLAYTIME = 10  # Minimum playtime in hours to consider a game
    MIN_GAMES = 2  # Minimum number of games played from a publisher

    # Query to get total playtime and game count for each publisher
    publisher_playtime = (
        db.session.query(
            Publisher.name.label("publisher_name"),
            func.sum(User_Game.playtime_total).label("total_publisher_playtime"),
            func.count(Game.app_id).label("total_publisher_games"),
        )
        .join(Publisher_Game, Game.app_id == Publisher_Game.app_id)
        .join(Publisher, Publisher_Game.publisher == Publisher.name)
        .join(User_Game, Game.app_id == User_Game.app_id)
        .filter(
            User_Game.steam_id == steam_id,  # Filter by the user's Steam ID
            User_Game.playtime_total >= MIN_PLAYTIME,  # Exclude games with less than 10 hours of playtime
        )
        .group_by(Publisher.name)
        .having(func.count(Game.app_id) >= MIN_GAMES)  # Only include publishers with at least 2 games
        .all()
    )

    # Calculate the user's total playtime and game count for all games
    total_playtime = (
        db.session.query(func.sum(User_Game.playtime_total))
        .filter(
            User_Game.steam_id == steam_id,
            User_Game.playtime_total >= MIN_PLAYTIME,
        )
        .scalar()
    )

    total_games = (
        db.session.query(func.count(User_Game.app_id))
        .filter(
            User_Game.steam_id == steam_id,
            User_Game.playtime_total >= MIN_PLAYTIME,
        )
        .scalar()
    )

    if not total_playtime or not total_games:
        return (False, None)

    # Find the publisher with the highest percentage increase in playtime
    favorite_publisher = None
    max_percentage_increase = -float("inf")

    for row in publisher_playtime:
        # Calculate average playtime for games published by the publisher
        publisher_avg_playtime = row.total_publisher_playtime / row.total_publisher_games

        # Calculate average playtime for games not published by the publisher
        non_publisher_avg_playtime = (
            (total_playtime - row.total_publisher_playtime)
            / (total_games - row.total_publisher_games)
            if total_games > row.total_publisher_games
            else 0
        )

        # Calculate percentage increase
        if non_publisher_avg_playtime > 0:
            percentage_increase = ((publisher_avg_playtime - non_publisher_avg_playtime) / non_publisher_avg_playtime) * 100
        else:
            percentage_increase = 0

        # Update favorite publisher if this one has the highest percentage increase
        if percentage_increase > max_percentage_increase:
            max_percentage_increase = percentage_increase
            favorite_publisher = {
                "publisher_name": row.publisher_name,
                "percentage_increase": percentage_increase,
            }

    # If no favorite publisher is found, return failure
    if not favorite_publisher:
        return (False, None)

    # Render the result
    return (
        True,
        render_template(
            "insights/favorite_publisher.html",
            publisher_name=favorite_publisher["publisher_name"],
            percentage_increase=round(favorite_publisher["percentage_increase"], 2),
        ),
    )



