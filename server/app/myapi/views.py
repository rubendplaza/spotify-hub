from django.shortcuts import render

from rest_framework import viewsets

from rest_framework.views import APIView
from rest_framework.response import Response
import numpy as np
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from spotifydb.models import Playlist, Song, User

from myapi.cf_reccs import *

# SPOTIFY_CREDS1 = ("95ca7ded0e274316a1c21476f83e1576", "15ee20c2e8924c80b5693dd9f26daa95")
SPOTIFY_CREDS2 = ("855879a1dbba413297f108ab660738ed", "f3bd56217f4d4b5b8c8b5898f41cd0be")
# SPOTIFY_CREDS3 = ("a123485102ba4faebcde3656cccccea5", "8ee1dc51621c4c28b81fad896eeba044")
# SPOTIFY_CREDS4 = ("da2457a6e39742e8ae047ff77018bb4c", "d559c4651db14d9baff2a2c25234c69a")

# Create your views here.

class LoginSpotify(APIView):

    # Make external spotify api call to get user's song information
    def get(self, request, format=None):
        # Create spotipy client
        response = {}
        auth_manager = SpotifyClientCredentials(client_id=SPOTIFY_CREDS2[0], client_secret=SPOTIFY_CREDS2[1])
        sp = spotipy.Spotify(auth_manager=auth_manager)

        # username = request.GET.get('username', '')
        username = get_username_from_display_name(request.GET.get('username', ''))
        print(f'Username: {username}')
        # This is the object that is returned back to the user
        user_object = {}
        user_object['user_id'] = username

        # Getting playlist ids
        user_playlists_id = get_user_playlists_ids(sp, user_object['user_id'])

        # Getting track ids for all songs in the playlists
        user_song_ids = []
        for playlist_id in user_playlists_id:
            current_playlist_song_ids = get_song_ids_in_playlist(sp, playlist_id)
            user_song_ids.extend(current_playlist_song_ids)

        # Remove any duplicate songs from users playlists
        unique_song_id_list = list(set(user_song_ids))

        # Get the track name and artist for each unique song id -> Save to a list of dictionaries
        

        user_tracks = get_tracks_50_a_time(sp, unique_song_id_list)
        songs = []
        for track in user_tracks:
            id = track['id']
            name = track['name']
            artist = track['album']['artists'][0]['name']
            song_dict = {"name": name, "artist": artist, "song_id": id}
            songs.append(song_dict)

        # for song_id in unique_song_id_list:
        #     track = sp.track(song_id)

        #     name = track['name']
        #     artist = track['album']['artists'][0]['name']

        #     # Create a dictionary containing a song's name, artist, and song ID -> Add this dictionary to a list 
        #     song_dict = {"name": name, "artist": artist, "song_id": song_id}
        #     songs.append(song_dict)

        user_object['songs'] = songs

        if len(songs) > 0:
            response['status'] = 200
            response['message'] = 'success'
            response['results'] = user_object
        else:
            response['status'] = 403
            response['message'] = 'error'
            response['results'] = {}

        return Response(response)
    

    # Not being used.
    def post(self, request, format=None):
        pass
        # response = {}
        # auth_manager = SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID2, client_secret=SPOTIPY_CLIENT_SECRET2)
        # sp = spotipy.Spotify(auth_manager=auth_manager)

        # user_object = {}
        # user_object['username'] = request.data.get('username')

        # # TODO: Known bug, only returning 100 songs or so. look at ['next']

        # # Getting playlist ids
        # user_playlists_info = get_user_playlists_info(sp, request.data.get("username"))
        # user_object['playlists'] = user_playlists_info

        # # Getting track ids
        # all_playlist_songs_with_features_grouped = []
        # for playlist_info in user_object['playlists']:
        #     current_playlist_song_ids = get_song_ids_in_playlist(sp, playlist_info['uri'])
        #     current_playlist_song_ids_grouped = [current_playlist_song_ids[i:i+100] for i in range(0, len(current_playlist_song_ids), 100)] # Split track ids in groups of 100 to make less api calls
        #     for song_id_group in current_playlist_song_ids_grouped:
        #         songs_with_features_group = get_song_features_by_group(sp, song_id_group)
        #         all_playlist_songs_with_features_grouped.append(songs_with_features_group)
        #     all_playlist_songs_with_features = flatten_2D_array(all_playlist_songs_with_features_grouped)
        #     playlist_info['tracks_with_features'] = all_playlist_songs_with_features
        
        # userModel = User()
        # # TODO: grab the id
        # userModel.username = user_object['username']
        # userModel.save()
        # for playlist in user_object['playlists']:
        #     playlistModel = Playlist()
        #     # TODO: grab the id
        #     playlistModel.id = playlist['uri']
        #     playlistModel.playlist_name = playlist['name']
        #     playlistModel.save()

        #     for track in playlist['tracks_with_features']:
        #         # TODO: get the rest of the fields
        #         songModel = Song()
        #         songModel.id = track['id']
        #         songModel.valence = track['valence']
        #         songModel.accousticness = track['acousticness']
        #         songModel.danceability = track['danceability']
        #         songModel.duration_ms = track['duration_ms']
        #         songModel.energy = track['energy']
        #         songModel.instrumentalness = track['instrumentalness']
        #         songModel.key = track['key']
        #         songModel.liveness = track['liveness']
        #         songModel.loudness = track['loudness']
        #         songModel.speechiness = track['speechiness']
        #         songModel.tempo = track['tempo']
        #         songModel.save()
        #         playlistModel.songs.add(songModel)
        #     userModel.playlists.add(playlistModel)

        # if user_object:
        #     response['status'] = 200
        #     response['message'] = 'success'
        #     response['results'] = user_object
        # else:
        #     response['status'] = 403
        #     response['message'] = 'error'
        #     response['results'] = {}
        # return Response(response)

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
