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

# export SPOTIPY_CLIENT_ID='95ca7ded0e274316a1c21476f83e1576'
# export SPOTIPY_CLIENT_SECRET='c0589ef660dd4e23a1cf1bcaef18c5b3'
# export SPOTIPY_REDIRECT_URI='your-app-redirect-url'

# Create your views here.


class Recommender(APIView):

    def __init__(self):
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
        song_db_entries = []
        current_song = {}

        # songs (not in db) -> spotify api (optional to store in db for subsequent calls) -> extract features that you want -> get recommendation from model -> is song made by someone in recommended artists

        df = pd.DataFrame(list(Song.objects.all().values()))

        songs = []
        for song_id in song_ids:
            curr_song = df.loc[df['id'] == song_id]
            songs.append(curr_song)
            print(curr_song)

        get_reccomendations(songs)

        response = {}
        response['status'] = 200
        response['message'] = 'success'
        response['results'] = 'thesearegonnabesongsfromCBFdataset'
        return Response(response)

def get_recommendations():
    pass