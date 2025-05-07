import json
import urllib.request
import os
import time
STEAM_API_KEY = os.getenv("STEAM_API_KEY")

#                                                              //STEAM WEB API FUNCTIONS//

class PrivateAccount(Exception):
    pass

class NoAchievements(Exception):
    pass

class NoStoreFront(Exception):
    pass


MAX_RETRIES = 3
RETRY_DELAY = 1
HEADERS ={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}    

#Fetches achievement data for a given game by app id, returns a list of tuples of the form (achievement_name, achievement_percentage)
def GetGlobalAchievementPercentagesForApp(app_id):
    url = f"http://api.steampowered.com/ISteamUserStats/GetGlobalAchievementPercentagesForApp/v0002/?gameid={app_id}"
    attempt = 0

    while attempt < MAX_RETRIES:
        try:
            request = urllib.request.Request(url, headers=HEADERS)
            try:
                with urllib.request.urlopen(request) as response:
                    data = response.read()
                    if not data:
                        raise Exception(f"The steam api is not responding correctly for endpoint GetGlobalAchievementPercentagesForApp({app_id})")
                    result = json.loads(data)
                    if not result["achievementpercentages"]["achievements"]:
                        raise NoAchievements(f"app_id: {app_id} has no achievements")
                    achievements = result["achievementpercentages"]["achievements"]
                    return [(achievement["name"], achievement["percent"]) for achievement in achievements]
            except urllib.error.HTTPError as e:
                if e.code == 400:
                    raise NoAchievements(f"app_id: {app_id} has no achievements")
                else:
                    raise  # Re-raise other HTTP errors to be handled by the outer try-except
        except NoAchievements as e:
            print(e)
            break
        except Exception as e:
            attempt += 1
            if attempt >= MAX_RETRIES:
                print(f"Attempt {attempt} for GetGlobalAchievementPercentagesForApp({app_id}) failed: {e}")
                raise e
            time.sleep(RETRY_DELAY)


#Fetches profile data for a given player, returns steamid, username, avatar_url
def GetPlayerSummaries(steam_id):
    url = f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={STEAM_API_KEY}&steamids={steam_id}"
    attempt = 0
    while attempt < MAX_RETRIES:
        try:
            request = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(request) as response:
                data = response.read()
                if not data:
                        raise Exception(f"The steam api is not responding correctly for endpoint GetPlayerSummaries({steam_id})")
                result = json.loads(data) 
                player_summary = result["response"]["players"][0]
                if player_summary["communityvisibilitystate"] != 3:
                    raise PrivateAccount("The provided account is private")
                return player_summary["steamid"], player_summary["personaname"], player_summary["avatarfull"]
        except Exception as e:
            attempt += 1
            if attempt >= MAX_RETRIES:
                print(f"Attempt {attempt} for GetPlayerSummaries({steam_id}) failed: {e}")
                raise e
            time.sleep(RETRY_DELAY)


#Fetches achievement data for a given player, returns the games name and a list of tuples of the form (apiname, achieved, unlocktime, name, description)
def GetPlayerAchievements(steam_id, app_id):
    url = f"https://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v0001/?appid={app_id}&key={STEAM_API_KEY}&steamid={steam_id}&l='en'"  
    attempt = 0
    while attempt < MAX_RETRIES:
        try:
            request = urllib.request.Request(url, headers=HEADERS)
            try:
                with urllib.request.urlopen(request) as response:
                    data = response.read()
                    if not data:
                        raise Exception(f"The steam api is not responding correctly for endpoint GetPlayerAchievements({steam_id}, {app_id})")
                    result = json.loads(data)
                    if not result["playerstats"]["success"]:
                        raise NoAchievements(f"app_id: {app_id} has no achievements")
                    if not result["playerstats"].get("achievements"):
                        raise NoAchievements(f"app_id: {app_id} has no achievements")
                    game_name = result["playerstats"]["gameName"]
                    achievement_data = [
                        (
                            achievement["apiname"],
                            achievement["achieved"],
                            achievement["unlocktime"],
                            achievement["name"],
                            achievement["description"],
                        )
                        for achievement in result["playerstats"]["achievements"]
                    ]
                    return game_name, achievement_data
            except urllib.error.HTTPError as e:
                if e.code == 400:
                    raise NoAchievements(f"app_id: {app_id} has no achievements")
                else:
                    raise  # Re-raise other HTTP errors to be handled by the outer try-except
        except NoAchievements as e:
            print(e)
            break
        except Exception as e:
            attempt += 1
            if attempt >= MAX_RETRIES:
                print(f"Attempt {attempt} for GetPlayerAchievements({steam_id}, {app_id}) failed: {e}")
                raise e
            time.sleep(RETRY_DELAY)

#Retrieves info about users game library, returns number of games owned and a list of tuples of the form (app_id, game_name, total_playtime, app_img_url, last_time_played)
def GetOwnedGames(steam_id):
    url = f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={STEAM_API_KEY}&steamid={steam_id}&include_appinfo=True&include_played_free_games=True"
    attempt = 0
    while attempt < MAX_RETRIES:
        try:
            request = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(request) as response:
                data = response.read()
                if not data:
                        raise Exception(f"The steam api is not responding correctly for endpoint GetOwnedGames({steam_id})")
                result = json.loads(data) 
                game_count = result["response"]["game_count"]
                games = [
                    (
                        game["appid"],
                        game["name"],
                        game["playtime_forever"],
                        f"http://media.steampowered.com/steamcommunity/public/images/apps/{game['appid']}/{game['img_icon_url']}.jpg",
                        game.get("rtime_last_played", 0)  # Use .get() with a default value of 0
                    )
                    for game in result["response"]["games"]
                ]
                return game_count, games
        except Exception as e:
            attempt += 1
            if attempt >= MAX_RETRIES:
                print(f"Attempt {attempt} for GetOwnedGames({steam_id}) failed: {e}")
                raise e
            time.sleep(RETRY_DELAY)

#Retrieves info about a players recent game data, returns number of games played in the last 2 week, and a list of tuples of the form (app_id, playtime_last_2_weeks)
def GetRecentlyPlayedGames(steam_id):
    url = f"http://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v0001/?key={STEAM_API_KEY}&steamid={steam_id}"
    attempt = 0
    while attempt < MAX_RETRIES:
        try:
            request = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(request) as response:
                data = response.read()
                if not data:
                        raise Exception(f"The steam api is not responding correctly for endpoint GetRecentlyPlayedGames({steam_id})")
                result = json.loads(data) 
                game_count = result["response"]["total_count"]
                games = [(game["appid"], game["playtime_2weeks"]) for game in result["response"]["games"]]
                return game_count, games
        except Exception as e:
            attempt += 1
            if attempt >= MAX_RETRIES:
                print(f"Attempt {attempt} for GetRecentlyPlayedGames({steam_id}) failed: {e}")
                raise e
            time.sleep(RETRY_DELAY)


#Retrieves possibly useful metadata about a given app, returns the games name, a list of developers, a list of publishers, a list of tuples of the form (genre_id, genre_name)
#and the games release date and metacritic score
def GetAppMetadata(app_id):
    url = f"https://store.steampowered.com/api/appdetails/?appids={app_id}&filters=basic,genres,release_date,developers,publishers,metacritic"
    attempt = 0
    while attempt < MAX_RETRIES:
        try:
            request = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(request) as response:
                data = response.read()
                if not data:
                        raise Exception(f"The steam api is not responding correctly for endpoint GetAppMetadata({app_id})")
                result = json.loads(data)
                if result[str(app_id)]["success"] != True:
                    raise NoStoreFront(f"app_id: {app_id} has no storefront")
                metadata = result[str(app_id)]["data"]
                developers = metadata.get("developers", [])
                publishers = metadata.get("publishers", [])
                genres = metadata.get("genres", [])  
                metacritic_score = metadata.get("metacritic", {}).get("score", None)
                return (
                    metadata["name"],
                    developers,
                    publishers,
                    [(genre["id"], genre["description"]) for genre in genres],
                    metadata["release_date"]["date"],
                    metacritic_score
                )
        except NoStoreFront as e:
            print(e)
            break
        except Exception as e:
            attempt += 1
            if attempt >= MAX_RETRIES:
                print(f"Attempt {attempt} for GetAppMetadata({app_id}) failed: {e}")
                raise e
            time.sleep(RETRY_DELAY)

