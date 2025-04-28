from app import db

#TODO: Make some wrapper functions: Calling dbAchievementAdd(name, rate, app_id) is going to be more readable then SQL statements and a function 
#      like getAchievement(name) that returns all the associated data in a python list will be easier to work with


#Represents an achievement
class Achievement(db.Model):
    achievement_name = db.Column(db.String(50), primary_key=True)
    #The internal name of the achievement on steam
    achievement_rate = db.Column(db.Integer, nullable=False)
    #The percentage of players who have unlocked this achievement
    app_id = db.Column(db.Integer, db.ForeignKey('game.app_id'), nullable=False)
    #The application ID of the game the achievement is from

#Represents a steam game
class Game(db.Model):
    app_id = db.Column(db.Integer, primary_key=True) 
    #Internal application ID of the game on steam
    game_name = db.Column(db.String(50), nullable=False)
    #Name of the game
    logo = db.Column(db.String(200), nullable=False)
    #Url to the games icon

#Represents a steam user
class User(db.Model):
    steam_id = db.Column(db.Integer, primary_key=True) 
    #Steam ID of the user
    username = db.Column(db.String(50), nullable=False)
    #Most recent username of the user
    avatar = db.Column(db.String(200), nullable=False)
    #Url to the users avatar


#Represents a specific achievement unlocked by a specific user
class User_Achievements(db.Model):
    #The achievement in question
    achievement_name = db.Column(db.String(50), db.ForeignKey('achievement.achievement_name'), primary_key=True)
    #The user in question
    steam_id = db.Column(db.Integer, db.ForeignKey('user.steam_id'), primary_key=True) 

#Represents a specific game owned by a specific user
class User_Game(db.Model):
    #The user in question
    steam_id = db.Column(db.Integer, db.ForeignKey('user.steam_id'), primary_key=True)
    #The game in question
    app_id = db.Column(db.Integer, db.ForeignKey('game.app_id'), primary_key=True)

