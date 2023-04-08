package ca.nkrishnaswamy.capstonespotifyapp.models

import com.google.gson.annotations.SerializedName

data class JSONUserResultsResponseModel(
    @SerializedName("user_id")
    var user_id: String,
    @SerializedName("songs")
    var songs: ArrayList<JSONUserSongModel>
)