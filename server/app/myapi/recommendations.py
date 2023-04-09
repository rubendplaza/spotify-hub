from django.shortcuts import render

from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response

import numpy as np
import pandas as pd

import csv

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotifydb.models import Playlist, Song, User

from myapi.cf_reccs import *

from sklearn.metrics.pairwise import cosine_similarity

# SPOTIFY_CREDS1 = ("95ca7ded0e274316a1c21476f83e1576", "15ee20c2e8924c80b5693dd9f26daa95")
# SPOTIFY_CREDS2 = ("855879a1dbba413297f108ab660738ed", "f3bd56217f4d4b5b8c8b5898f41cd0be")
# SPOTIFY_CREDS3 = ("a123485102ba4faebcde3656cccccea5", "8ee1dc51621c4c28b81fad896eeba044")
SPOTIFY_CREDS4 = ("da2457a6e39742e8ae047ff77018bb4c", "d559c4651db14d9baff2a2c25234c69a")

# Create your views here.
print('Initializing vars')
(model, interactions, user_dict, artists_dict) = initialize_cf_data()

class Recommender(APIView):

    def get(self, request, format=None):
        
        # Used for initialization.
        # self.initialize_cf_vars()
        pass
        # auth_manager = SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID2, client_secret=SPOTIPY_CLIENT_SECRET2)
        # sp = spotipy.Spotify(auth_manager=auth_manager)
        # user = sp.user('stevienash98765')
        # print(f'user received: {user}')
        # print('Finished initializing.')

        # This code will be removed.
        # user_id = request.data.get('user_id')
        # nrec_items = 10
        # recommended_artists = get_artists_reccs_for_user(user_id, nrec_items, self.model, self.interactions, self.user_dict, self.artists_dict)
        # print(f'Recommended Artists: {recommended_artists}')

        # response = {}
        # response['status'] = 200
        # response['message'] = 'success'
        # response['results'] = 'Server initialized.'
        # return Response(response)

    def post(self, request, format=None):
        display_name = get_display_name_from_username(request.data['username'])
        song_ids = request.data.get('songs')
        num_of_recommended_songs = request.data.get('num_of_recommended_songs')
        is_dynamic = request.data.get('is_dynamic')

        print(f'Display name received: {display_name}')
        # print(song_ids)
        # print(num_of_recommended_songs)
        # print(type(is_dynamic))
        print(f"Dynamic mode is set to: {is_dynamic}")

        auth_manager = SpotifyClientCredentials(client_id=SPOTIFY_CREDS4[0], client_secret=SPOTIFY_CREDS4[1])
        sp = spotipy.Spotify(auth_manager=auth_manager)

        ######
        # CF #
        ######
        arr_recommended_artists = []
        if (model == None):
            print('Model doesnt exist')
        if (model != None):  
            nrec_items = 15
            arr_recommended_artists = get_artists_reccs_for_user(display_name, nrec_items, model, interactions, user_dict, artists_dict)
            print(f'Recommended Artists: {arr_recommended_artists}')
        # arr_recommended_artists = [
		# 	"Selena Gomez",
		# 	"Selena Gomez & The Scene",
		# 	"Ariana Grande",
		# 	"Miley Cyrus",
		# 	"Ed Sheeran",
		# 	"Katy Perry",
		# 	"The Weeknd",
		# 	"Lady Gaga",
		# 	"Drake",
		# 	"Beyoncé",
		# 	"Taylor Swift",
		# 	"Rihanna",
		# 	"Pitbull",
		# 	"David Guetta",
		# 	"Calvin Harris",
		# 	"Maroon 5",
		# 	"Avicii",
		# 	"Jason Derulo",
		# 	"Nicki Minaj",
		# 	"Ellie Goulding",
		# 	"Bruno Mars",
		# 	"Coldplay",
		# 	"Chris Brown",
		# 	"Justin Timberlake",
		# 	"JAY Z",
		# 	"Flo Rida"
		# ]

        #######
        # CBF #
        #######

        # Get song features using Spotify API (spotipy)
        print('Starting CBF...')
        song_features = sp.audio_features(song_ids)
        
        # print('Getting sp.tracks...')
        # all_tracks = sp.tracks(song_ids)
        # print(f'Received tracks: {all_tracks}')
        # for id in song_ids:
        #     print('Getting track from input songs...')
        #     track = sp.track(id)
        #     name = track['name']
        #     artist = track['album']['artists'][0]['name']

        #     add name and artist feature to current song_features list of dictionaries
        #     song_features[i].update({"name": name})
        #     song_features[i].update({"artist": artist})

            # i = i + 1

        i = 0
        input_tracks = sp.tracks(song_ids)['tracks']
        for track in input_tracks:
            name = track['name']
            artist = track['album']['artists'][0]['name']
            song_features[i].update({"name": name})
            song_features[i].update({"artist": artist})
            i = i + 1

        # Desired features for our content based algorithm
        desired_features = ['name', 'artist', 'valence', 'acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness', 'speechiness',]
        
        # Create new list of song dictionaries with only desired features
        input_songs = [
            {k: v for k, v in d.items() if k in desired_features} for d in song_features
        ]

        all_songs = None
        if (is_dynamic):
            print('Getting CBF recommended songs dynamically...')
            all_songs = get_cbf_rec_songs_dynamic(sp, arr_recommended_artists)

            # Uncomment this (and the function) to add dynamic songs to the .csv file
            # create_data_csv(all_songs)
        else:
            print('Getting CBF recommended songs from static CSV file')
            all_songs = get_cbf_rec_songs_static(arr_recommended_artists)

        # Use CBF model to get recommended number of songs
        print('Getting recommended songs...')
        recommended_songs = get_CBF_songs(input_songs, all_songs, 50)
        # recommended_songs = recommended_songs[['name', 'artists']]
        recommended_songs = recommended_songs['id'].tolist()

        print(f'Length of rec songs: {len(recommended_songs)}')
        
        output_songs = [] # list of object
        tracks = sp.tracks(recommended_songs)['tracks']

        for track in tracks:
            name = track['name']
            artist = track['album']['artists'][0]['name']
            tmp = { "name": name, "artist": artist }
            output_songs.append(tmp)

        df = pd.DataFrame(output_songs)
        df.drop_duplicates(subset=['name', 'artist'], inplace=True)
        unique_songs = df.head(num_of_recommended_songs)

        # Print before turning to dictionary (looks cleaner in console)
        print("Recommended songs from CBF:")
        print(unique_songs)
        print(type(unique_songs))

        unique_songs = unique_songs.to_dict('records')
        
        response = {}
        response['status'] = 200
        response['message'] = 'success'
        response['results'] = {
            'songs': unique_songs,
        }

        return Response(response)
    

# def create_data_csv(all_songs):   
#     print("Attempting to create a .csv from 'all_songs'")

#     # name of the output CSV file
#     filename = "data.csv"

#     # list of keys for the dictionary (to be used as CSV header)
#     header = ['artist', 'id', 'valence', 'acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness', 'speechiness']

#     # open the CSV file in append mode and write the rows
#     with open(filename, "a", newline="") as csvfile:
#         writer = csv.DictWriter(csvfile, fieldnames = header)

#         # write each dictionary to a row in the CSV file
#         for row in all_songs:
#             writer.writerow(row)

def get_cbf_rec_songs_static(artists):

    static_cbf_data = pd.read_csv('data.csv', encoding='utf-8')

    # Create a list of the column names without artists
    column_names = list(static_cbf_data.columns)
    column_names.remove('artist')

    # These are the songs that will be returned
    songs = []

    # loop through each row of the dataframe
    for index, row in static_cbf_data.iterrows():
        # check if the value in the artist column is in the search list
        if row['artist'] in artists:
            # create a dictionary of the remaining columns
            remaining_dict = {col_name: row[col_name] for col_name in column_names}
            # append the dictionary to the result list
            songs.append(remaining_dict)

    return songs

def get_cbf_rec_songs_dynamic(sp, artists):

    # map_artist_uri_to_name = {} # This is for building .csv (static CBF)
    # artist_list = [] # This is for building .csv (static CBF)

    artist_uris = []
    print('Artist searches...')
    for artist in artists:
        print('Artist search')
        artist_search = sp.search(q=artist, type='artist')
        first_name_from_search = artist_search['artists']['items'][0]['name']
        if (first_name_from_search == artist):
            artist_uris.append(artist_search['artists']['items'][0]['uri'])

            # map_artist_uri_to_name.update({artist_search['artists']['items'][0]['uri']: first_name_from_search}) # This is for building .csv (static CBF)
            continue
        sleep(0.25)

    track_uris = []
    print('Getting albums....')
    for artist_uri in artist_uris:
        print('New artist...')
        artist_albums = sp.artist_albums(artist_uri, album_type='album')
        for album in artist_albums['items']:
            album_uri = album['uri']
            tracks = sp.album_tracks(album_uri)['items']
            for track in tracks:
                track_uri = track['uri']
                track_uris.append(track_uri)

                # artist_list.append(map_artist_uri_to_name[artist_uri]) # This is for building .csv (static CBF)
            sleep(0.1)

    song_features = []
    print('Getting audio features...')
    while track_uris:
        print('Calling for 99 tracks...')
        tmp_song_features = sp.audio_features(track_uris[0:99])

        song_features += tmp_song_features
        track_uris = track_uris[99:]

    # add a new key-value pair (artist: artist_name) to each dictionary in song_features using zip() - FOR CBF Static stuff
    # for d, artist_name in zip(song_features, artist_list):
    #     if d is not None:
    #         d['artist'] = artist_name
    
    # Below was just for debug
    # data = {
    #     "features": song_features
    # }
    # with open('dump.json', 'w') as f:
    #     json.dump(data, f)

    # Desired features for our content based algorithm
    # desired_features = ['artist', 'id', 'valence', 'acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness', 'speechiness',] # Static CBF stuff
    desired_features = ['id', 'valence', 'acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness', 'speechiness',]
    
    # Create new list of song dictionaries with only desired features
    songs = [
        {k: v for k, v in d.items() if k in desired_features} for d in song_features if d is not None
    ]

    # songs = [
    #     (new_dict := {k: v for k, v in d.items() if k in desired_features}, 
    #     print(f"Iteration {i+1}: {len(new_dict)} desired features added to new song dictionary."))
    #     [0] # discard the print statement and keep only the new_dict
    #     for i, d in enumerate(song_features)
    # ]

    return songs

def get_CBF_songs(songs, all_songs, num_of_recommended_songs=50):

    # Convert songs (list of dictionaries) to a pandas dataframe
    input_songs = pd.DataFrame(songs)

    # Get the dataset from which we recommend songs from
    data_original = pd.DataFrame(all_songs)

    # Drop duplicate songs
    # data_original = data_original.drop_duplicates(subset=['name'])
    data_original = data_original.drop_duplicates(subset=['valence', 'danceability', 'energy', 'instrumentalness', 'liveness', 'speechiness'])

    # Standardize some relevent columns from the data -> Converts to Numpy Array first
    num_col_names = ['valence', 'acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness', 'speechiness']
    data_numOnly = data_original[num_col_names]

    np_data = np.array(data_numOnly)

    data_mean = np_data.mean(axis=0)
    data_std = np_data.std(axis=0)

    standardized_data = (np_data - data_mean)/(data_std)

    # Copy the standardized data back into a dataframe
    data = data_original.copy()
    data[num_col_names] = standardized_data

    # selected_features = ['valence', 'acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness', 'speechiness', 'name', 'artists']
    selected_features = ['valence', 'acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness', 'speechiness', 'id']
    data = data[selected_features]

    # n is the number of songs our function will initially recommend (Ex. User wants 11 songs and provides 5 input songs -> So model will return 15 songs)
    n = int(num_of_recommended_songs / len(songs)) + 1
    n = n*2

    # Get recommended songs (Only return the number of songs user wanted recommended back)
    recommended_songs = playlist_vector(input_songs, data, n)
    recommended_songs = recommended_songs.head(num_of_recommended_songs) 

    return recommended_songs

def playlist_vector(inputSongs, ModelPlaylist, n):
    # inputSongs: songs which you want recommendations for
    # ModePlaylist: all songs we are comparing against
    # n: how many top songs from each recommendation you want
    # Returns: list of recommendations

    temp = None
    flag = False
    for i in range(0,inputSongs.shape[0]):
        recommendations = get_cosine_recommendations(inputSongs.iloc[[i]], ModelPlaylist)
        for j in range(0,n):
            if flag == False:
                flag = True
                temp = recommendations.iloc[[j]]
            else:
                # temp.loc[len(temp)] = recommendations.iloc[j]
                temp = temp.append(recommendations.iloc[j], ignore_index=True)

    temp = temp.sort_values('sim',ascending = False)
    # temp = temp.drop_duplicates(subset=['name'])

    return temp

def get_cosine_recommendations(inputSong, ModelPlaylist):
    # Not changing the raw data. Just using most of the given numerical columns (look at the original "data" variable)

    recommended_sim = ModelPlaylist.copy()
    nparray_sim = cosine_similarity(inputSong.drop(['name', 'artist'], axis = 1).values, ModelPlaylist.drop(['id'], axis = 1).values)

    # Ordering the recommended songs from most to least
    recommended_sim['sim'] = nparray_sim.tolist()[0]
    recommended_sim_songs = recommended_sim.sort_values('sim',ascending = False)

    return recommended_sim_songs