#Importing the libraries
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import warnings
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
import streamlit as st
from pathlib import Path
import requests
from bs4 import BeautifulSoup
warnings.filterwarnings("ignore")

#Setting up the Spotify API
#Next we will initialize Spotipy
client_id = st.secrets['CLIENT_ID']
client_secret = st.secrets['CLIENT_SECRET']
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

#Function to get the Billboard Hot 100 songs
def get_billboard_top():
    r = requests.get('https://www.billboard.com/charts/hot-100/').content
    soup = BeautifulSoup(r, 'html.parser')
    n1_song = soup.find_all('h3', attrs={'class': 'c-title a-no-trucate a-font-primary-bold-s u-letter-spacing-0021 u-font-size-23@tablet lrv-u-font-size-16 u-line-height-125 u-line-height-normal@mobile-max a-truncate-ellipsis u-max-width-245 u-max-width-230@tablet-only u-letter-spacing-0028@tablet'})
    songs = soup.find_all('h3', attrs={'class': 'c-title a-no-trucate a-font-primary-bold-s u-letter-spacing-0021 lrv-u-font-size-18@tablet lrv-u-font-size-16 u-line-height-125 u-line-height-normal@mobile-max a-truncate-ellipsis u-max-width-330 u-max-width-230@tablet-only'})
    n1_artist = soup.find_all('span', attrs={'class': 'c-label a-no-trucate a-font-primary-s lrv-u-font-size-14@mobile-max u-line-height-normal@mobile-max u-letter-spacing-0021 lrv-u-display-block a-truncate-ellipsis-2line u-max-width-330 u-max-width-230@tablet-only u-font-size-20@tablet'})
    artists = soup.find_all('span', attrs={'class': 'c-label a-no-trucate a-font-primary-s lrv-u-font-size-14@mobile-max u-line-height-normal@mobile-max u-letter-spacing-0021 lrv-u-display-block a-truncate-ellipsis-2line u-max-width-330 u-max-width-230@tablet-only'})
    df = pd.DataFrame({
        "Song": [song.text for song in songs],
        "Artist": [artist.text for artist in artists]
    })
    df.loc[0] = [n1_song[0].text, n1_artist[0].text]
    df['Song'] = df['Song'].str.replace('\n', '').str.replace('\t', '')
    df['Artist'] = df['Artist'].str.replace('\n', '').str.replace('\t', '')
    df.to_csv('billboard_hot_100.csv', index=False)
    return df

#Reading the dataset
url = "https://dl.dropboxusercontent.com/scl/fi/zc5e1lnzzjw7knzh58vgy/tracks_features.csv?rlkey=6lkmcs1z9ik6gjyj92blk9bw4"
features = pd.read_csv(url)
billboard = get_billboard_top()

#Function to get the song features
def get_song_features(track_id):
    track = sp.track(track_id)
    features = sp.audio_features(track_id)
    song = {
        'explicit': track['explicit'],
        'danceability': features[0]['danceability'],
        'energy': features[0]['energy'],
        'key': features[0]['key'],
        'loudness': features[0]['loudness'],
        'mode': features[0]['mode'],
        'speechiness': features[0]['speechiness'],
        'acousticness': features[0]['acousticness'],
        'instrumentalness': features[0]['instrumentalness'],
        'liveness': features[0]['liveness'],
        'valence': features[0]['valence'],
        'tempo': features[0]['tempo'],
        'duration_ms': features[0]['duration_ms'],
        'time_signature': features[0]['time_signature'],
        'year': track['album']['release_date'][:4],
        'track_id': track_id,
        'name': track['name'],
        'artist': track['artists'][0]['name'],
    }
    return [song]

#Function to get the artist most popular song
def get_popular_song(artist):
    results = sp.search(q=artist, limit=1)
    artist_id = results['tracks']['items'][0]['artists'][0]['id']
    top_tracks = sp.artist_top_tracks(artist_id)
    return top_tracks['tracks'][0]['id']

#Now, we will create a dataframe with the features of the songs in the features dataframe
selected_features = features.drop(columns=['id', 'name', 'album', 'album_id', 'artists', 'artist_ids', 'track_number', 'disc_number', 'release_date'])

#Now, we will scale the features
scaler = StandardScaler()
scaled_features = scaler.fit_transform(selected_features)

#Using the information from the plot, we will use 4 clusters to group the songs
kmeans = KMeans(n_clusters=4, init='k-means++', max_iter=300, n_init=10, random_state=0)
kmeans.fit(scaled_features)

#Now, I will save the clusters in a new variable
cluster = kmeans.predict(scaled_features)

#Now, we will unite the clusters with the features and song information
clustered_features = pd.DataFrame(scaled_features, columns=selected_features.columns)
clustered_features['name'] = features['name']
clustered_features['artists'] = features['artists']
clustered_features['album'] = features['album']
clustered_features['cluster'] = cluster

#Creating the Streamlit app
st.title('Spotify Song Recommender')
st.write('This app will recommend you a song based on the song or artist you choose.')
st.write('If the song or the artist are present in the Billboard Top 100, it will recommend a song from the same list.')
st.write('If the song or the artist are not in the Billboard Top 100, it will search for it in Spotify and recommend a similar song.')

#Creating the input for the user
song = st.text_input('Enter the song you want to get a recommendation for:')
artist = st.text_input('Enter the artist you want to get a recommendation for:')

#Getting the song features
if song:
    try:
        song_id = sp.search(q=song, limit=1)['tracks']['items'][0]['id']
        song_features = get_song_features(song_id)
        song_features = pd.DataFrame(song_features)
        song_cluster = kmeans.predict(scaler.transform(song_features.drop(columns=['track_id', 'name', 'artist'])).values)
        song_cluster = clustered_features[clustered_features['cluster'] == song_cluster[0]]
        song_cluster = song_cluster[song_cluster['name'] != song]
        song_cluster = song_cluster[song_cluster['artists'] != artist]
        if song_cluster.empty:
            st.write('No recommendations found for this song.')
        else:
            st.write('Recommendations for', song, 'by', artist)
            st.write(song_cluster[['name', 'artists']])
    except:
        st.write('Song not found.')
elif artist:
    try:
        song_id = get_popular_song(artist)
        song_features = get_song_features(song_id)
        song_features = pd.DataFrame(song_features)
        song_cluster = kmeans.predict(scaler.transform(song_features.drop(columns=['track_id', 'name', 'artist'])).values)
        song_cluster = clustered_features[clustered_features['cluster'] == song_cluster[0]]
        song_cluster = song_cluster[song_cluster['artists'] != artist]
        if song_cluster.empty:
            st.write('No recommendations found for this artist.')
        else:
            st.write('Recommendations for', artist)
            st.write(song_cluster[['name', 'artists']])
    except:
        st.write('Artist not found.')

#Creating the sidebar
st.sidebar.title('Billboard Hot 100')
st.sidebar.write('Here are the current Billboard Hot 100 songs:')
st.sidebar.write(billboard)

#Creating the footer
st.markdown('Created by [Samuel Carmona](www.linkedin.com/in/samuelcskories)')