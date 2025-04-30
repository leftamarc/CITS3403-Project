from app import db
from datetime import datetime
from app.security import hash_password, check_password
#using werkzeug security atm can change later if needed (just to hash passwords in database)

#TODO: Make some wrapper functions: Calling dbAchievementAdd(name, rate, app_id) is going to be more readable then SQL statements and a function 
#      like getAchievement(name) that returns all the associated data in a python list will be easier to work with


#*******************************************************************************//STEAM API DATA TABLES//************************************************************************

#                                                    /*******************************//ENTITIES//*******************************/

#Represents an achievement
class Achievement(db.Model):
    #The internal name of the achievement on steam
    internal_name   =   db.Column(db.String(200), primary_key=True)

    #The percentage of players who have unlocked this achievement
    rate            =   db.Column(db.Integer, nullable=False)

    #The application ID of the game the achievement is from
    app_id          =   db.Column(db.Integer, db.ForeignKey('game.app_id'), nullable=False)

    #The display name of the achievement on steam
    display_name    =   db.Column(db.String(500), nullable=False)

    #The description of the achievement on steam
    description     =   db.Column(db.String(500))


#Represents a steam game
class Game(db.Model):
    #Internal application ID of the game on steam
    app_id          =   db.Column(db.Integer, primary_key=True) 

    #Name of the game
    name            =   db.Column(db.String(50), nullable=False)

    #Url to the games icon
    image           =   db.Column(db.String(200), nullable=False)

    #Release date
    release_date    =   db.Column(db.Integer)


#Represents a steam user
class Steam_User(db.Model):
    #Steam ID of the user
    steam_id        =   db.Column(db.Integer, primary_key=True) 
    
    #Most recent username of the user
    username        =   db.Column(db.String(200), nullable=False)
 
    #Url to the users avatar
    image           =   db.Column(db.String(200), nullable=False)


#Represents a genre
class Genre(db.Model):
    #The internal ID of the genre tag on steam
    genre_id        =   db.Column(db.Integer, primary_key=True)

    #The name of the genre
    name            =   db.Column(db.String(100), nullable=False)


#Represents a game developer
class Developer(db.Model):
    #Name of the developer
    name            =  db.Column(db.String(200), primary_key=True)


#Reprents a game publisher
class Publisher(db.Model):
    #Name of the publisher
    name            = db.Column(db.String(200), primary_key=True)    

#                                                   /*******************************//ASSOCIATIONS//*******************************/

#Represents a specific achievement that could be unlocked by a specific user
class User_Achievements(db.Model):
    #The achievement in question
    name            =   db.Column(db.String(500), db.ForeignKey('achievement.internal_name'), primary_key=True)

    #The user in question
    steam_id        =   db.Column(db.Integer, db.ForeignKey('steam_user.steam_id'), primary_key=True) 

    #Whether or not the achievement has been achieved by the player
    achieved        =   db.Column(db.Integer, nullable=False)

    #The time the achievement was unlocked, if ever
    unlock_time     =   db.Column(db.Integer)


#Represents a specific game owned by a specific user
class User_Game(db.Model):
    #The user in question
    steam_id        =   db.Column(db.Integer, db.ForeignKey('steam_user.steam_id'), primary_key=True)

    #The game in question
    app_id          =   db.Column(db.Integer, db.ForeignKey('game.app_id'), primary_key=True)

    #Total play time
    playtime_total  =   db.Column(db.Integer, nullable=False)

    #Playtime last 2 weeks
    playtime_2wk    =   db.Column(db.Integer, nullable=False)

    #Last played
    last_played     =   db.Column(db.Integer, nullable=False)


#Reprents a specific game tagged with a specific genre
class Game_Genre(db.Model):
    # The game in question
    app_id          =   db.Column(db.Integer, db.ForeignKey('game.app_id'), primary_key=True)

    # The genre in question
    genre_id        =   db.Column(db.Integer, db.ForeignKey('genre.genre_id'), primary_key=True)


#Reprents a specific game created by a specific developer
class Developer_Games(db.Model):
    # The game in question
    app_id          =   db.Column(db.Integer, db.ForeignKey('game.app_id'), primary_key=True)

    # The developer in question
    developer       =   db.Column(db.String(500), db.ForeignKey('developer.name'), primary_key=True)


#Reprents a specific game published by a specific publisher
class Publisher_Games(db.Model):
    # The game in question
    app_id          =   db.Column(db.Integer, db.ForeignKey('game.app_id'), primary_key=True)

    # The developer in question
    publisher       =   db.Column(db.String(500), db.ForeignKey('publisher.name'), primary_key=True)

#********************************************************************************************************************************************************************************




#represents a user login system (using werzeug security)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = hash_password(password)