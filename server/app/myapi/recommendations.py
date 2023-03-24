from django.shortcuts import render

from rest_framework import viewsets

from rest_framework.views import APIView
from rest_framework.response import Response
import numpy as np
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from spotifydb.models import Playlist, Song, User

# export SPOTIPY_CLIENT_ID='95ca7ded0e274316a1c21476f83e1576'
# export SPOTIPY_CLIENT_SECRET='c0589ef660dd4e23a1cf1bcaef18c5b3'
# export SPOTIPY_REDIRECT_URI='your-app-redirect-url'

# Create your views here.


class Recommender(APIView):
    def post(self, request, format=None):
        song_ids = request.data.get('songs')
        song_db_entries = []
        current_song = {}

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