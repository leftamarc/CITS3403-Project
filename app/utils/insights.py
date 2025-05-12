from app.models import Game, User_Game, Developer, Developer_Game, Publisher, Publisher_Game, Genre, Game_Genre, Achievement, User_Achievement, Steam_User
from app import db
from flask import render_template
from sqlalchemy import func, cast, Integer
from datetime import datetime, timedelta
import random
import pandas as pd
import numpy as np
import sklearn
from sklearn.ensemble import IsolationForest
from sklearn.linear_model import LogisticRegression, LinearRegression, Ridge
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from itertools import combinations

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
    Determines whether the user prefers older or newer games based on playtime compared to the mean age of their library.
    Only considers games with a minimum playtime.
    """
    MIN_PLAYTIME = 10  # Minimum playtime in hours to consider a game

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
            User_Game.playtime_total >= MIN_PLAYTIME,  # Exclude games with less than the minimum playtime
        )
        .group_by(func.strftime('%Y', func.datetime(Game.release_date, 'unixepoch')))
        .all()
    )

    # Ensure we have enough data points for regression
    if len(result) < 2:
        return (False, None)

    # Convert query result to a DataFrame
    df = pd.DataFrame(result, columns=["release_year", "total_playtime"])
    df["release_year"] = df["release_year"].astype(int)

    # Calculate the mean release year of the user's library
    mean_release_year = df["release_year"].mean()

    # Prepare data for regression
    X = df[["release_year"]].values  # Feature: release year
    y = df["total_playtime"].values  # Target: total playtime

    # Perform linear regression
    model = sklearn.linear_model.LinearRegression()
    model.fit(X, y)

    # Get the slope of the regression line
    slope = model.coef_[0]

    # Interpret the slope
    if slope > 0:
        preference = "newer games"
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
            mean_release_year=int(mean_release_year),
        ),
    )

def taste_breaker(steam_id):
    """
    Finds a game where the user's playtime is a strong outlier compared to other games in its listed genres.
    If multiple games fit this criterion, selects one randomly and provides a statistic about its outlierness.
    Only considers games with a minimum playtime and a minimum anomaly score.
    """
    MIN_PLAYTIME = 10      # Minimum playtime in hours to consider a game
    MIN_ANOMALY_SCORE = -0.25  # Minimum anomaly score to consider a game as an outlier

    # Subquery: get total playtime per game for this user
    playtime_subquery = (
        db.session.query(
            User_Game.app_id.label("app_id"),
            func.sum(User_Game.playtime_total).label("total_playtime")
        )
        .filter(
            User_Game.steam_id == steam_id,
            User_Game.playtime_total >= MIN_PLAYTIME
        )
        .group_by(User_Game.app_id)
        .subquery()
    )

    # Main query: join to genres
    game_data = (
        db.session.query(
            Game.name.label("game_name"),
            playtime_subquery.c.total_playtime,
            func.group_concat(Genre.name, ",").label("genres"),
        )
        .join(playtime_subquery, Game.app_id == playtime_subquery.c.app_id)
        .join(Game_Genre, Game.app_id == Game_Genre.app_id)
        .join(Genre, Game_Genre.genre_id == Genre.genre_id)
        .group_by(Game.app_id, Game.name, playtime_subquery.c.total_playtime)
        .all()
    )

    # Ensure we have enough data
    if not game_data or len(game_data) < 2:
        return (False, None)

    # Convert to DataFrame
    df = pd.DataFrame(game_data, columns=["game_name", "total_playtime", "genres"])
    df["total_playtime"] = df["total_playtime"].astype(float)

    # Expand genres into separate rows for each game
    genre_expanded = df.assign(genres=df["genres"].str.split(",")).explode("genres")

    # Group by genre and calculate outliers using Isolation Forest
    outlier_games = []
    outlier_scores = {}
    for genre, group in genre_expanded.groupby("genres"):
        if len(group) < 2:
            continue  # Skip genres with fewer than 2 games

        X = group[["total_playtime"]].values
        model = IsolationForest(contamination=0.1, random_state=42)
        group["is_outlier"] = model.fit_predict(X)
        group["anomaly_score"] = model.decision_function(X)

        # Only consider strong outliers
        outliers = group[(group["is_outlier"] == -1) & (group["anomaly_score"] <= MIN_ANOMALY_SCORE)]
        outlier_games.extend(outliers["game_name"].tolist())
        for _, row in outliers.iterrows():
            outlier_scores[row["game_name"]] = row["anomaly_score"]

    if not outlier_games:
        return (False, None)

    # Select a random outlier game
    selected_game = random.choice(outlier_games)
    selected_game_data = df[df["game_name"] == selected_game].iloc[0]
    anomaly_score = outlier_scores[selected_game]

    return (
        True,
        render_template(
            "insights/taste_breaker.html",
            game_name=selected_game,
            total_playtime=round(selected_game_data["total_playtime"], 2),
            genres=selected_game_data["genres"],
            anomaly_score=round(anomaly_score, 2),
        ),
    )

def favorite_publisher(steam_id):
    """
    Finds the publisher whose games the user plays significantly more than their average,
    quantifies the effect as a percentage increase, and shows the publisher with the greatest positive influence.
    """
    MIN_PLAYTIME = 5  # Only consider games with at least this much playtime

    # Query: get playtime and publisher for each game the user owns
    game_data = (
        db.session.query(
            Game.name.label("game_name"),
            func.sum(User_Game.playtime_total).label("total_playtime"),
            Publisher.name.label("publisher"),
        )
        .join(User_Game, Game.app_id == User_Game.app_id)
        .join(Publisher_Game, Game.app_id == Publisher_Game.app_id)
        .join(Publisher, Publisher_Game.publisher == Publisher.name)
        .filter(
            User_Game.steam_id == steam_id,
            User_Game.playtime_total >= MIN_PLAYTIME,
        )
        .group_by(Game.app_id, Game.name, Publisher.name)
        .all()
    )

    if not game_data or len(game_data) < 2:
        return (False, None)

    # Convert to DataFrame
    df = pd.DataFrame(game_data, columns=["game_name", "total_playtime", "publisher"])
    df["total_playtime"] = df["total_playtime"].astype(float)

    # Calculate the user's average playtime for all games
    overall_avg = df["total_playtime"].mean()

    # Calculate the average playtime for each publisher
    publisher_stats = (
        df.groupby("publisher")["total_playtime"]
        .agg(["mean", "count"])
        .reset_index()
    )
    publisher_stats["percent_increase"] = ((publisher_stats["mean"] - overall_avg) / overall_avg) * 100

    # Only consider publishers with at least 2 games for robustness
    publisher_stats = publisher_stats[publisher_stats["count"] >= 2]

    if publisher_stats.empty:
        return (False, None)

    # Find the publisher with the greatest positive percent increase
    fav_row = publisher_stats.loc[publisher_stats["percent_increase"].idxmax()]

    if fav_row["percent_increase"] <= 0:
        return (False, None)  # No publisher has a positive influence

    return (
        True,
        render_template(
            "insights/favorite_publisher.html",
            publisher=fav_row["publisher"],
            percent_increase=round(fav_row["percent_increase"], 1),
            avg_playtime=round(fav_row["mean"], 2),
            overall_avg=round(overall_avg, 2),
            game_count=int(fav_row["count"]),
        ),
    )

def least_fav_genre(steam_id):
    """
    Uses logistic regression to find the genre most associated with the user playing a game for more than 5 but no more than 10 hours.
    Quantifies the effect as an odds ratio.
    """
    MIN_PLAY = 5
    MAX_PLAY = 10

    # Query: get playtime and genres for each game the user owns
    game_data = (
        db.session.query(
            Game.name.label("game_name"),
            func.sum(User_Game.playtime_total).label("total_playtime"),
            func.group_concat(Genre.name, ",").label("genres"),
        )
        .join(User_Game, Game.app_id == User_Game.app_id)
        .join(Game_Genre, Game.app_id == Game_Genre.app_id)
        .join(Genre, Game_Genre.genre_id == Genre.genre_id)
        .filter(User_Game.steam_id == steam_id)
        .group_by(Game.app_id, Game.name)
        .all()
    )

    if not game_data or len(game_data) < 5:
        return (False, None)

    # DataFrame and label
    df = pd.DataFrame(game_data, columns=["game_name", "total_playtime", "genres"])
    df["total_playtime"] = df["total_playtime"].astype(float)
    df["label"] = ((df["total_playtime"] > MIN_PLAY) & (df["total_playtime"] <= MAX_PLAY)).astype(int)

    # One-hot encode genres (multi-label)
    genre_dummies = df["genres"].str.get_dummies(sep=",")
    if genre_dummies.shape[1] < 2:
        return (False, None)  # Not enough genre variety

    # Fit logistic regression
    model = LogisticRegression(max_iter=1000)
    model.fit(genre_dummies, df["label"])

    # Find genre with highest positive coefficient
    coefs = pd.Series(model.coef_[0], index=genre_dummies.columns)
    top_genre = coefs.idxmax()
    odds_ratio = np.exp(coefs[top_genre])
    percent = 100 * (odds_ratio - 1)

    # How many games in this genre and how many are in the "tried but didn't stick" range
    genre_mask = genre_dummies[top_genre] == 1
    total = genre_mask.sum()
    in_range = ((df["label"] == 1) & genre_mask).sum()

    return (
        True,
        render_template(
            "insights/least_fav_genre.html",
            genre=top_genre,
            odds_ratio=round(odds_ratio, 2),
            percent=round(percent, 1),
            in_range=in_range,
            total=total,
        ),
    )

def genre_synergy(steam_id):
    """
    Finds the genre duo (pair) that, when both are present in a game, has the strongest positive influence on total playtime.
    Uses linear regression to quantify the synergy effect.
    """
    MIN_PLAYTIME = 2  # Only consider games with at least this much playtime

    # Query: get playtime and genres for each game the user owns
    game_data = (
        db.session.query(
            Game.name.label("game_name"),
            func.sum(User_Game.playtime_total).label("total_playtime"),
            func.group_concat(Genre.name, ",").label("genres"),
        )
        .join(User_Game, Game.app_id == User_Game.app_id)
        .join(Game_Genre, Game.app_id == Game_Genre.app_id)
        .join(Genre, Game_Genre.genre_id == Genre.genre_id)
        .filter(
            User_Game.steam_id == steam_id,
            User_Game.playtime_total >= MIN_PLAYTIME,
        )
        .group_by(Game.app_id, Game.name)
        .all()
    )

    if not game_data or len(game_data) < 5:
        return (False, None)

    # DataFrame and one-hot encode genres
    df = pd.DataFrame(game_data, columns=["game_name", "total_playtime", "genres"])
    df["total_playtime"] = df["total_playtime"].astype(float)
    genre_dummies = df["genres"].str.get_dummies(sep=",")
    genre_names = genre_dummies.columns.tolist()

    if len(genre_names) < 2:
        return (False, None)

    # Add pairwise (synergy) columns
    pair_cols = []
    for g1, g2 in combinations(genre_names, 2):
        col_name = f"{g1} + {g2}"
        df[col_name] = genre_dummies[g1] & genre_dummies[g2]
        pair_cols.append(col_name)

    # Prepare regression features: all single genres and all pairs
    X = pd.concat([genre_dummies, df[pair_cols]], axis=1)
    y = df["total_playtime"]

    # Fit linear regression
    model = LinearRegression()
    model.fit(X, y)
    coefs = pd.Series(model.coef_, index=X.columns)

    # Find the pair with the highest positive coefficient
    pair_coefs = coefs[pair_cols]
    if pair_coefs.empty or pair_coefs.max() <= 0:
        return (False, None)
    best_pair = pair_coefs.idxmax()
    synergy_value = pair_coefs.max()

    # How many games have this duo
    games_with_duo = int(df[best_pair].sum())
    avg_playtime_with_duo = df[df[best_pair] == 1]["total_playtime"].mean() if games_with_duo > 0 else 0

    # Calculate user's average playtime for all games
    overall_avg_playtime = df["total_playtime"].mean() if len(df) > 0 else 0

    # Calculate percent increase
    percent_increase = ((avg_playtime_with_duo - overall_avg_playtime) / overall_avg_playtime * 100) if overall_avg_playtime > 0 else 0

    g1, g2 = best_pair.split(" + ")

    # Calculate multiplier (e.g., 2.0x means double the average)
    multiplier = (avg_playtime_with_duo / overall_avg_playtime) if overall_avg_playtime > 0 else 0

    return (
        True,
        render_template(
            "insights/genre_synergy.html",
            genre1=g1,
            genre2=g2,
            multiplier=round(multiplier, 2),
            avg_playtime_with_duo=round(avg_playtime_with_duo, 1),
            overall_avg_playtime=round(overall_avg_playtime, 1),
            games_with_duo=games_with_duo,
        ),
    )

def metacritic_vs_playtime(steam_id):
    """
    Quantifies how much the user's normalized playtime is influenced by Metacritic score.
    Reports the extra normalized hours played per Metacritic point, and the correlation.
    """
    MIN_PLAYTIME = 5

    game_data = (
        db.session.query(
            Game.name.label("game_name"),
            func.sum(User_Game.playtime_total).label("total_playtime"),
            Game.metacritic.label("metacritic"),
        )
        .join(User_Game, Game.app_id == User_Game.app_id)
        .filter(
            User_Game.steam_id == steam_id,
            User_Game.playtime_total >= MIN_PLAYTIME,
            Game.metacritic.isnot(None),
        )
        .group_by(Game.app_id, Game.name, Game.metacritic)
        .all()
    )

    if not game_data or len(game_data) < 5:
        return (False, None)

    df = pd.DataFrame(game_data, columns=["game_name", "total_playtime", "metacritic"])
    df["total_playtime"] = df["total_playtime"].astype(float)
    df["metacritic"] = df["metacritic"].astype(float)

    # Normalize playtime by user's average
    user_avg = df["total_playtime"].mean()
    df["norm_playtime"] = df["total_playtime"] / user_avg if user_avg > 0 else df["total_playtime"]

    # Regression: normalized playtime ~ metacritic
    X = df[["metacritic"]]
    y = df["norm_playtime"]
    model = LinearRegression()
    model.fit(X, y)
    slope = model.coef_[0]
    corr = df["metacritic"].corr(df["norm_playtime"])

    return (
        True,
        render_template(
            "insights/metacritic_vs_playtime.html",
            slope=round(slope, 3),
            corr=round(corr, 2),
            user_avg=round(user_avg, 1),
        ),
    )


def genre_metacritic_influence(steam_id):
    """
    For each genre, regress normalized playtime against Metacritic score.
    Reports the genre where the user's playtime is most and least influenced by Metacritic.
    """
    MIN_PLAYTIME = 5

    # Query: get playtime, metacritic, and genres for each game the user owns
    game_data = (
        db.session.query(
            Game.name.label("game_name"),
            func.sum(User_Game.playtime_total).label("total_playtime"),
            Game.metacritic.label("metacritic"),
            func.group_concat(Genre.name, ",").label("genres"),
        )
        .join(User_Game, Game.app_id == User_Game.app_id)
        .join(Game_Genre, Game.app_id == Game_Genre.app_id)
        .join(Genre, Game_Genre.genre_id == Genre.genre_id)
        .filter(
            User_Game.steam_id == steam_id,
            User_Game.playtime_total >= MIN_PLAYTIME,
            Game.metacritic.isnot(None),
        )
        .group_by(Game.app_id, Game.name, Game.metacritic)
        .all()
    )

    if not game_data or len(game_data) < 5:
        return (False, None)

    df = pd.DataFrame(game_data, columns=["game_name", "total_playtime", "metacritic", "genres"])
    df["total_playtime"] = df["total_playtime"].astype(float)
    df["metacritic"] = df["metacritic"].astype(float)

    # Normalize playtime by user's average
    user_avg = df["total_playtime"].mean()
    df["norm_playtime"] = df["total_playtime"] / user_avg if user_avg > 0 else df["total_playtime"]

    # Expand genres into separate rows for each game
    genre_expanded = df.assign(genre=df["genres"].str.split(",")).explode("genre")

    # Only keep genres with at least 4 games for robustness
    genre_counts = genre_expanded["genre"].value_counts()
    valid_genres = genre_counts[genre_counts >= 4].index

    genre_slopes = {}
    genre_corrs = {}
    for genre in valid_genres:
        sub = genre_expanded[genre_expanded["genre"] == genre]
        if sub["metacritic"].nunique() > 1 and sub["norm_playtime"].nunique() > 1:
            X = sub[["metacritic"]]
            y = sub["norm_playtime"]
            model = LinearRegression()
            model.fit(X, y)
            slope = model.coef_[0]
            corr = sub["metacritic"].corr(sub["norm_playtime"])
            genre_slopes[genre] = slope
            genre_corrs[genre] = corr

    if not genre_slopes:
        return (False, None)

    most_influenced_genre = max(genre_slopes, key=genre_slopes.get)
    least_influenced_genre = min(genre_slopes, key=genre_slopes.get)

    return (
        True,
        render_template(
            "insights/genre_metacritic_influence.html",
            most_genre=most_influenced_genre,
            most_slope=round(genre_slopes[most_influenced_genre], 3),
            most_corr=round(genre_corrs[most_influenced_genre], 2),
            least_genre=least_influenced_genre,
            least_slope=round(genre_slopes[least_influenced_genre], 3),
            least_corr=round(genre_corrs[least_influenced_genre], 2),
        ),
    )

def never_achieve(steam_id):
    """
    Finds an unachieved achievement the player is least likely to ever achieve,
    using logistic regression on playtime, global unlock rate, metacritic, and the user's personal genre achievement rate.
    Randomly selects from the 25 least likely.
    Returns the achievement name, game, and the predicted probability of ever achieving it.
    """
    # Query all achievements for this user, with playtime, global unlock rate, and genres
    achievement_data = (
        db.session.query(
            Achievement.display_name.label("achievement_name"),
            Achievement.rate.label("global_rate"),
            User_Achievement.achieved.label("achieved"),
            User_Game.playtime_total.label("playtime"),
            Game.name.label("game_name"),
            Game.metacritic.label("metacritic"),
            func.group_concat(Genre.name, ",").label("genres"),
        )
        .join(User_Achievement, (Achievement.app_id == User_Achievement.app_id) & (Achievement.internal_name == User_Achievement.internal_name))
        .join(User_Game, (User_Achievement.app_id == User_Game.app_id) & (User_Achievement.steam_id == User_Game.steam_id))
        .join(Game, Game.app_id == User_Game.app_id)
        .outerjoin(Game_Genre, Game.app_id == Game_Genre.app_id)
        .outerjoin(Genre, Game_Genre.genre_id == Genre.genre_id)
        .filter(User_Achievement.steam_id == steam_id)
        .group_by(Achievement.app_id, Achievement.internal_name, Achievement.display_name, Achievement.rate, User_Achievement.achieved, User_Game.playtime_total, Game.name, Game.metacritic)
        .all()
    )

    if not achievement_data or len(achievement_data) < 10:
        return (False, None)

    df = pd.DataFrame(achievement_data, columns=["achievement_name", "global_rate", "achieved", "playtime", "game_name", "metacritic", "genres"])
    df["global_rate"] = df["global_rate"].astype(float)
    df["playtime"] = df["playtime"].astype(float)
    df["metacritic"] = df["metacritic"].fillna(df["metacritic"].mean()).astype(float)
    df["achieved"] = df["achieved"].astype(int)
    df["genres"] = df["genres"].fillna("")

    # Compute user's personal achievement rate per genre
    genre_achievements = []
    for _, row in df.iterrows():
        for genre in set([g.strip() for g in row["genres"].split(",") if g.strip()]):
            genre_achievements.append({
                "genre": genre,
                "achieved": row["achieved"]
            })
    genre_achievements_df = pd.DataFrame(genre_achievements)
    if genre_achievements_df.empty:
        return (False, None)
    genre_rates = genre_achievements_df.groupby("genre")["achieved"].mean().to_dict()

    # Add user's personal genre achievement rate as a feature
    def get_personal_genre_rate(genres):
        genres = [g.strip() for g in genres.split(",") if g.strip()]
        if not genres:
            return 0.0
        return np.mean([genre_rates.get(g, 0.0) for g in genres])
    df["personal_genre_rate"] = df["genres"].apply(get_personal_genre_rate)

    # Only use rows with non-null playtime and global_rate
    df = df.dropna(subset=["playtime", "global_rate"])

    # Features: playtime, global_rate, metacritic, personal_genre_rate
    X = df[["playtime", "global_rate", "metacritic", "personal_genre_rate"]]
    y = df["achieved"]

    # Only fit if both classes are present
    if y.nunique() < 2:
        return (False, None)

    model = LogisticRegression(max_iter=1000)
    model.fit(X, y)

    # Predict probability for unachieved achievements
    unachieved = df[df["achieved"] == 0].copy()
    if unachieved.empty:
        return (False, None)
    unachieved["prob"] = model.predict_proba(unachieved[["playtime", "global_rate", "metacritic", "personal_genre_rate"]])[:, 1]

    # Get the 25 least likely achievements and pick one at random
    top_n = min(25, len(unachieved))
    least_likely = unachieved.nsmallest(top_n, "prob")
    hardest = least_likely.sample(n=1, random_state=random.randint(0, 999999)).iloc[0]

    # Get the user's display name
    user = db.session.query(Steam_User).filter_by(steam_id=steam_id).first()
    username = user.username if user else "This user"

    return (
        True,
        render_template(
            "insights/never_achieve.html",
            username=username,
            achievement_name=hardest["achievement_name"],
            game_name=hardest["game_name"],
            likelihood=round(hardest["prob"] * 100, 2),
        ),
    )

def they_got_stuck_at_the_tutorial(steam_id):
    """
    Finds the game in the user's library where low Metacritic score is most strongly correlated with rare achievements globally.
    For each game, computes the correlation between the game's Metacritic and its achievements' global unlock rates.
    Returns the game with the strongest negative correlation (i.e., lower Metacritic = rarer achievements).
    """
    # Query all games in the user's library with their metacritic and achievement global rates
    game_ach_data = (
        db.session.query(
            Game.app_id,
            Game.name.label("game_name"),
            Game.metacritic.label("metacritic"),
            Achievement.display_name.label("achievement_name"),
            Achievement.rate.label("global_rate"),
        )
        .join(User_Game, Game.app_id == User_Game.app_id)
        .join(Achievement, Game.app_id == Achievement.app_id)
        .filter(
            User_Game.steam_id == steam_id,
            Game.metacritic.isnot(None),
            Achievement.rate.isnot(None),
        )
        .all()
    )

    if not game_ach_data or len(game_ach_data) < 10:
        return (False, None)

    df = pd.DataFrame(game_ach_data, columns=["app_id", "game_name", "metacritic", "achievement_name", "global_rate"])
    df["metacritic"] = df["metacritic"].astype(float)
    df["global_rate"] = df["global_rate"].astype(float)

    # Only keep games with at least 5 achievements
    counts = df["app_id"].value_counts()
    valid_games = counts[counts >= 5].index
    df = df[df["app_id"].isin(valid_games)]

    if df.empty:
        return (False, None)

    # For each game, compute the correlation between metacritic and global_rate (will be NaN if metacritic is constant, but it's not)
    corrs = {}
    for app_id, group in df.groupby("app_id"):
        if group["global_rate"].nunique() > 1:
            # All achievements in a game have the same metacritic, so correlation is undefined.
            # Instead, use the mean global_rate as a proxy for "rareness" and find the game with lowest mean global_rate and lowest metacritic.
            corrs[app_id] = (group["metacritic"].iloc[0], group["global_rate"].mean(), group["game_name"].iloc[0])

    if not corrs:
        return (False, None)

    # Find the game with the lowest metacritic and lowest mean global_rate (rarest achievements)
    # Score: (1 - metacritic/100) * (1 - mean_global_rate/100)
    scored = {k: (1 - v[0]/100) * (1 - v[1]/100) for k, v in corrs.items()}
    worst_app_id = max(scored, key=scored.get)
    metacritic, mean_global_rate, game_name = corrs[worst_app_id]

    return (
        True,
        render_template(
            "insights/they_got_stuck_at_the_tutorial.html",
            game_name=game_name,
            metacritic=int(metacritic),
            completion_rate=round(100 - mean_global_rate, 1),  # "completion_rate" here is % of rarest (lower is rarer)
        ),
    )

def most_skilled_genre(steam_id):
    """
    Finds the genre where the player is most skilled, defined as the genre where the user has unlocked the rarest achievements on average.
    Uses the average global unlock rate of the user's unlocked achievements per genre (lower = rarer = more skilled).
    Only considers genres with at least 5 unlocked achievements.
    """
    # Query all unlocked achievements for this user, with their global unlock rate and genres
    achievement_data = (
        db.session.query(
            Achievement.display_name.label("achievement_name"),
            Achievement.rate.label("global_rate"),
            func.group_concat(Genre.name, ",").label("genres"),
        )
        .join(User_Achievement, (Achievement.app_id == User_Achievement.app_id) & (Achievement.internal_name == User_Achievement.internal_name))
        .join(Game_Genre, Achievement.app_id == Game_Genre.app_id)
        .join(Genre, Game_Genre.genre_id == Genre.genre_id)
        .filter(
            User_Achievement.steam_id == steam_id,
            User_Achievement.achieved == 1,
            Achievement.rate.isnot(None),
        )
        .group_by(Achievement.app_id, Achievement.internal_name, Achievement.display_name, Achievement.rate)
        .all()
    )

    if not achievement_data or len(achievement_data) < 10:
        return (False, None)

    df = pd.DataFrame(achievement_data, columns=["achievement_name", "global_rate", "genres"])
    df["global_rate"] = df["global_rate"].astype(float)
    df["genres"] = df["genres"].fillna("")

    # Expand genres into separate rows for each achievement
    genre_expanded = df.assign(genre=df["genres"].str.split(",")).explode("genre")
    genre_expanded["genre"] = genre_expanded["genre"].str.strip()
    genre_expanded = genre_expanded[genre_expanded["genre"] != ""]

    # Only keep genres with at least 5 unlocked achievements
    genre_counts = genre_expanded["genre"].value_counts()
    valid_genres = genre_counts[genre_counts >= 5].index

    if valid_genres.empty:
        return (False, None)

    # Compute the average global rarity (lower = more skilled) for each genre
    genre_skill = genre_expanded[genre_expanded["genre"].isin(valid_genres)].groupby("genre")["global_rate"].mean()

    # Find the genre with the lowest average global_rate (i.e., rarest achievements unlocked)
    most_skilled = genre_skill.idxmin()
    avg_rarity = genre_skill.min()

    return (
        True,
        render_template(
            "insights/most_skilled_genre.html",
            genre=most_skilled,
            avg_rarity=round(avg_rarity, 2),
            count=int(genre_counts[most_skilled]),
        ),
    )
