from django.shortcuts import render

from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response

import numpy as np
import pandas as pd

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from myapi.track_request_helpers import *
from spotifydb.models import Playlist, Song, User

from myapi.cf_reccs import *

from sklearn.metrics.pairwise import cosine_similarity

import base64
import requests

# SPOTIPY_CLIENT_ID='95ca7ded0e274316a1c21476f83e1576'
# SPOTIPY_CLIENT_SECRET='15ee20c2e8924c80b5693dd9f26daa95'
# export SPOTIPY_REDIRECT_URI='your-app-redirect-url'
# SPOTIPY_CLIENT_ID2='855879a1dbba413297f108ab660738ed'
# SPOTIPY_CLIENT_SECRET2='f3bd56217f4d4b5b8c8b5898f41cd0be'

# Create your views here.
# print('Initializing vars')
# (model, interactions, user_dict, artists_dict) = initialize_cf_data()

class Recommender(APIView):

    model = None
    interactions = None
    user_dict = None
    artists_dict = None

    TESTING = 0

    def __init__(self):

        # pass
        if self.TESTING == 0:
            self.TESTING = 1
            (self.model, self.interactions, self.user_dict, self.artists_dict) = initialize_cf_data()
            print('init method....')
        # self.model = None
        # self.interactions = None
        # self.user_dict = None
        # self.artists_dict = None

    def initialize_cf_vars(self):
        pass
        # print('Initializing method call...')
        # (model, interactions, user_dict, artists_dict) = initialize_cf_data()
        # self.model = model
        # self.interactions = interactions
        # self.user_dict = user_dict
        # self.artists_dict = artists_dict


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
        display_name = get_display_name_from_username(request.data.get('username'))
        song_ids = request.data.get('songs')
        num_of_recommended_songs = request.data.get('num_of_recommended_songs')
        is_dynamic = request.data.get('is_dynamic')

        print(f'Display name received: {display_name}')
        print(song_ids)
        print(num_of_recommended_songs)
        print(type(is_dynamic))
        print(is_dynamic)

        auth_manager = SpotifyClientCredentials(client_id=SPOTIFY_CREDS_LIST[CREDS_INDEX][0], client_secret=SPOTIFY_CREDS_LIST[CREDS_INDEX][1])
        sp = spotipy.Spotify(auth_manager=auth_manager)

        spotify_auth_token = create_auth_token(client_id=SPOTIFY_CREDS_LIST[CREDS_INDEX][0], client_secret=SPOTIFY_CREDS_LIST[CREDS_INDEX][1])

        ######
        # CF #
        ######
        arr_recommended_artists = []
        if (self.model == None):
            print('Model doesnt exist')
        if (self.model != None):  
            nrec_items = 15
            arr_recommended_artists = get_artists_reccs_for_user(display_name, nrec_items, self.model, self.interactions, self.user_dict, self.artists_dict)
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
        i = 0
        # print('Getting sp.tracks...')
        # # all_tracks = sp.tracks(song_ids)
        # track = get_track(spotify_auth_token, song_ids) # replace with make_request_for_track
        # print(f'Received tracks: {all_tracks}')
        # for id in song_ids:
        #     print('Getting track from input songs...')
        # #     track = sp.track(id)
        #     track = get_track(spotify_auth_token, id) # replace with make_request_for_track
        #     name = track['name']
        #     artist = track['album']['artists'][0]['name']

        #     add name and artist feature to current song_features list of dictionaries
        #     song_features[i].update({"name": name})
        #     song_features[i].update({"artist": artist})

            # i = i + 1

        # input_tracks_OG = sp.tracks(song_ids)['tracks']
        input_tracks = make_request_for_tracks(spotify_auth_token, song_ids)['tracks']

        print(f"Size of input tracks received: {len(input_tracks)}")

        # print(f"These are True?: {type(input_tracks_OG) == type(input_tracks)}")

        # print(f"OG: {input_tracks_OG}")
        # print(f"\nNew Input Tracks: {input_tracks}")
        # print(f"Type Input Tracks: {type(input_tracks)}")

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
            print('Getting dynamic...')
            all_songs = get_cbf_rec_songs_dynamic(sp, arr_recommended_artists)

        # Use CBF model to get recommended number of songs
        print('Getting recommended songs...')
        recommended_songs = get_CBF_songs(input_songs, 50, all_songs)
        # recommended_songs = recommended_songs[['name', 'artists']]
        recommended_songs = recommended_songs['id'].tolist()

        print(f'Length of rec songs: {len(recommended_songs)}')
        output_songs = [] # list of object
        # tracks = sp.tracks(recommended_songs)['tracks']
        tracks = make_request_for_tracks(spotify_auth_token, recommended_songs)['tracks']

        for track in tracks:
            name = track['name']
            artist = track['album']['artists'][0]['name']
            tmp = { "name": name, "artist": artist }
            output_songs.append(tmp)

        #     artist = track['album']['artists'][0]['name']
        # for id in recommended_songs:
        #     print('Getting track...')
        # #     track = sp.track(id)
        #     track = get_track(spotify_auth_token, id) # replace with make_request_for_track
        #     name = track['name']
        #     artist = track['album']['artists'][0]['name']
        #     tmp = { "name": name, "artist": artist }
        #     output_songs.append(tmp)
            # print(f'Name: {name} Artist: {artist}')

            # add name and artist feature to current song_features list of dictionaries
            # song_features[i].update({"name": name})
            # song_features[i].update({"artist": artist})

            # i = i + 1

        df = pd.DataFrame(output_songs)
        df.drop_duplicates(subset=['name', 'artist'], inplace=True)
        unique_songs = df.head(num_of_recommended_songs).to_dict('records')

        print("Recommended songs from CBF:")
        print(recommended_songs)
        print(type(recommended_songs))

        # songs (not in db) -> spotify api (optional to store in db for subsequent calls) -> extract features that you want -> get recommendation from model -> is song made by someone in recommended artists

        # dict_recommended_songs = recommended_songs.to_dict()

        response = {}
        response['status'] = 200
        response['message'] = 'success'
        response['results'] = {
            'songs': unique_songs,
        }

        return Response(response)   

def get_cbf_rec_songs_dynamic(sp, artists):

    artist_uris = []
    print('Artist searches...')
    for artist in artists:
        artist_search = sp.search(q=artist, type='artist')
        first_name_from_search = artist_search['artists']['items'][0]['name']
        if (first_name_from_search == artist):
            artist_uris.append(artist_search['artists']['items'][0]['uri'])
            continue

    print('Getting albums....')
    track_uris = []
    for artist_uri in artist_uris:
        artist_albums = sp.artist_albums(artist_uri, album_type='album')
        for album in artist_albums['items']:
            album_uri = album['uri']
            tracks = sp.album_tracks(album_uri)['items']
            for track in tracks:
                track_uri = track['uri']
                track_uris.append(track_uri)

    print('Getting audio features...')
    song_features = []
    while track_uris:
        print('Calling for 99 tracks...')
        tmp_song_features = sp.audio_features(track_uris[0:99])
        song_features += tmp_song_features
        track_uris = track_uris[99:]

    # Desired features for our content based algorithm
    desired_features = ['id', 'valence', 'acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness', 'speechiness',]
    # Create new list of song dictionaries with only desired features
    songs = [
        {k: v for k, v in d.items() if k in desired_features} for d in song_features
    ]

    return songs

def get_CBF_songs(songs, num_of_recommended_songs=50, all_songs=None):

    # 

    # Convert songs (list of dictionaries) to a pandas dataframe
    input_songs = pd.DataFrame(songs)

    # Get the dataset from which we recommend songs from
    if all_songs is None: 
        data_original = pd.read_csv('data.csv')
    else:
        data_original = pd.DataFrame(all_songs)
        # print(data_original)

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
                temp.loc[len(temp)] = recommendations.iloc[j]
                # temp = temp.append(recommendations.iloc[j], ignore_index=True)

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
