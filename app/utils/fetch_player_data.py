import time as tm
from datetime import datetime
from app.models import Game, User_Game, Developer, Developer_Game, Publisher, Publisher_Game, Genre, Game_Genre, Achievement, User_Achievement, Steam_User
from app.utils.api import GetPlayerSummaries, GetOwnedGames, GetAppMetadata, GetPlayerAchievements, GetGlobalAchievementPercentagesForApp

def FetchPlayerData(steam_id):
    try:
        # Update steam info
        steamid, username, avatar_url = GetPlayerSummaries(steam_id)
        n_game_owned, library = GetOwnedGames(steam_id)
        Steam_User.upsert(steam_id, username, avatar_url, n_game_owned)

        # Update game info for all owned games
        for game in library:
            app_id = game[0]
            print(f'\nfetching data for app_id {app_id}')
            game_name = game[1]
            playtime = (game[2] / 60)
            image = game[3]
            last_played = game[4]

            try:
                game_name, developers, publishers, genres, release_date, metacritic = GetAppMetadata(app_id)
            except:
                continue

            # Convert release_date to Unix timestamp using the new function
            release_date_timestamp = convert_to_unix_timestamp(release_date)

            Game.upsert(app_id, game_name, image, release_date_timestamp, metacritic)
            User_Game.upsert(steam_id, app_id, playtime, last_played)

            # Update developers
            for developer in developers:
                Developer.upsert(developer)
                Developer_Game.upsert(app_id, developer)

            # Update publishers
            for publisher in publishers:
                Publisher.upsert(publisher)
                Publisher_Game.upsert(app_id, publisher)

            # Update genres
            for genre in genres:
                Genre.upsert(genre[0], genre[1])
                Game_Genre.upsert(app_id, genre[0])

            # Fetch achievements
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
                print(e)
                continue

    except Exception as e:
        raise

def convert_to_unix_timestamp(release_date):
    if not release_date:
        return 0
    try:
        # Try parsing "Day Month, Year" (e.g., "28 Mar, 2017")
        return int(tm.mktime(datetime.strptime(release_date, "%d %b, %Y").timetuple()))
    except ValueError:
        # If parsing fails, return 0
        return 0