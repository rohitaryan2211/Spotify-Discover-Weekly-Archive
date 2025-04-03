import requests
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import base64
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

CLIENT_ID= os.getenv('client_id')
CLIENT_ID_SECRET = os.getenv('client_secret')
DISCOVER_WEEKLY_URL = os.getenv('discover_weekly_url')
ARCHIVE_WEEKLY_ID = os.getenv('archive_weekly_id')
REFRESH_ACCESS_TOKEN = os.getenv('refresh_access_token')

def getDiscoverWeeklyTracks():

    URL = f'{DISCOVER_WEEKLY_URL}'

    results = requests.get(URL)    
    soup= BeautifulSoup(results.text, "html.parser")    

    DiscoverWeeklyTracks = []

    a_links = soup.find_all('a')

    print('No of links present: ', len(a_links))

    for x in a_links:
        if x['href'].startswith('/track'):
            uri = 'spotify:track:' + str(x['href'][7:])
            DiscoverWeeklyTracks.append(uri)

    return DiscoverWeeklyTracks

def get_user_id(sp):
    return sp.me()["id"]

def refresh_access_token(refresh_token):
    
    payload = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
    }
    auth_header = {'Authorization': 'Basic ' + base64.b64encode((f'{CLIENT_ID}' + ':' + f'{CLIENT_ID_SECRET}').encode()).decode()}
    response = requests.post('https://accounts.spotify.com/api/token', data=payload, headers=auth_header)
    return response.json().get('access_token')

def add_tracks_to_playlist(sp, user_info, playlist_id, track_uris):

    sp.user_playlist_add_tracks(user=user_info, playlist_id=playlist_id, tracks=track_uris, position=0)

def main():

    print("Script started")

    DiscoverWeeklyTracks = getDiscoverWeeklyTracks()

    new_access_token = refresh_access_token(f'{REFRESH_ACCESS_TOKEN}')

    sp = spotipy.Spotify(auth=new_access_token)

    user_info = get_user_id(sp)

    print('Tracks added to Yearly playlist')

    current_date = datetime.now()
    month_year = current_date.strftime("%B %Y")  
    year = current_date.strftime("%Y")
    monthly_playlist_name = f"Discover Weekly Archive {month_year}"
    yearly_playlist_name = f"Discover Weekly Archive {year}"

    monthly_playlist_exists = False
    monthly_playlist_id = None

    playlists = []
    offset = 0
    while True:
        batch = sp.current_user_playlists(limit=50, offset=offset)["items"]
        if not batch:
            break
        playlists.extend(batch)
        offset += 50
    
    ## Check if monthly playlist exists
    for playlist in playlists:
        if playlist["name"] == monthly_playlist_name:
            monthly_playlist_id = playlist["id"]
            monthly_playlist_exists = True
            break

    if not monthly_playlist_exists:
        new_playlist = sp.user_playlist_create(
            user=user_info,
            name=monthly_playlist_name,
            public=True,
            description=f"Auto-generated archive of Discover Weekly tracks for {month_year}"
        )
        monthly_playlist_id = new_playlist["id"]
        print(f"Created new playlist: {monthly_playlist_name}")
    else:
        print(f"Playlist already exists: {monthly_playlist_name}")

    
    yearly_playlist_exists = False
    yearly_playlist_id = None
    
    ## Check if the yearly playlist exists
    for playlist in playlists:
        if playlist["name"] == yearly_playlist_name:
            yearly_playlist_id = playlist["id"]
            yearly_playlist_exists = True
            break

    if not yearly_playlist_exists:
        new_playlist = sp.user_playlist_create(
            user=user_info,
            name=yearly_playlist_name,
            public=True,
            description=f"Auto-generated archive of Discover Weekly tracks for {year}"
        )
        yearly_playlist_id = new_playlist["id"]
        print(f"Created new playlist: {yearly_playlist_name}")
    else:
        print(f"Playlist already exists: {yearly_playlist_name}")

    add_tracks_to_playlist(sp, user_info, monthly_playlist_id, DiscoverWeeklyTracks)
    print(f"Added {len(DiscoverWeeklyTracks)} tracks to playlist: {monthly_playlist_name}")     

    add_tracks_to_playlist(sp, user_info, yearly_playlist_id, DiscoverWeeklyTracks)
    print(f"Added {len(DiscoverWeeklyTracks)} tracks to playlist: {yearly_playlist_name}")

    print('Script Executed Successfully')

if __name__ == '__main__':
    main()