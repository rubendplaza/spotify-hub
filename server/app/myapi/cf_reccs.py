# from collections import defaultdict
# from sklearn.metrics.pairwise import cosine_similarity
# from lightfm.evaluation import precision_at_k, auc_score
# from lightfm import LightFM, cross_validation
import lightfm
# from scipy import sparse
import random
import itertools
from time import *

import pickle
import os

# import numpy as np
import pandas as pd
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from myapi.cf_helpers import *

# SPOTIFY_CREDS1 = ("95ca7ded0e274316a1c21476f83e1576", "15ee20c2e8924c80b5693dd9f26daa95")
# SPOTIFY_CREDS2 = ("855879a1dbba413297f108ab660738ed", "f3bd56217f4d4b5b8c8b5898f41cd0be")
# SPOTIFY_CREDS3 = ("a123485102ba4faebcde3656cccccea5", "8ee1dc51621c4c28b81fad896eeba044")
# SPOTIPY_CLIENT_ID='855879a1dbba413297f108ab660738ed'
# SPOTIPY_CLIENT_SECRET='f3bd56217f4d4b5b8c8b5898f41cd0be'


def get_artists_reccs_for_user(user_id, nrec_items, model, interactions, user_dict, artists_dict):

    recommended_artists = sample_recommendation_user(model=model, interactions=interactions, user_id=user_id, user_dict=user_dict, item_dict=artists_dict, threshold=0, nrec_items=nrec_items)
    return recommended_artists


def initialize_cf_data():
    users_to_add = ['stevienash98765', '31wexqymjgzdkkved4vcwote7r2q', '31jcprt274yhbqbldnen6q4r2rxq']
    # CHANGE THE MODULO VALUE TO WHATEVER V WAS USED WHEN GETTING THE PICKLE FILE FROM JUPYTER NOTEBOOK
    print('Reading cf csv...')
    df_playlist = pd.read_csv('spotifydataset.csv', error_bad_lines=False, warn_bad_lines=False, skiprows=lambda i: i>0 and (i % 1 != 0))
    print(f'Number of rows: {df_playlist.shape[0]}')
    df_playlist.columns = df_playlist.columns.str.replace('"', '')
    df_playlist.columns = df_playlist.columns.str.replace('name', '')
    df_playlist.columns = df_playlist.columns.str.replace(' ', '')
    # df_playlist.head()
    df_playlist = add_users_to_dataset(df_playlist, users_to_add)

    # Keeping artists that appear with a minimum frequency. (50)
    df_playlist = df_playlist.groupby('artist').filter(lambda x : len(x) >= 50)
    # df_playlist.loc[df_playlist['user_id'] == temp_user_id]

    # Keeping users with at least 10 unique artists in their playlists to lessen the impact of the COLD START problem.
    df_playlist = df_playlist[df_playlist.groupby('user_id').artist.transform('nunique') >= 10]
    # df_playlist.loc[df_playlist['user_id'] == temp_user_id]

    # Grouping by the frequency count for each users artists (# of times that an artist appeared in playlists created by a user)
    # size = lambda x : len(x) # !IMPORTANT
    df_freq = df_playlist.groupby(['user_id', 'artist']).agg('size').reset_index().rename(columns={0:'freq'})[['user_id', 'artist', 'freq']].sort_values(['freq'], ascending=False)
    # df_freq.head()
    # df_freq.loc[df_freq['user_id'] == temp_user_id]

    # Creating a data frame for artists and artist id
    # ARTIST MAPPING
    df_artist = pd.DataFrame(df_freq['artist'].unique())
    df_artist = df_artist.reset_index()
    df_artist = df_artist.rename(columns={'index':'artist_id', 0:'artist'})
    # df_artist.head()

    # Adding artist_id to the frequency data frame
    df_freq = pd.merge(df_freq, df_artist, how='inner', on='artist')

    # Create interaction matrix
    interactions = create_interaction_matrix(df=df_freq, user_col="user_id", item_col="artist_id", rating_col='freq', norm=False, threshold=None)
    # interactions.head()

    print(f'Number of rows after processing: {interactions.shape[0]}')

    # Create user dict
    user_dict = create_user_dict(interactions=interactions)

    # Create item dict
    artists_dict = create_item_dict(df=df_artist, id_col="artist_id", name_col="artist")

    print('Importing model...')
    model = import_pickle_model()
    print('Finished importing model.')
    return (model, interactions, user_dict, artists_dict)

def add_users_to_dataset(df_playlist, users):
    print('Adding test users to dataset...')
    auth_manager = SpotifyClientCredentials(client_id=SPOTIFY_CREDS3[0], client_secret=SPOTIFY_CREDS3[1])
    sp = spotipy.Spotify(auth_manager=auth_manager)
    new_user_rows = []
    for username in users:
        user = sp.user(username)
        # print(f'Received user: {user}')
        # user_id = user['id']
        display_name = get_display_name_from_username(username)
        # playlists = sp.user_playlists(username)
        playlist_names = get_user_playlists_names(sp, username)
        # print(f'playlist names: {playlist_names}')
        playlist_ids = get_user_playlists_ids(sp, username)
        # print(f'playlist ids: {playlist_ids}')
        song_ids = []
        for playlist_id in playlist_ids:
            current_playlist_song_ids = get_song_ids_in_playlist(sp, playlist_id)
            # print(f'playlist song ids: {current_playlist_song_ids}')
            song_ids.extend(current_playlist_song_ids)
        input_tracks = get_tracks_50_a_time(sp, song_ids)

        for track in input_tracks:
            name = track["name"]
            artist = track['album']['artists'][0]['name']

            # Create a dictionary containing a song's name, artist, and song ID -> Add this dictionary to a list 
            new_row = {
                'user_id': display_name,
                'track': name,
                'artist': artist,
                'playlist': playlist_names[0]
            }
            # print('adding to new row')
            new_user_rows.append(new_row)
#     for row in new_user_rows:
#         print(row)
    # print('updating df')
    temp_df = pd.DataFrame(new_user_rows) 
    df_playlist = pd.concat([df_playlist, temp_df], ignore_index = True)
    print('Finished adding users to dataset.')
    return df_playlist

def get_tracks_50_a_time(sp, track_ids):
    tracks = []
    for i in range(0, len(track_ids), 50):
        # Get the next 50 tracks using the sp.tracks() method
        print('Getting 50 tracks....')
        track_batch = sp.tracks(track_ids[i:i+50])
        tracks += track_batch['tracks']
    return tracks

def get_user_playlists_names(sp, username):
    tmp = []
    playlists = sp.user_playlists(username)
    print('Received playlists...')
    while playlists:
        # print(f'Iterating playlist')
        for i, playlist in enumerate(playlists['items']):
            tmp.append(playlist['name'])
        if playlists['next']:
            playlists = sp.next(playlists)
        else:
            playlists = None
    return tmp

def get_user_playlists_ids(sp, username):
    tmp = []
    playlists = sp.user_playlists(username)
    print('Received playlists...')
    while playlists:
        # print(f'Iterating playlist')
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
    print('Received playlist tracks...')
    for track in playlist_tracks_raw['items']:
        playlist_tracks.append(track["track"]["id"])
    return playlist_tracks

# Display names will be used for getting recommendations
def get_display_name_from_username(username):
    if (username == '31jcprt274yhbqbldnen6q4r2rxq'):
        return 'billywalton98765'
    if (username == 'stevienash98765'):
        return 'stevienash98765'
    if (username == '31wexqymjgzdkkved4vcwote7r2q'):
        return 'plazadruben'
    
def get_username_from_display_name(displayname):
    if (displayname == 'billywalton98765'):
        return '31jcprt274yhbqbldnen6q4r2rxq'
    if (displayname == 'stevienash98765'):
        return 'stevienash98765' 
    if (displayname == 'plazadruben'):
        return '31wexqymjgzdkkved4vcwote7r2q'