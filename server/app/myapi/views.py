from django.shortcuts import render

from rest_framework import viewsets

from rest_framework.views import APIView
from rest_framework.response import Response
import numpy as np
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from spotifydb.models import Playlist, Song, User

# export SPOTIPY_CLIENT_ID='95ca7ded0e274316a1c21476f83e1576'
# export SPOTIPY_CLIENT_SECRET='c0589ef660dd4e23a1cf1bcaef18c5b3'
# export SPOTIPY_REDIRECT_URI='your-app-redirect-url'

# Create your views here.

class LoginSpotify(APIView):
    # Make external spotify api call to get user's song information
    def get(self, request, format=None):
        # Create spotipy client
        response = {}
        auth_manager = SpotifyClientCredentials(client_id="95ca7ded0e274316a1c21476f83e1576", client_secret="c0589ef660dd4e23a1cf1bcaef18c5b3")
        sp = spotipy.Spotify(auth_manager=auth_manager)

        # Get user playlist ids
        playlist_ids = get_user_playlists_ids(sp, 'rubendplaza')

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

    def post(self, request, format=None):
        response = {}
        auth_manager = SpotifyClientCredentials(client_id="95ca7ded0e274316a1c21476f83e1576", client_secret="c0589ef660dd4e23a1cf1bcaef18c5b3")
        sp = spotipy.Spotify(auth_manager=auth_manager)

        user_object = {}
        user_object['username'] = request.data.get('username')

        # TODO: Known bug, only returning 100 songs or so. look at ['next']

        # Getting playlist ids
        user_playlists_info = get_user_playlists_info(sp, request.data.get("username"))
        user_object['playlists'] = user_playlists_info

        # Getting track ids
        all_playlist_songs_with_features_grouped = []
        for playlist_info in user_object['playlists']:
            current_playlist_song_ids = get_song_ids_in_playlist(sp, playlist_info['uri'])
            current_playlist_song_ids_grouped = [current_playlist_song_ids[i:i+100] for i in range(0, len(current_playlist_song_ids), 100)] # Split track ids in groups of 100 to make less api calls
            for song_id_group in current_playlist_song_ids_grouped:
                songs_with_features_group = get_song_features_by_group(sp, song_id_group)
                all_playlist_songs_with_features_grouped.append(songs_with_features_group)
            all_playlist_songs_with_features = flatten_2D_array(all_playlist_songs_with_features_grouped)
            playlist_info['tracks_with_features'] = all_playlist_songs_with_features
        
        userModel = User()
        # TODO: grab the id
        userModel.username = user_object['username']
        userModel.save()
        for playlist in user_object['playlists']:
            playlistModel = Playlist()
            # TODO: grab the id
            playlistModel.id = playlist['uri']
            playlistModel.playlist_name = playlist['name']
            playlistModel.save()

            for track in playlist['tracks_with_features']:
                # TODO: get the rest of the fields
                songModel = Song()
                songModel.id = track['id']
                songModel.valence = track['valence']
                songModel.accousticness = track['acousticness']
                songModel.danceability = track['danceability']
                songModel.duration_ms = track['duration_ms']
                songModel.energy = track['energy']
                songModel.instrumentalness = track['instrumentalness']
                songModel.key = track['key']
                songModel.liveness = track['liveness']
                songModel.loudness = track['loudness']
                songModel.speechiness = track['speechiness']
                songModel.tempo = track['tempo']
                songModel.save()
                playlistModel.songs.add(songModel)
            userModel.playlists.add(playlistModel)

        if user_object:
            response['status'] = 200
            response['message'] = 'success'
            response['results'] = user_object
        else:
            response['status'] = 403
            response['message'] = 'error'
            response['results'] = {}
        return Response(response)

def get_user_playlists_info(sp, username):
    tmp = []
    playlists = sp.user_playlists(username)
    while playlists:
        for i, playlist in enumerate(playlists['items']):
            playlist_obj = {}
            playlist_obj['name'] = playlist['name']
            playlist_obj['uri'] = playlist['uri']
            tmp.append(playlist_obj)
        if playlists['next']:
            playlists = sp.next(playlists)
        else:
            playlists = None
    return tmp

def get_user_playlists_ids(sp, username):
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

def get_song_ids_in_playlist(sp, playlist_id):
    playlist_tracks = []
    playlist_tracks_raw = sp.playlist_tracks(playlist_id=playlist_id, fields='items(track(id))')
    for track in playlist_tracks_raw['items']:
        playlist_tracks.append(track["track"]["id"])
    return playlist_tracks

def get_song_features_by_group(sp, track_id_group):
    return sp.audio_features(track_id_group);

def get_song_features(sp, track_id):
    pass;

# TODO: To fix later, use track id instead of playlist id to get the same information
def get_song_information(sp, track_id):
    playlist_tracks = sp.playlist_tracks(playlist_id=playlist_id, fields='items(track(album(id,name,album_type),id,name,popularity,artists(id,name)))')
    return playlist_tracks['items']

def get_song(sp, song_id):
    pass

def flatten_2D_array(arr):
    tmp = []
    for inside_arr in arr:
        for element in inside_arr:
            tmp.append(element)
    return tmp

def print_2D_array(arr2D):
    print("Printing array:")
    for arr in arr2D:
        print(arr)
        print("\n\n")
