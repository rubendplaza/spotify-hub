package ca.nkrishnaswamy.capstonespotifyapp.ui

import android.content.Intent
import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import ca.nkrishnaswamy.capstonespotifyapp.R
import ca.nkrishnaswamy.capstonespotifyapp.RecommendationsRecyclerViewAdapter
import ca.nkrishnaswamy.capstonespotifyapp.models.SongModel
import com.google.android.material.button.MaterialButton

class RecommendationActivity : AppCompatActivity() {
    private lateinit var backButton : MaterialButton
    private val overallSongsList = ArrayList<SongModel>()
    private lateinit var username: String
    private val recommendationsList = ArrayList<SongModel>()
    private lateinit var recommendationsRVAdapter: RecommendationsRecyclerViewAdapter

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_recommendation)

        val recyclerView: RecyclerView = findViewById(R.id.recommendationsRecyclerView)

        backButton = findViewById(R.id.backButton)

        val bundle: Bundle? = intent.extras

        bundle?.let {
            bundle.apply {
                val retrievedListOfRecommendations = getParcelableArrayList<SongModel>("recommendationsSongsList")
                if (retrievedListOfRecommendations != null) {
                    recommendationsList.addAll(retrievedListOfRecommendations)
                }

                val overallListOfSongs = getParcelableArrayList<SongModel>("overallRetrievedSongs")
                if (overallListOfSongs != null) {
                    overallSongsList.addAll(overallListOfSongs)
                }

                username = getString("username")!!
            }
        }

        recommendationsRVAdapter = RecommendationsRecyclerViewAdapter(recommendationsList)
        val layoutManager = LinearLayoutManager(applicationContext)
        recyclerView.layoutManager = layoutManager
        recyclerView.adapter = recommendationsRVAdapter

        backButton.setOnClickListener {
            val intent = Intent(this@RecommendationActivity, UserSongsActivity::class.java)
            intent.putExtra("songsList", overallSongsList)
            intent.putExtra("username", username)
            startActivity(intent)
        }

    }
}