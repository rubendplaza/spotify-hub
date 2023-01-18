from django.db import models
from django.contrib.postgres.fields import ArrayField

class Song(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    valence = models.FloatField()
    year = models.IntegerField()
    accousticness = models.FloatField()
    artists = ArrayField(models.CharField(max_length=100))
    danceability = models.FloatField()
    duration_ms = models.IntegerField()
    energy = models.FloatField()
    explicit = models.IntegerField()
    instrumentalness = models.FloatField()
    key = models.IntegerField()
    liveness = models.FloatField()
    loudness = models.FloatField()
    mode = models.IntegerField()
    popularity = models.IntegerField()
    release_date = models.CharField(max_length=10)
    speechiness = models.FloatField()
    tempo = models.FloatField()

class Playlist(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    playlist_name = models.CharField(max_length=255)
    ## song_id = models.CharField(max_length=255)
    songs = models.ManyToManyField(Song)

class User(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    username = models.CharField(max_length=255)
    ## playlist_id = models.CharField(max_length=255)
    playlists = models.ManyToManyField(Playlist)

