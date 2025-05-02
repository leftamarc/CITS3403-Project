import json
import urllib.request
import os
import time
STEAM_API_KEY = os.getenv("STEAM_API_KEY")

#                                                              //STEAM WEB API FUNCTIONS//

class PrivateAccount(Exception):
    pass

class NoMatches(Exception):
    pass

class RequestFail(Exception):
    pass

MAX_RETRIES = 3
RETRY_DELAY = 1

#Fetches achievement data for a given game by app id, returns a list of tuples of the form (achievement_name, achievement_percentage)
def GetGlobalAchievementPercentagesForApp(app_id):
    url = f"http://api.steampowered.com/ISteamUserStats/GetGlobalAchievementPercentagesForApp/v0002/?gameid={app_id}"
    attempt = 0

    while attempt < MAX_RETRIES:
        try:
            with urllib.request.urlopen(url) as response:
                data = response.read()
                if not data:
                    raise NoMatches("No matching data for input parameters")
                result = json.loads(data) 
                achievements = result["achievementpercentages"]["achievements"]
                return [(achievement["name"], achievement["percent"]) for achievement in achievements]
        except Exception as e:
            attempt += 1
            if attempt >= MAX_RETRIES:
                raise RequestFail(f"Error: {e}")
            time.sleep(RETRY_DELAY)


#Fetches profile data for a given player, returns steamid, username, avatar_url
def GetPlayerSummaries(steam_id):
    url = f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={STEAM_API_KEY}&steamids={steam_id}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    attempt = 0
    while attempt < MAX_RETRIES:
        try:
            request = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(request) as response:
                data = response.read()
                if not data:
                    raise NoMatches("No matching data for input parameters")
                result = json.loads(data) 
                player_summary = result["response"]["players"][0]
                if player_summary["communityvisibilitystate"] != 3:
                    raise PrivateAccount("The provided account is private")
                return player_summary["steamid"], player_summary["personaname"], player_summary["avatarfull"]
        except Exception as e:
            attempt += 1
            if attempt >= MAX_RETRIES:
                print(f"Attempt {attempt} failed: {e}")
                raise RequestFail(f"Error: {e}")
            time.sleep(RETRY_DELAY)


#Fetches achievement data for a given player, returns the games name and a list of tuples of the form (apiname, achieved, unlocktime, name, description)
def GetPlayerAchievements(steam_id, app_id):
    url = f"https://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v0001/?appid={app_id}&key={STEAM_API_KEY}&steamid={steam_id}&l='en'"
    try:
        with urllib.request.urlopen(url) as response:
            data = response.read()
            if not data:
                raise NoMatches("No matching data for input parameters")
            result = json.loads(data) 
            game_name = result["playerstats"]["gameName"]
            achievement_data = [(achievement["apiname"], achievement["achieved"], achievement["unlocktime"], achievement["name"], achievement["description"]) for achievement in result["playerstats"]["achievements"]]
            return game_name, achievement_data
    except Exception as e:
        raise RequestFail(f"Error: {e}")

#Retrieves info about users game library, returns number of games owned and a list of tuples of the form (app_id, total_playtime, app_img_url, last_time_played)
def GetOwnedGames(steam_id):
    url = f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={STEAM_API_KEY}&steamid={steam_id}&include_appinfo=True&include_played_free_games=True"
    try:
        with urllib.request.urlopen(url) as response:
            data = response.read()
            if not data:
                raise NoMatches("No matching data for input parameters")
            result = json.loads(data) 
            game_count = result["response"]["game_count"]
            games = [(game["appid"], game["playtime_forever"], "http://media.steampowered.com/steamcommunity/public/images/apps/"+str(game["appid"])+"/"+game["img_icon_url"]+".jpg", game["rtime_last_played"]) for game in result["response"]["games"]]
            return game_count, games
    except Exception as e:
        raise RequestFail(f"Error: {e}")

#Retrieves info about a players recent game data, returns number of games played in the last 2 week, and a list of tuples of the form (app_id, playtime_last_2_weeks)
def GetRecentlyPlayedGames(steam_id):
    url = f"http://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v0001/?key={STEAM_API_KEY}&steamid={steam_id}"
    try:
        with urllib.request.urlopen(url) as response:
            data = response.read()
            if not data:
                raise NoMatches("No matching data for input parameters")
            result = json.loads(data) 
            game_count = result["response"]["total_count"]
            games = [(game["appid"], game["playtime_2weeks"]) for game in result["response"]["games"]]
            return game_count, games
    except Exception as e:
        raise RequestFail(f"Error: {e}")


#Retrieves possibly useful metadata about a given app, returns the games name, a list of developers, a list of publishers, a list of tuples of the form (genre_id, genre_name)
#and the games release date
def GetAppMetadata(app_id):
    url = f"https://store.steampowered.com/api/appdetails/?appids={app_id}&filters=basic,genres,release_date,developers,publishers,metacritic"
    try:
        with urllib.request.urlopen(url) as response:
            data = response.read()
            if not data:
                raise NoMatches("No matching data for input parameters")
            result = json.loads(data) 
            if result[str(app_id)]["success"] != True:
                raise NoMatches("No matching data for input parameters")
            metadata = result[str(app_id)]["data"]
            return  metadata["name"], metadata["developers"], metadata["publishers"], [(genre["id"], genre["description"]) for genre in metadata["genres"]], metadata["release_date"]["date"]
    except Exception as e:
        raise RequestFail(f"Error: {e}")
      

app_id = 442070
steam_id = 76561199042412978
#GetGlobalAchievementPercentagesForApp(app_id)
#GetPlayerSummaries(steam_id)

print(STEAM_API_KEY)