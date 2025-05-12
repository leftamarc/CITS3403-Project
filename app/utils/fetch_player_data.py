import time as tm
from app import db
from datetime import datetime
from app.models import Game, User_Game, Developer, Developer_Game, Publisher, Publisher_Game, Genre, Game_Genre, Achievement, User_Achievement, Steam_User
from app.utils.api import GetPlayerSummaries, GetOwnedGames, GetAppMetadata, GetPlayerAchievements, GetGlobalAchievementPercentagesForApp


def FetchPlayerData(steam_id):
    try:
        # Fetch and update player data
        steam_user, library = fetch_player_data(steam_id)

        # Process each game in the player's library
        for game in library:
            app_id = game[0]
            print(f'\nFetching data for app_id {app_id}')
            process_game_data(steam_id, app_id, game)

        db.session.commit()

    except Exception as e:
        raise


def fetch_player_data(steam_id):
    '''Fetch and update player data'''
    steamid, username, avatar_url = GetPlayerSummaries(steam_id)
    n_game_owned, library = GetOwnedGames(steam_id)
    Steam_User.upsert(steam_id, username, avatar_url, n_game_owned)
    return (steamid, library)


def process_game_data(steam_id, app_id, game):
    '''Fetch and update game data'''
    game_name = game[1]
    playtime = game[2] / 60  # Convert minutes to hours
    image = game[3]
    last_played = game[4]

    try:
        game_name, developers, publishers, genres, release_date, metacritic = GetAppMetadata(app_id)
    except Exception as e:
        print(f"Error fetching metadata for app_id {app_id}: {e}")
        return
        #Just skipping this game if error happens

    # Convert release_date to Unix timestamp
    release_date_timestamp = convert_to_unix_timestamp(release_date)

    # Upsert game and user-game data
    Game.upsert(app_id, game_name, image, release_date_timestamp, metacritic)
    User_Game.upsert(steam_id, app_id, playtime, last_played)

    # Process related data
    process_developer_data(app_id, developers)
    process_publisher_data(app_id, publishers)
    process_genre_data(app_id, genres)
    process_achievement_data(steam_id, app_id)


def process_developer_data(app_id, developers):
    '''Fetch and update developer data'''
    for developer in developers:
        Developer.upsert(developer)
        Developer_Game.upsert(app_id, developer)


def process_publisher_data(app_id, publishers):
    '''Fetch and update publisher data'''
    for publisher in publishers:
        Publisher.upsert(publisher)
        Publisher_Game.upsert(app_id, publisher)


def process_genre_data(app_id, genres):
    '''Fetch and update genre data'''
    for genre in genres:
        Genre.upsert(genre[0], genre[1])
        Game_Genre.upsert(app_id, genre[0])

    


def process_achievement_data(steam_id, app_id):
    '''Fetch and update achievement data for a specific game'''
    try:
        game_name, player_achievements = GetPlayerAchievements(steam_id, app_id)
        global_achievements = GetGlobalAchievementPercentagesForApp(app_id)

        # Create dictionaries for achievements
        achievement_dicts = []

        # Process player achievements
        for achievement in player_achievements:
            achievement_dicts.append({
                "internal_name": achievement[0],
                "rate": None,  # Placeholder for global rate
                "app_id": app_id,
                "display_name": achievement[3],
                "description": achievement[4],
                "achieved": achievement[1],
                "unlock_time": achievement[2],
            })

        # Update the rate field from global achievements
        for global_achievement in global_achievements:
            for achievement in achievement_dicts:
                if achievement["internal_name"] == global_achievement[0]:
                    achievement["rate"] = global_achievement[1]

        # Upsert achievements into the database
        for achievement in achievement_dicts:
            if not achievement["rate"]:
                #For some reason sometimes steam will have no global achievement data but have user achievement data
                #for the same achievement, in this case we just skip the achievement entirely
                continue

            Achievement.upsert(
                achievement["internal_name"],
                achievement["rate"],
                achievement["app_id"],
                achievement["display_name"],
                achievement["description"],
            )
            User_Achievement.upsert(
                achievement["internal_name"],
                achievement["app_id"],
                steam_id,
                achievement["achieved"],
                achievement["unlock_time"],
            )
    except Exception as e:
        return
        #Most commonly just catches the NoAchievement's exception raised by the api call



def convert_to_unix_timestamp(release_date):
    '''Convert a release date string to a Unix timestamp'''
    if not release_date:
        return 0
    try:
        # Try parsing "Day Month, Year" (e.g., "28 Mar, 2017")
        return int(tm.mktime(datetime.strptime(release_date, "%d %b, %Y").timetuple()))
    except ValueError:
        # If parsing fails, return 0
        return 0