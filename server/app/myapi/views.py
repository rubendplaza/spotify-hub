from django.shortcuts import render

from rest_framework import viewsets
# from .serializers import HeroSerializer
# from .models import Hero

from rest_framework.views import APIView
from rest_framework.response import Response
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# export SPOTIPY_CLIENT_ID='95ca7ded0e274316a1c21476f83e1576'
# export SPOTIPY_CLIENT_SECRET='c0589ef660dd4e23a1cf1bcaef18c5b3'
# export SPOTIPY_REDIRECT_URI='your-app-redirect-url'

# Create your views here.
# class HeroViewSet(viewsets.ModelViewSet):
#     queryset = Hero.objects.all().order_by('name')
#     serializer_class = HeroSerializer

class LoginSpotify(APIView):
    # Make external spotify api call to get user's song information
    def get(self, request, format=None):
        # Create spotipy client
        response = {}
        auth_manager = SpotifyClientCredentials(client_id="95ca7ded0e274316a1c21476f83e1576", client_secret="c0589ef660dd4e23a1cf1bcaef18c5b3")
        sp = spotipy.Spotify(auth_manager=auth_manager)

        # Get user playlist ids
        playlist_ids = getUsersPlaylistIds(sp, 'rubendplaza')

        # Lists to store user information
        # OVERALL OPTIMIZATION: Create database models to store this information so we only go to spotify API when #                       we haven't already seen a track.
        playlist_tracks = []
        all_playlists_tracks = []
        all_tracks_information = []

        # Iterate over playlist ids and get every song they have in their playlists
        # OPTIMIZATION: Only retrieve track ids not all this other information
        for playlist_id in playlist_ids:
            playlist_tracks = sp.playlist_tracks(playlist_id=playlist_id, fields='items(track(album(id,name,album_type),id,name,popularity,artists(id,name)))')
            all_playlists_tracks += playlist_tracks['items']
            break

        # For every track get all information for that track
        # OPTIMIZATION: Store a specific tracks information once in database
        for track in all_playlists_tracks:
            current_track = sp.track(track_id=track['track']['id'])

            # A track does not return genre information, so we grab genre information from the artists on the track
            # OPTMIZATION: Store artist infomration in database so we only every need to retrieve it once
            #              from the spotify API
            for idx, artist in enumerate(track['track']['artists']):
                artist_id = artist['id']
                current_artist = sp.artist(artist_id=artist_id)
                genres_for_artist = current_artist['genres']
                current_track['artists'][idx]['genres'] = genres_for_artist

            # Add current tracks information to the list of all tracks
            all_tracks_information.append(current_track)
            break

        # Return all the track information to the client
        # OPTIMIZATION: This will all happen in the background once a user signs up
        if len(all_tracks_information) > 0:
            response['status'] = 200
            response['message'] = 'success'
            response['results'] = all_tracks_information
        else:
            response['status'] = 403
            response['message'] = 'error'
            response['results'] = {}
        return Response(response)

def getUsersPlaylistIds(sp, username):
    tmp = []
    playlists = sp.user_playlists(username)
    while playlists:
        for i, playlist in enumerate(playlists['items']):
            tmp.append(playlist['uri'])
        if playlists['next']:
            playlists = sp.next(playlists)
        else:
            playlists = None
    return tmp
