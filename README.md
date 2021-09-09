# Twitch Clip Sharing App

A simple web app allowing users to share and like twitch clips. User accounts and clip data is taken from the twitch API and stored in a databse. Users are authenticated using Oauth2.

## Features
- View a list of Twitch clips from your channel that can be posted.
- View and like other users clips.
- View popular clips sorted by date and number of likes.
- View other users profile page with a list of their clips and a link to their Twitch channel.

## Design Choice (User Authentication)
I wanted to mantain integrity on the app by ensuring that users used the same username on both the app and Twitch.tv. This way, users could not say they are someone they are not. To do this, I needed to use Oauth offered by Twitch, but I had to decicde how to implement it effectively.

### Alternatives
1. The first option was to have users create an account on the app and then allow them to connect their Twitch account. 
2. The second option was to have users create their account on the app using their Twitch account

I Went with option 2 for this project to keep the project simple while protecting users sensitive information. 

Option 1. Creates unnecessary risk for the users by storing their passwords in a database. Using Option 2, we store the user's access token for the Twitch API in their browser cookies. We can then request it from them as needed. If the users access token is ever expired or revoked, we attempt to get a new one.

To check what user is currently logged in, we make a GET request to https://api.twitch.tv/helix/users using the access token in the users browser cookies. The response is the logged in users information. This way we can get the user's id and store that in our database along with their profile and clips. The users id from twitch is how we keep track of them in our database.

## Design Choice (AJAX vs. back-end requests)
Most requests are made on the server side, but AJAX is used when a user likes or dislikes a post. 

I used AJAX so that users could like and dislike posts without the page refreshing on them. 

## Design Choice (Clips)
A user can only share clips that were taken on their channel. This is validated using their access token and the Twitch API. 

## Technologies
- Twitch API and Oauth
- Python
- Javascript 

## Deployment
App is deployed at https://twitchclipapp.herokuapp.com
