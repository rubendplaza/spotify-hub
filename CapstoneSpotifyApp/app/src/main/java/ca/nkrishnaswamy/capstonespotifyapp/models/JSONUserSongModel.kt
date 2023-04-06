package ca.nkrishnaswamy.capstonespotifyapp.models

import com.google.gson.annotations.SerializedName

data class JSONUserSongModel(
    @SerializedName("name")
    var name: String,
    @SerializedName("artist")
    var artist: String,
    @SerializedName("song_id")
    var song_id: String
)