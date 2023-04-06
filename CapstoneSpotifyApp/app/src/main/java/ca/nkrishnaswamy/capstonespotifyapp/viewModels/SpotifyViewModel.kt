package ca.nkrishnaswamy.capstonespotifyapp.viewModels

import android.app.Application
import android.util.Log
import androidx.lifecycle.AndroidViewModel
import ca.nkrishnaswamy.capstonespotifyapp.models.SongModel
import ca.nkrishnaswamy.capstonespotifyapp.repositories.SpotifyUserRepository

class SpotifyViewModel(application: Application): AndroidViewModel(application) {

    private val repository = SpotifyUserRepository()

    suspend fun getUserSongs(username: String): ArrayList<SongModel> {
        return repository.getUserSongs(username)
    }

    suspend fun getRecommendations(songIds: List<String>): ArrayList<SongModel> {
        return repository.getRecommendations(songIds)
    }

}