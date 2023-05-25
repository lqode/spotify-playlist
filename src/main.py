import os
import requests
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyOAuth


BILLBOARD_URL = "https://www.billboard.com/charts/hot-100"
CLIENT_ID = os.environ["SPOTIFY_CLIENT_ID"]
CLIENT_SECRET = os.environ["SPOTIFY_CLIENT_SECRET"]
CLIENT_REDIRECT_URI = os.environ["SPOTIFY_REDIRECT_URI"]

scope = "playlist-modify-private"
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=CLIENT_REDIRECT_URI,
        scope=scope,
        show_dialog=True,
        cache_path="token.txt"
    )
)
user_id = sp.current_user()["id"]
# Get input date from user
date = input("Which year do you want to travel to? Type the date in this format YYYY-MM-DD:")

# Call Billboard URIs to get top 100 songs
response = requests.get(f"{BILLBOARD_URL}/{date}")
billboard_webpage = response.text

# beautiful soup instantiate
soup = BeautifulSoup(billboard_webpage, "html.parser")
songs = soup.select(".o-chart-results-list__item h3")
# store titles of top 100 song
song_titles = [song.getText().strip() for song in songs]

# Get the song URIs from Spotify
song_uris = []
year = date.split("-")[0]
for song in song_titles:
    result = sp.search(q=f"track:{song} year:{year}", type="track")
    try:
        uri = result["tracks"]["items"][0]["uri"]
        song_uris.append(uri)
    except IndexError:
        print(f"{song} doesn't exist in Spotify. Skipped")

# create new playlist on Spotify and add the top 100 songs to it
playlist = sp.user_playlist_create(user=user_id, name=f"{date} Billboard 100", public=False)
sp.playlist_add_items(playlist_id=playlist["id"], items=song_uris)
