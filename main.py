import requests
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import base64
from dotenv import load_dotenv
import os

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

    # print(soup)

    DiscoverWeeklyTracks = []

    a_links = soup.find_all('a')

    print('No of links present: ', len(a_links))

    for x in a_links:
        if x['href'].startswith('/track'):
            # print(x['href'][7:])
            uri = 'spotify:track:' + str(x['href'][7:])
            # print(uri)
            DiscoverWeeklyTracks.append(uri)

    # print(DiscoverWeeklyTracks)

    return DiscoverWeeklyTracks

def get_user_id(sp):
    return sp.me()["id"]

# Function to refresh access token
def refresh_access_token(refresh_token):
    
    payload = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
    }
    auth_header = {'Authorization': 'Basic ' + base64.b64encode((f'{CLIENT_ID}' + ':' + f'{CLIENT_ID_SECRET}').encode()).decode()}
    response = requests.post('https://accounts.spotify.com/api/token', data=payload, headers=auth_header)
    return response.json().get('access_token')

def main():

    print("Script started")

    DiscoverWeeklyTracks = getDiscoverWeeklyTracks()

    new_access_token = refresh_access_token(f'{REFRESH_ACCESS_TOKEN}')

    sp = spotipy.Spotify(auth=new_access_token)

    user_info = get_user_id(sp)

    sp.user_playlist_add_tracks(user=user_info, playlist_id=f'{ARCHIVE_WEEKLY_ID}', tracks=DiscoverWeeklyTracks)
            
    print('Script Executed Successfully')

if __name__ == '__main__':
    main()