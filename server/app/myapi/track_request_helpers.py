import base64
import requests

SPOTIFY_CREDS_LIST = [
    ("95ca7ded0e274316a1c21476f83e1576", "15ee20c2e8924c80b5693dd9f26daa95"), # ruben's account
    ("855879a1dbba413297f108ab660738ed", "f3bd56217f4d4b5b8c8b5898f41cd0be"), # steve nash
    ("a123485102ba4faebcde3656cccccea5", "8ee1dc51621c4c28b81fad896eeba044"), # billywalton   
]

CREDS_INDEX = 0

def create_auth_token(client_id, client_secret):

    auth_url = 'https://accounts.spotify.com/api/token'
    auth_header = base64.b64encode((client_id + ':' + client_secret).encode('ascii')).decode('ascii')
    auth_data = {'grant_type': 'client_credentials'}
    auth_response = requests.post(auth_url, headers={'Authorization': 'Basic ' + auth_header}, data=auth_data)
    
    auth_response = auth_response.json()

    token = None

    print(f"Auth response: {auth_response}")

    if "access_token" in auth_response:
        token = auth_response['access_token']
        print(token)
    else:
        print('Authentication failed')
    
    return token

def make_request_for_track(spotify_auth_token, track_ID):

    track = get_track(spotify_auth_token, track_ID)

    while track == None:
        # Rate limited
        global CREDS_INDEX
        if CREDS_INDEX == len(SPOTIFY_CREDS_LIST):
            CREDS_INDEX = 0
        else:
            CREDS_INDEX+=1

        new_spotify_auth_token = create_auth_token(client_id=SPOTIFY_CREDS_LIST[CREDS_INDEX][0], client_secret=SPOTIFY_CREDS_LIST[CREDS_INDEX][1])

        track = get_track(new_spotify_auth_token, track_ID)

    return track

def get_track(spotify_auth_token, track_ID):
    track_url = f'https://api.spotify.com/v1/tracks/{track_ID}'
    track_response = requests.get(track_url, headers={'Authorization': 'Bearer ' + spotify_auth_token})

    try:
        json_response = track_response.json()

        if "id" not in json_response:
            print('Track Call Failed')

        return json_response
    
    except Exception as e:
        print("Rate limited...")
        return None

def make_request_for_tracks(spotify_auth_token, track_IDs_list):

    tracks_list = get_tracks(spotify_auth_token, track_IDs_list)

    while tracks_list == None:
        # Rate limited
        global CREDS_INDEX
        if CREDS_INDEX == len(SPOTIFY_CREDS_LIST):
            CREDS_INDEX = 0
        else:
            CREDS_INDEX+=1

        new_spotify_auth_token = create_auth_token(client_id=SPOTIFY_CREDS_LIST[CREDS_INDEX][0], client_secret=SPOTIFY_CREDS_LIST[CREDS_INDEX][1])

        tracks_list = get_tracks(new_spotify_auth_token, track_IDs_list)

    return tracks_list
        

def get_tracks(spotify_auth_token, track_IDs_list):
    tracks_url = f"https://api.spotify.com/v1/tracks?ids={','.join(track_IDs_list)}"
    print(f"URL for tracks: {tracks_url}")
    tracks_response = requests.get(tracks_url, headers={'Authorization': 'Bearer ' + spotify_auth_token})
    print(f"Track Response: {tracks_response}")

    try:
        json_response = tracks_response.json()

        if "tracks" not in json_response:
            print("Tracks Call Failed")

        return json_response

    except Exception as e:
        print("Rate limited...")
        return None