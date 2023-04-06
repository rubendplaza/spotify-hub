package ca.nkrishnaswamy.capstonespotifyapp.repositories

import android.util.Log
import ca.nkrishnaswamy.capstonespotifyapp.SpotifyAPICallsService
import ca.nkrishnaswamy.capstonespotifyapp.models.SongModel
import android.widget.Toast
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.RequestBody.Companion.toRequestBody

import org.json.JSONObject
import java.lang.Exception
import java.security.AccessController.getContext


class SpotifyUserRepository() {
    private val apiCallService = SpotifyAPICallsService()

    suspend fun getUserSongs(username: String) : ArrayList<SongModel> {

        val response = apiCallService.getSongsOfUser(username)

        val resultSongsList : ArrayList<SongModel> = ArrayList()
        if (response.isSuccessful) {
            val songsList = response.body()?.results?.songs
            if (songsList != null) {
                for (i in 0 until songsList.count()) {
                    val songId = songsList[i].song_id
                    val artist = songsList[i].artist
                    val name = songsList[i].name

                    val currentSong = SongModel(name, artist, songId)
                    resultSongsList.add(currentSong)
                }
            }
        }
        return resultSongsList
    }

    suspend fun getRecommendations(songIdsList: List<String>) : ArrayList<SongModel> {

        val jsonObject = JSONObject()
        jsonObject.put("songs", songIdsList)
        jsonObject.put("num_of_recommended_songs", 1) // hard-coding this to 1

        val jsonObjectString = jsonObject.toString()
        val requestBody = jsonObjectString.toRequestBody("application/json".toMediaTypeOrNull())
        val response = apiCallService.getRecommendations(requestBody)

        val recommendationsList : ArrayList<SongModel> = ArrayList()

        if (response.isSuccessful) {
            val resultsDict = response.body()
            if (resultsDict != null) {
                Log.d("TESTTT", resultsDict.string())
            }
        }
        return recommendationsList
    }
}