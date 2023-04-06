package ca.nkrishnaswamy.capstonespotifyapp.models

import com.google.gson.annotations.SerializedName

data class JSONUserSongsResponseModel(
    @SerializedName("status")
    var status: Int,
    @SerializedName("message")
    var message: String,
    @SerializedName("results")
    var results: JSONUserResultsResponseModel
)