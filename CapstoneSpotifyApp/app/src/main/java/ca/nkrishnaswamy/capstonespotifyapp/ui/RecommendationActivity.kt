package ca.nkrishnaswamy.capstonespotifyapp.ui

import android.content.Intent
import android.os.Bundle
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import ca.nkrishnaswamy.capstonespotifyapp.R
import ca.nkrishnaswamy.capstonespotifyapp.models.SongModel
import com.google.android.material.button.MaterialButton

class RecommendationActivity : AppCompatActivity() {
    private lateinit var recommendedSongName : TextView
    private lateinit var recommendedArtistName : TextView
    private lateinit var backButton : MaterialButton
    private val overallSongsList = ArrayList<SongModel>()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_recommendation)

        recommendedSongName = findViewById(R.id.recommended_song_name)
        recommendedArtistName = findViewById(R.id.recommended_artist_name)
        backButton = findViewById(R.id.backButton)

        val bundle: Bundle? = intent.extras

        bundle?.let {
            bundle.apply {
                val recommendationsList: List<SongModel>? = getParcelable("recommendationsList")
                if (recommendationsList != null) {
                    recommendedSongName.text = recommendationsList[0].name
                    recommendedArtistName.text = recommendationsList[0].artist
                }
                val overallListOfSongs : List<SongModel>? = getParcelable("overallRetrievedSongs")
                if (overallListOfSongs != null) {
                    overallSongsList.addAll(overallListOfSongs)
                }
            }
        }

        backButton.setOnClickListener {
            val intent = Intent(this@RecommendationActivity, UserSongsActivity::class.java)
            intent.putExtra("songsList", overallSongsList)
            startActivity(intent)
        }

    }
}