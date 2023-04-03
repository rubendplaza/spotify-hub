from django.shortcuts import render

from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response

import numpy as np
import pandas as pd

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotifydb.models import Playlist, Song, User

from myapi.cf_reccs import *

from sklearn.metrics.pairwise import cosine_similarity

# export SPOTIPY_CLIENT_ID='95ca7ded0e274316a1c21476f83e1576'
# export SPOTIPY_CLIENT_SECRET='c0589ef660dd4e23a1cf1bcaef18c5b3'
# export SPOTIPY_REDIRECT_URI='your-app-redirect-url'

# Create your views here.


class Recommender(APIView):

    def __init__(self):
        
        # This thing breaks for us (don't have csv file)
       (model, interactions, user_dict, artists_dict) = initialize_cf_data()
       self.model = model
       self.interactions = interactions
       self.user_dict = user_dict
       self.artists_dict = artists_dict


    def get(self, request, format=None):

        # Used for initialization.
        # getMySongs -> send back to user and send back user id


        # This code will be removed.
        user_id = request.data.get('user_id')
        nrec_items = 10
        recommended_artists = get_artists_reccs_for_user(user_id, nrec_items, self.model, self.interactions, self.user_dict, self.artists_dict)
        print(f'Recommended Artists: {recommended_artists}')

        response = {}
        response['status'] = 200
        response['message'] = 'success'
        response['results'] = recommended_artists
        return Response(response)

    def post(self, request, format=None):
        # {
        #     "songs": ["DSJKFNEJKF", "dashjkdaan"]
        # }
        song_ids = request.data.get('songs')
        num_of_recommended_songs = request.data.get('num_of_recommended_songs')

        print(song_ids)
        print(num_of_recommended_songs)

        auth_manager = SpotifyClientCredentials(client_id="95ca7ded0e274316a1c21476f83e1576", client_secret="c0589ef660dd4e23a1cf1bcaef18c5b3")
        sp = spotipy.Spotify(auth_manager=auth_manager)

        # Get song features using Spotify API (spotipy)
        song_features = sp.audio_features(song_ids)
        
        i = 0
        for id in song_ids:
            track = sp.track(id)

            name = track['name']
            artist = track['album']['artists'][0]['name']

            # add name and artist feature to current song_features list of dictionaries
            song_features[i].update({"name": name})
            song_features[i].update({"artist": artist})

            i = i + 1

        # Desired features for our content based algorithm
        desired_features = ['name', 'artist', 'valence', 'acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness', 'speechiness',]
        
        # Create new list of song dictionaries with only desired features
        songs = [
            {k: v for k, v in d.items() if k in desired_features} for d in song_features
        ]

        # Use CBF model to get recommended number of songs
        recommended_songs = get_CBF_songs(songs, num_of_recommended_songs)
        recommended_songs = recommended_songs[['name', 'artists']]

        print("Recommended songs from CBF:")
        print(recommended_songs)
        print(type(recommended_songs))

        # songs (not in db) -> spotify api (optional to store in db for subsequent calls) -> extract features that you want -> get recommendation from model -> is song made by someone in recommended artists

        dict_recommended_songs = recommended_songs.to_dict()

        response = {}
        response['status'] = 200
        response['message'] = 'success'
        response['results'] = dict_recommended_songs

        return Response(response)

def get_CBF_songs(songs, num_of_recommended_songs):

    # Convert songs (list of dictionaries) to a pandas dataframe
    input_songs = pd.DataFrame(songs)

    # Get the dataset from which we recommend songs from
    data_original = pd.read_csv('data.csv')

    # Drop duplicate songs
    data_original = data_original.drop_duplicates(subset=['name'])

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

    selected_features = ['valence', 'acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness', 'speechiness', 'name', 'artists']
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
                temp = temp.append(recommendations.iloc[j], ignore_index=True)

    temp = temp.sort_values('sim',ascending = False)
    temp = temp.drop_duplicates(subset=['name'])

    return temp

def get_cosine_recommendations(inputSong, ModelPlaylist):
    # Not changing the raw data. Just using most of the given numerical columns (look at the original "data" variable)

    recommended_sim = ModelPlaylist.copy()
    nparray_sim = cosine_similarity(inputSong.drop(['name', 'artist'], axis = 1).values, ModelPlaylist.drop(['name', 'artists'], axis = 1).values)

    # Ordering the recommended songs from most to least
    recommended_sim['sim'] = nparray_sim.tolist()[0]
    recommended_sim_songs = recommended_sim.sort_values('sim',ascending = False)

    return recommended_sim_songs