package ca.nkrishnaswamy.capstonespotifyapp.models

import android.os.Parcelable
import kotlinx.parcelize.Parcelize

@Parcelize
data class SongModel(
    var name: String,
    var artist: String,
    var song_id: String
//    var isSelected: Boolean = false
): Parcelable