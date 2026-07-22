import requests
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import base64
from dotenv import load_dotenv
import os
from datetime import datetime
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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

    logger.info(f'No of links present: {len(a_links)}')

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
    
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        logger.error(f"Error getting access token: {response.status_code} - {response.text}")
        raise err

    return response.json().get('access_token')

def get_playlist_track_uris(sp, playlist_id):
    track_uris = set()
    offset = 0
    while True:
        results = sp.playlist_tracks(playlist_id, offset=offset)
        items = results.get('items', [])
        if not items:
            break
        for item in items:
            track = item.get('track')
            if track and track.get('uri'):
                track_uris.add(track['uri'])
        offset += len(items)
    return track_uris

def add_tracks_to_playlist(sp, user_info, playlist_id, track_uris):
    existing_uris = get_playlist_track_uris(sp, playlist_id)
    new_uris = [uri for uri in track_uris if uri not in existing_uris]
    
    if not new_uris:
        return 0

    # Spotipy limits to 100 tracks per request
    for i in range(0, len(new_uris), 100):
        sp.user_playlist_add_tracks(user=user_info, playlist_id=playlist_id, tracks=new_uris[i:i+100], position=0)
        
    return len(new_uris)

def main():

    logger.info("Script started")

    DiscoverWeeklyTracks = getDiscoverWeeklyTracks()

    new_access_token = refresh_access_token(f'{REFRESH_ACCESS_TOKEN}')

    sp = spotipy.Spotify(auth=new_access_token)

    user_info = get_user_id(sp)

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
        logger.info(f"Created new playlist: {monthly_playlist_name}")
    else:
        logger.info(f"Playlist already exists: {monthly_playlist_name}")

    
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
        logger.info(f"Created new playlist: {yearly_playlist_name}")
    else:
        logger.info(f"Playlist already exists: {yearly_playlist_name}")

    added_monthly = add_tracks_to_playlist(sp, user_info, monthly_playlist_id, DiscoverWeeklyTracks)
    logger.info(f"Added {added_monthly} new tracks to playlist: {monthly_playlist_name}")     

    added_yearly = add_tracks_to_playlist(sp, user_info, yearly_playlist_id, DiscoverWeeklyTracks)
    logger.info(f"Added {added_yearly} new tracks to playlist: {yearly_playlist_name}")

    logger.info('Script Executed Successfully')

if __name__ == '__main__':
    main()