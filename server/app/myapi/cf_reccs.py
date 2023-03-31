# from collections import defaultdict
# from sklearn.metrics.pairwise import cosine_similarity
# from lightfm.evaluation import precision_at_k, auc_score
# from lightfm import LightFM, cross_validation
import lightfm
# from scipy import sparse
import random
import itertools

import pickle
import os

# import numpy as np
import pandas as pd
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

from myapi.cf_helpers import *


def get_artists_reccs_for_user(user_id, nrec_items, model, interactions, user_dict, artists_dict):

    recommended_artists = sample_recommendation_user(model=model, interactions=interactions, user_id=user_id, user_dict=user_dict, item_dict=artists_dict, threshold=0, nrec_items=nrec_items)
    return recommended_artists


def initialize_cf_data():
    # CHANGE THE MODULO VALUE TO WHATEVER V WAS USED WHEN GETTING THE PICKLE FILE FROM JUPYTER NOTEBOOK 
    df_playlist = pd.read_csv('spotifydataset.csv', error_bad_lines=False, warn_bad_lines=False, skiprows=lambda i: i>0 and (i % 50 != 0))
    print(f'Number of rows: {df_playlist.shape[0]}')
    df_playlist.columns = df_playlist.columns.str.replace('"', '')
    df_playlist.columns = df_playlist.columns.str.replace('name', '')
    df_playlist.columns = df_playlist.columns.str.replace(' ', '')
    # df_playlist.head()
    df_playlist = add_users_to_dataset(df_playlist)

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

    model = import_pickle_model()

    return (model, interactions, user_dict, artists_dict)

# TODO: Do hyper parameter tuning to get best params for model before getting pickle file.
# TODO: (Add users to dataset using spotify api. Also add them in this way in the jupyter notebook) to get pickle file.
def add_users_to_dataset(df_playlist):
    # Adding test user and seeing what the output will be.
    temp_user_id = '00000000000000000000000000000000'
    temp_user_artists = [
        'Eminem', 'Kanye West', '50 Cent', 'Drake', 'Kendrick Lamar', 'Future', 
        'Lil Baby', 'Snoop Dogg', 'Post Malone', 'Lil Wayne', 'Kid Cudi']
    temp_track_name = 'testtrackname'
    temp_playlist_name = 'testplaylist'

    new_rows = []
    for i in range(5000):
        temp_artist = random.choice(temp_user_artists)
        new_row = {
            'user_id': temp_user_id,
            'artist': temp_artist,
            'track': temp_track_name,
            'playlist': temp_playlist_name
        }
        new_rows.append(new_row)

    temp_df = pd.DataFrame(new_rows) 
    df_playlist = pd.concat([df_playlist, temp_df], ignore_index = True)
    # df_last = df_playlist.tail(10)
    # See if user was inserted properly
    # print(df_last)
    # df_playlist.loc[df_playlist['user_id'] == temp_user_id]
    return df_playlist
