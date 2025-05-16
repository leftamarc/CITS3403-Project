from app import db
from datetime import datetime
from app.security import hash_password, check_password, check_password_hash
from flask_login import UserMixin

#using werkzeug security atm can change later if needed (just to hash passwords in database)

#TODO: Make some wrapper functions: Calling dbAchievementAdd(name, rate, app_id) is going to be more readable then SQL statements and a function 
#      like getAchievement(name) that returns all the associated data in a python list will be easier to work with


#*******************************************************************************//STEAM API DATA TABLES//************************************************************************

#                                                    /*******************************//ENTITIES//*******************************/

#Represents an achievement
from time import time


# Represents an achievement
class Achievement(db.Model):
    __tablename__ =   'achievement'

    #Unique internal name of the achievement on the steam api
    internal_name = db.Column(db.String(200), primary_key=True)

    #Global achievement rate as a percentage
    rate          = db.Column(db.Integer, nullable=False)

    #App ID of the game the achievement is from
    app_id        = db.Column(db.Integer, db.ForeignKey('game.app_id'), primary_key=True)

    #External name of the achievement on steam
    display_name  = db.Column(db.String(500), nullable=False)

    #Description of the achievement on steam
    description   = db.Column(db.String(500), nullable=False)

    #Creates a new row or updates the existing one for the provided primary keys
    @classmethod
    def upsert(cls, internal_name, rate, app_id, display_name, description):
        achievement = cls.query.filter_by(internal_name=internal_name).first()
        if achievement:
            achievement.rate = rate
            achievement.app_id = app_id
            achievement.display_name = display_name
            achievement.description = description
        else:
            achievement = cls(
                internal_name=internal_name,
                rate=rate,
                app_id=app_id,
                display_name=display_name,
                description=description
            )
            db.session.add(achievement)



'''///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////'''


# Represents a steam game
class Game(db.Model):
    __tablename__ = 'game'

    #Unique ID for the game
    app_id        = db.Column(db.Integer, primary_key=True)

    #Name of the game
    name          = db.Column(db.String(50), nullable=False)

    #Img url of the game
    image         = db.Column(db.String(200), nullable=False)

    #Releaste date of the game as a unix timestamp
    release_date  = db.Column(db.Integer, nullable=False)

    #Metacritic score of the game, if it has one
    metacritic    = db.Column(db.Integer)

    #Creates a new row or updates the existing one for the provided primary keys
    @classmethod
    def upsert(cls, app_id, name, image, release_date, metacritic):
        game = cls.query.filter_by(app_id=app_id).first()
        if game:
            game.name = name
            game.image = image
            game.release_date = release_date
            game.metacritic = metacritic
        else:
            game = cls(
                app_id=app_id,
                name=name,
                image=image,
                release_date=release_date,
                metacritic=metacritic
            )
            db.session.add(game)



'''///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////'''


# Represents a steam user
class Steam_User(db.Model):
    __tablename__ = 'steam_user'
    #Steam ID of the user
    steam_id        =   db.Column(db.Integer, primary_key=True) 
    
    #Most recent username of the user
    username        =   db.Column(db.String(200), nullable=False)
 
    #Url to the users avatar
    image           =   db.Column(db.String(200), nullable=False)

    #Associated SteamWrapped Account ID
    id =  db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    #Total number of games owned
    n_games_owned = db.Column(db.Integer, nullable=False, default=0)

    #Creates a new row or updates the existing one for the provided primary keys
    @classmethod
    def upsert(cls, steam_id, username, image, n_games_owned):
        user = cls.query.filter_by(steam_id=steam_id).first()
        if user:
            user.username = username
            user.image = image
            user.n_games_owned = n_games_owned
        else:
            user = cls(
                steam_id=steam_id,
                username=username,
                image=image,
                n_games_owned=n_games_owned
            )
            db.session.add(user)



'''///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////'''


# Represents a genre
class Genre(db.Model):
    __tablename__ = 'genre'

    #Unique ID of the genre according to steam api
    genre_id      = db.Column(db.Integer, primary_key=True)

    #Name of the genre
    name          = db.Column(db.String(100), nullable=False)

    #Creates a new row or updates the existing one for the provided primary keys
    @classmethod
    def upsert(cls, genre_id, name):
        genre = cls.query.filter_by(genre_id=genre_id).first()
        if genre:
            genre.name = name
        else:
            genre = cls(
                genre_id=genre_id,
                name=name
            )
            db.session.add(genre)



'''///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////'''


# Represents a game developer
class Developer(db.Model):
    __tablename__ = 'developer'

    #Name of the developer
    name          = db.Column(db.String(200), primary_key=True)

    #Creates a new row or updates the existing one for the provided primary keys
    @classmethod
    def upsert(cls, name):
        developer = cls.query.filter_by(name=name).first()
        if not developer:
            developer = cls(name=name)
            db.session.add(developer)



'''///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////'''


# Represents a game publisher
class Publisher(db.Model):
    __tablename__ = 'publisher'

    #Name of the publisher
    name          = db.Column(db.String(200), primary_key=True)

    #Creates a new row or updates the existing one for the provided primary keys
    @classmethod
    def upsert(cls, name):
        publisher = cls.query.filter_by(name=name).first()
        if not publisher:
            publisher = cls(name=name)
            db.session.add(publisher)



'''///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////'''     


# Represents a specific achievement unlocked by a specific user
class User_Achievement(db.Model):
    __tablename__ = 'user_achievement'

    #Internal name of the achievement on steam
    internal_name = db.Column(db.String(500), db.ForeignKey('achievement.internal_name'), primary_key=True)

    #App ID of the game the achievement is from
    app_id        = db.Column(db.Integer, db.ForeignKey('game.app_id'), primary_key=True)

    #Steam ID of the user who has the achievement
    steam_id      = db.Column(db.Integer, db.ForeignKey('steam_user.steam_id'), primary_key=True)

    #Achieved status 0 = false 1 = true
    achieved      = db.Column(db.Integer, nullable=False, default=0)

    #The unlock time as a unix timestamp 0 = never unlocked
    unlock_time   = db.Column(db.Integer, nullable=False, default=0)

    #Creates a new row or updates the existing one for the provided primary keys
    @classmethod
    def upsert(cls, internal_name, app_id, steam_id, achieved, unlock_time):
        user_achievement = cls.query.filter_by(
            internal_name=internal_name, steam_id=steam_id, app_id=app_id).first()
        if user_achievement:
            user_achievement.achieved = achieved
            user_achievement.unlock_time = unlock_time
        else:
            user_achievement = cls(
                internal_name=internal_name,
                app_id=app_id,
                steam_id=steam_id,
                achieved=achieved,
                unlock_time=unlock_time
            )
            db.session.add(user_achievement)



'''///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////'''


# Represents a specific game owned by a specific user
class User_Game(db.Model):
    __tablename__  = 'user_game'

    #Steam ID of the user who owns the game
    steam_id       = db.Column(db.Integer, db.ForeignKey('steam_user.steam_id'), primary_key=True)

    #Unique Application ID of the game
    app_id         = db.Column(db.Integer, db.ForeignKey('game.app_id'), primary_key=True)

    #The users total playtime in the game
    playtime_total = db.Column(db.Integer, nullable=False, default=0)

    #The last time the game was played 0 = never
    last_played    = db.Column(db.Integer, nullable=False, default=0)

    #Creates a new row or updates the existing one for the provided primary keys
    @classmethod
    def upsert(cls, steam_id, app_id, playtime_total, last_played):
        user_game = cls.query.filter_by(steam_id=steam_id, app_id=app_id).first()
        if user_game:
            user_game.playtime_total = playtime_total
            user_game.last_played = last_played
        else:
            user_game = cls(
                steam_id=steam_id,
                app_id=app_id,
                playtime_total=playtime_total,
                last_played=last_played
            )
            db.session.add(user_game)

'''///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////'''


# Represents a specific game tagged with a specific genre
class Game_Genre(db.Model):
    __tablename__ = 'game_genre'

    app_id        = db.Column(db.Integer, db.ForeignKey('game.app_id'), primary_key=True)

    genre_id      = db.Column(db.Integer, db.ForeignKey('genre.genre_id'), primary_key=True)

    #Creates a new row or updates the existing one for the provided primary keys
    @classmethod
    def upsert(cls, app_id, genre_id):
        game_genre = cls.query.filter_by(app_id=app_id, genre_id=genre_id).first()
        if not game_genre:
            game_genre = cls(
                app_id=app_id,
                genre_id=genre_id
            )
            db.session.add(game_genre)



'''///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////'''


# Represents a specific game created by a specific developer
class Developer_Game(db.Model):
    __tablename__ = 'developer_game'

    #Unique Application ID of the game
    app_id        = db.Column(db.Integer, db.ForeignKey('game.app_id'), primary_key=True)

    #Name of the developer
    developer     = db.Column(db.String(500), db.ForeignKey('developer.name'), primary_key=True)

    #Creates a new row or updates the existing one for the provided primary keys
    @classmethod
    def upsert(cls, app_id, developer_name):
        developer_game = cls.query.filter_by(app_id=app_id, developer=developer_name).first()
        if not developer_game:
            developer_game = cls(
                app_id=app_id,
                developer=developer_name
            )
            db.session.add(developer_game)



'''///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////'''     


# Represents a specific game published by a specific publisher
class Publisher_Game(db.Model):
    __tablename__ = 'publisher_game'

    #Unique Application ID of the game
    app_id = db.Column(db.Integer, db.ForeignKey('game.app_id'), primary_key=True)

    # The developer in question
    publisher       =   db.Column(db.String(500), db.ForeignKey('publisher.name'), primary_key=True)

    #Creates a new row or updates the existing one for the provided primary keys
    @classmethod
    def upsert(cls, app_id, publisher_name):
        publisher_game = cls.query.filter_by(app_id=app_id, publisher=publisher_name).first()
        if not publisher_game:
            publisher_game = cls(
                app_id=app_id,
                publisher=publisher_name
            )
            db.session.add(publisher_game)



'''///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////'''        

#********************************************************************************************************************************************************************************




#represents a user login system (using werkzeug security)
class User(db.Model, UserMixin):
    #Name of the publisher
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = hash_password(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)




# Logs the last time an API call was called successfully
class Api_Log(db.Model):
    __tablename__ = 'api_log'
    endpoint = db.Column(db.String(2048), primary_key=True)
    last_called = db.Column(db.Integer)

    # Logs the provided end point
    @classmethod
    def log_api_call(cls, endpoint):
        current_time = int(time())
        api_log = cls.query.filter_by(endpoint=endpoint).first()
        if api_log:
            api_log.last_called = current_time
        else:
            api_log = cls(endpoint=endpoint, last_called=current_time)
            db.session.add(api_log)
        db.session.commit()

    # Returns a boolean if enough time in seconds has passed since the last time this endpoint was called
    @classmethod
    def can_call(cls, endpoint, duration):
        current_time = int(time())
        api_log = cls.query.filter_by(endpoint=endpoint).first()
        if not api_log:
            return True
        return (current_time - api_log.last_called) >= duration

# Saving Cards

class shared_collections(db.Model):
    share_id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Auto-incrementing primary key
    saved_id = db.Column(db.Integer, db.ForeignKey('saved_collections.saved_id'), nullable=False)  # Foreign key, wrapped id 
    id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Foreign key, recipient id

class saved_collections(db.Model):
    saved_id = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    title = db.Column(db.String(255), default="Untitled")  # Updated line
    steam_id = db.Column(db.Integer, db.ForeignKey('steam_user.steam_id'))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

class saved_cards(db.Model):
    card_no = db.Column(db.Integer, primary_key=True, autoincrement=True)
    saved_id = db.Column(db.Integer, db.ForeignKey('saved_collections.saved_id'), nullable=False)
    card = db.Column(db.Text, nullable=False)




