from app import db

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String())
    display_name = db.Column(db.String())
    description = db.Column(db.String())
    profile_image_url = db.Column(db.String())
    view_count = db.Column(db.Integer)
    email = db.Column(db.String())
    created_at = db.Column(db.Date)

    likes = db.relationship(
        'Clip',
        secondary="likes"
    )

class Clip(db.Model):
    __tablename__ = 'clips'
    id = db.Column(db.String(), primary_key=True)
    url = db.Column(db.String())
    embed_url = db.Column(db.String())
    broadcaster_id = db.Column(db.Integer)
    broadcaster_name = db.Column(db.String())
    creator_id = db.Column(db.Integer)
    creator_name = db.Column(db.String())
    game_id = db.Column(db.Integer)
    title = db.Column(db.String())
    view_count = db.Column(db.Integer)
    created_at = db.Column(db.Date)
    thumbnail_url = db.Column(db.String())
    duration = db.Column(db.Integer)
    description = db.Column(db.String(150))

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'),
        nullable=False)
    user = db.relationship('User',
        backref=db.backref('clips', lazy=True))

class Like(db.Model):
    __tablename__ = 'likes'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'),
        nullable=False, primary_key=True)

    clip_id = db.Column(db.String(), db.ForeignKey('clips.id'),
        nullable=False, primary_key=True)

class Game(db.Model):
    __tablename__ = 'games'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    box_art_url = db.Column(db.String())
