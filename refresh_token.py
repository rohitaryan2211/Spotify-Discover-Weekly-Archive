import os
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv('client_id')
CLIENT_ID_SECRET = os.getenv('client_secret')

sp_oauth = SpotifyOAuth(
    client_id= f'{CLIENT_ID}',
    client_secret = f'{CLIENT_ID_SECRET}',
    redirect_uri = "http://localhost:8080/",
    scope = "playlist-read-private playlist-modify-public playlist-modify-private",
)
token = sp_oauth.get_access_token()
refresh_token = token["refresh_token"]

print(refresh_token)