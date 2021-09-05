from flask import Flask, render_template, request, redirect, session, flash, jsonify
import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc
from sqlalchemy.sql import func
import requests
import json
from hidden_stuff import SECRET_KEY, REDIRECT_URI, CLIENT_SECRET, CLIENT_ID

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///capstone'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = SECRET_KEY
db = SQLAlchemy(app)

from models import User, Clip, Like
db.create_all()

### Logic Functions

# Functions that make api requests

def get_user_dict(token):
    """Returns a dictionary with Twitch.tv user data grabbed using an access token"""

    # making the request
    headers = {'Authorization': f'Bearer {token}', 'Client-Id': CLIENT_ID}
    r = requests.get("https://api.twitch.tv/helix/users", headers=headers)

    # If unauthorized, token is likely bad
    if r.status_code == 401:
        session.pop('access_token', None)
        return None

    # turning response into a dict with information we need
    data = json.loads(r.content)
    data = data.get('data')[0]
    user_data = {
        'id' : data.get('id'),
        'login' : data.get('login'),
        'display_name' : data.get('display_name'),
        'description' : data.get('description'),
        'profile_image_url' : data.get('profile_image_url'),
        'view_count' : data.get('view_count'),
        'email' : data.get('email'),
        'created_at' : data.get('created_at')
    }

    return user_data

def get_clip_dict(id, token):
    """Makes a Twitch api request using the logged in users access token to get a users clips by ID"""

    # making the request
    headers = {'Authorization': f'Bearer {token}', 'Client-Id': CLIENT_ID}
    r = requests.get(f"https://api.twitch.tv/helix/clips?id={id}", headers=headers)

    # If unauthorized, token is likely bad
    if r.status_code == 401:
        session.pop('access_token', None)
        return None
    
    # extracting list of clips from response data
    data = json.loads(r.content)
    data = data.get('data')[0]

    return data

def token_to_clips(token):
    """Gets a users clips using their access token"""

    # getting the users dict for easy access to their id
    user = get_user_dict(token)

    # if user is None, access token is likely bad, start auth
    if user is None:
        return redirect('/auth')

    # get user id from user dict
    user_id = user.get('id')

    # making the request
    headers = {'Authorization': f'Bearer {token}', 'Client-Id': CLIENT_ID}
    r = requests.get(f"https://api.twitch.tv/helix/clips?broadcaster_id={user_id}", headers=headers)

    # if unauthorized, token is bad. Return None
    if r.status_code == 401:
        session.pop('access_token', None)
        return None

    # formatting response data as a list
    data = json.loads(r.content)
    clips = data.get('data')

    return clips

def code_to_token(code):
    """Get users access token from oauth code. Returns the token"""

    # making the request
    r = requests.post("https://id.twitch.tv/oauth2/token", data={'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET,
    'code': code,
    'grant_type': 'authorization_code',
    'redirect_uri': REDIRECT_URI})

    # returning the access token from response
    data = r.json()
    return data.get('access_token')

def user_exist(token):
    """Returns boolean if user exists in our database. We dont check for a bad token here, becuase this function is only called with a fresh token"""

    # getting user data for access to user id
    user = get_user_dict(token)

    # check if user exist
    exists = db.session.query(User.id).filter_by(id=user.get('id')).first() is not None

    return exists

def authed():
    """Returns boolean if user is authed"""

    return 'access_token' in session


### View Functions

# Clips

@app.route('/clips')
def list_clips():
    """Displays all posted clips sorted by total likes"""

    # if user not authed, start auth proccess
    if not authed():
        return redirect('/auth')

    # querying clips from database ordered by total likes
    clips = db.session.query(Clip, func.count(Like.user_id).label('total')).join(Like, isouter=True).group_by(Clip).order_by('total', Clip.created_at).all()

    # we need the current user's likes for visual representation of what they already liked
    user = get_user_dict(session['access_token'])

    # if user is non, token is bad. start auth
    if user is None:
        return redirect('/auth')

    # getting the user from our database to see what posts they like
    user = User.query.get(user.get('id'))

    return render_template('clips.html', clips=clips, likes=user.likes)

@app.route('/clips/add', methods=['POST'])
def add_clip():
    """POST route for adding a new clip to the database"""

    # if user not authed, reauth
    if not authed():
        return redirect('/auth')

    # grabbing the clips description and id from our html form
    desc = request.form.get('desc')
    clip_id = request.form.get('clip_id')

    # getting the clips full data from Twitch.tv
    clip = get_clip_dict(clip_id, session['access_token'])

    # getting the users data from Twitch.tv
    user = get_user_dict(session['access_token'])

    # if user is None, token is bad, reauth
    if user is None:
        return redirect('/auth')

    # getting the current users id
    userid=user.get('id')

    # creating a new clip from all our data
    new_clip = Clip(id=clip.get('id'), url=clip.get('url'), embed_url=clip.get('embed_url'), broadcaster_id=clip.get('broadcaster_id'), broadcaster_name=clip.get('broadcaster_name'), creator_id=clip.get('creator_id'), creator_name=clip.get('creator_name'), game_id=clip.get('game_id'), title=clip.get('title'), view_count=clip.get('view_count'), created_at=datetime.date.today(), thumbnail_url=clip.get('thumbnail_url'), duration=clip.get('duration'), description=desc, user_id=userid )

    # trying to add the clip to our database
    try:
        db.session.add(new_clip)
        db.session.commit()
        flash('clip added!')
    except exc.IntegrityError:
        db.session.rollback()
        flash('something went wrong!')
    
    return redirect(f'/users/{userid}')

@app.route('/clips/<id>/vote/add', methods=['POST'])
def vote_clip(id):
    """POST route for liking a clip"""

    # getting the clip from databse to like
    clip = Clip.query.filter_by(id=id).first()

    # getting the current user
    user = get_user_dict(session['access_token'])

    # creating the like from clip and user id
    like = Like(user_id = user.get('id'), clip_id = id)

    # trying to add the like to database
    try:
        db.session.add(like)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        return jsonify('failed')
    
    return jsonify('success')

@app.route('/clips/<id>/vote/delete', methods=['POST'])
def unvote_clip(id):
    """POST route for unliking a post"""

    # getting the clip from the clip id
    clip = Clip.query.filter_by(id=id).first()

    # getting the current user
    user = get_user_dict(session['access_token'])

    # getting the like to be deleted
    like = Like.query.filter_by(user_id=user.get('id'), clip_id=id).first()

    # trying to delete the like
    try:
        db.session.delete(like)
        db.session.commit()
    except exc.IntegrityError:
        db.session.rollback()
        return jsonify('failed')

    return jsonify('success')

# Users

@app.route('/profile')
def profile_page():
    """Displays the logged in users profile taken from Twitch.tv and allows the user to share clips of their channel"""

    # If user not authed, start auth proccess
    if not authed():
        return redirect('/auth')

    # Get the users information as a dictionary using their session
    user = get_user_dict(session['access_token'])

    # If response from attempting to grab the user is None, the token is likely invalid, so start auth proccess
    if user is None:
        return redirect('/auth')

    # Get the users clips as a list using their access token
    clips = token_to_clips(session['access_token'])

    # If response from attempting to grab the clips is None, the token is likely invalid, so start auth proccess
    if clips is None:
        return redirect('/auth')
    
    return render_template('profile.html', user=user, clips=clips)

@app.route('/users/<id>')
def view_user(id):
    """Displays the profile of any user by id along with clips they have publicly shared"""

    # If user not authed, start auth proccess
    if not authed():
        return redirect('/auth')

    # querying to get the requested user
    user = User.query.filter_by(id = id).first()

    # querying to get the requested users clips
    clips = Clip.query.filter_by(user_id = id)

    return render_template('user.html', user=user, clips=clips, likes=user.likes)

# Authentication

@app.route("/")
def home():
    """Redirects to lander if no user and to clips if there is a user"""
    if not authed():
        return render_template('lander.html')

    return redirect('/clips')

@app.route("/auth")
def auth():
    """Redirects to the twitch oauth url, That url sends users to /grab-code"""

    return redirect(f'https://api.twitch.tv/kraken/oauth2/authorize?response_type=code&client_id=g37b9kh93q0fiihc931e29gwihf2q9&redirect_uri={REDIRECT_URI}&scope=user_read')

@app.route("/grab-code")
def auth_to_code():
    """uses the code to get an access token and then sends users to their profile page"""

    # getting the oauth code from request
    code = request.args.get("code")

    # turning the code into a token
    token = code_to_token(code)

    # adding the token to user session
    session['access_token'] = token

    # if user is not currently in our database, add them
    if not user_exist(session['access_token']):

        # getting user data from Twitch.tv for our database
        user_data = get_user_dict(session['access_token'])

        # creating a new user from api data
        user = User(id=user_data.get('id'), login=user_data.get('login'), display_name=user_data.get('display_name'), description=user_data.get('description'), profile_image_url=user_data.get('profile_image_url'), view_count=user_data.get('view_count'), email=user_data.get('email'), created_at=user_data.get('created_at'))

        # trying to add the user
        try:
            db.session.add(user)
            db.session.commit()
            flash('welcome new user! share one of your channel clips!')
        except exc.IntegrityError:
            db.session.rollback()
            flash('something went wrong!')

        return redirect('/profile')
    return redirect('/profile')









