from app import db

class Achievement(db.Model):
    achievement_name = db.Column(db.String(50), primary_key=True)
    achievement_rate = db.Column(db.Integer, nullable=False) 
    app_id = db.Column(db.Integer, db.ForeignKey('game.app_id'), nullable=False)

class Game(db.Model):
    app_id = db.Column(db.Integer, primary_key=True) 
    game_name = db.Column(db.String(50), nullable=False)
    logo = db.Column(db.String(200), nullable=False)

class User(db.Model):
    steam_id = db.Column(db.Integer, primary_key=True) 
    username = db.Column(db.String(50), nullable=False)
    avatar = db.Column(db.String(200), nullable=False)

class User_Achievements(db.Model):
    achievement_name = db.Column(db.String(50), db.ForeignKey('achievement.achievement_name'), primary_key=True)
    steam_id = db.Column(db.Integer, db.ForeignKey('user.steam_id'), primary_key=True) 

class User_Game(db.Model):
    steam_id = db.Column(db.Integer, db.ForeignKey('user.steam_id'), primary_key=True)
    app_id = db.Column(db.Integer, db.ForeignKey('game.app_id'), primary_key=True)

