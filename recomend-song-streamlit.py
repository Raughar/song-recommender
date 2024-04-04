#Importing the libraries
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import warnings
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
import streamlit as st
warnings.filterwarnings("ignore")

#We will start by loading the data
url = "https://dl.dropboxusercontent.com/scl/fi/zc5e1lnzzjw7knzh58vgy/tracks_features.csv?rlkey=6lkmcs1z9ik6gjyj92blk9bw4"
billboard = pd.read_csv(r'files\billboard_hot_100.csv')
features = pd.read_csv(url)

#Next we will initialize Spotipy
client_id = st.secrets['CLIENT_ID']
client_secret = st.secrets['CLIENT_SECRET']
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

#Creating a function to get the song features, year, duration, explicit, and time signature
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

#Function to get the most popular song of the artist
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

#Creting the song recomendation system
"""
Recommends a song based on user input of song or artist name.
Uses the Billboard Hot 100 and Spotify data to provide recommendations.
"""

# Asking the user if they want to search by song or artist
select = input('Do you want to search by song or artist? ')
out_song = ''

# If the user selects song, we will ask for the name of the song
if select.lower() == 'song':
    song = input('Enter the name of a song: ')
    
    # Checking if the song is in the Billboard Hot 100
    if song in list(billboard['Song']):
        filtered_billboard = billboard[billboard['Song'] != song]
        random_song = filtered_billboard.sample()
        print(f'We recommend the song {random_song["Song"].values[0]} by {random_song["Artist"].values[0]}')
    
    # If the song is not in the Billboard Hot 100, we will ask the user if they want a random song that is not in the Billboard Hot 100
    else:
        print('The song is not in the Billboard Hot 100')
        out_song = input('Would you like a random song that is not in the Billboard Hot 100? (Y/N) ')

# If the user selects artist, we will ask for the name of the artist
else:
    artist = input('Enter the name of the artist: ')
    
    # Checking if the artist is in the Billboard Hot 100
    if artist in list(billboard['Artist']):
        # Getting a random song from the artist
        filtered_billboard = billboard[billboard['Artist'] == artist]
        random_song = filtered_billboard.sample()
        print(f'We recommend the song {random_song["Song"].values[0]} by {random_song["Artist"].values[0]}')
    
    # If the artist is not in the Billboard Hot 100, we will ask the user if they want a random song that is not in the Billboard Hot 100
    else:
        print('The artist is not in the Billboard Hot 100')
        out_song = input('Would you like a random song that is not in the Billboard Hot 100? (Y/N) ')

# If the users wants a random song, we will get a random song until the user decides to stop
while out_song.lower() == 'y':
    # Asking the user for the name of a song they like
    if select.lower() == 'song':
        # Searching for the song in the features dataframe and recommending a song that is in the same cluster
        if song in list(features['name']):
            song_index = features[features['name'] == song].index[0]
            song_features = selected_features.iloc[song_index]
            song_features = scaler.transform([song_features])
            song_cluster = kmeans.predict(song_features)
            similar_songs = clustered_features[clustered_features['cluster'] == song_cluster[0]].sample()
            print(f'We recommend the song {similar_songs["name"].values[0]} by {similar_songs["artists"].values[0]}')
            out_song = input('Would you like another recommendation? (Y/N) ')

        # If the song is not in the features dataframe, we will search for the song in Spotify and recommend a song that is in the same cluster
        elif song not in list(features['name']):
            
            # Searching for the song in Spotify with the help of Spotipy
            results = sp.search(q=song, limit=1)

            # Getting the song features
            song_id = results['tracks']['items'][0]['id']
            song_features = get_song_features(song_id)
            song_features = pd.DataFrame(song_features)
            song_features = song_features.drop(columns=['track_id', 'name', 'artist'])
            song_features = scaler.transform(song_features)
            song_cluster = kmeans.predict(song_features)
            similar_songs = clustered_features[clustered_features['cluster'] == song_cluster[0]].sample()
            print(f'We recommend the song {similar_songs["name"].values[0]} by {similar_songs["artists"].values[0]}')
            out_song = input('Would you like another recommendation? (Y/N) ')
        
        else:
            print('Impossible to find the song')
            out_song = input('Would you like another recommendation? (Y/N) ')
            
    elif select.lower() == 'artist':
        #Getting the artist's most popular song
        song_id = get_popular_song(artist)
        song_features = get_song_features(song_id)
        song_features = pd.DataFrame(song_features)
        song_features = song_features.drop(columns=['track_id', 'name', 'artist'])
        song_features = scaler.transform(song_features)
        song_cluster = kmeans.predict(song_features)
        similar_songs = clustered_features[clustered_features['cluster'] == song_cluster[0]].sample()
        print(f'We recommend the song {similar_songs["name"].values[0]} by {similar_songs["artists"].values[0]}')
        out_song = input('Would you like another recommendation? (Y/N) ')
    
print('Thank you for using the program!')