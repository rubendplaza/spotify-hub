package ca.nkrishnaswamy.capstonespotifyapp.ui

import android.content.Intent
import android.os.Bundle
import android.util.Log
import android.view.View
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.ViewModelProvider
import androidx.recyclerview.selection.SelectionPredicates
import androidx.recyclerview.selection.SelectionTracker
import androidx.recyclerview.selection.StableIdKeyProvider
import androidx.recyclerview.selection.StorageStrategy
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import ca.nkrishnaswamy.capstonespotifyapp.R
import ca.nkrishnaswamy.capstonespotifyapp.SongDetailsLookup
import ca.nkrishnaswamy.capstonespotifyapp.SongsRecyclerViewAdapter
import ca.nkrishnaswamy.capstonespotifyapp.models.SongModel
import ca.nkrishnaswamy.capstonespotifyapp.viewModels.SpotifyViewModel
import com.google.android.material.button.MaterialButton
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class UserSongsActivity : AppCompatActivity() {
    private lateinit var usernameTextView : TextView
    private lateinit var errorTextView : TextView
    private lateinit var getRecommendationsButton : MaterialButton
    private lateinit var spotifyViewModel : SpotifyViewModel
    private lateinit var recyclerViewAdapter: SongsRecyclerViewAdapter
    private var tracker: SelectionTracker<Long>? = null
    private val songsList = ArrayList<SongModel>()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_display_songs)

        val recyclerView: RecyclerView = findViewById(R.id.songsRecyclerView)

        spotifyViewModel = ViewModelProvider(this).get(SpotifyViewModel::class.java)

        usernameTextView = findViewById(R.id.username)
        errorTextView = findViewById(R.id.errorMessage)
        getRecommendationsButton = findViewById(R.id.getRecommendationsButton)
        getRecommendationsButton.visibility = View.INVISIBLE

        val bundle: Bundle? = intent.extras

        bundle?.let {
            bundle.apply {
                val username: String? = getString("username")
                usernameTextView.text = username

                val retrievedSongsList = getParcelableArrayList<SongModel>("songsList")
                if (retrievedSongsList != null) {
                    songsList.addAll(retrievedSongsList)
                }
                Log.d("TESTT", "${songsList.count()}")
            }
        }

        recyclerView.layoutManager = LinearLayoutManager(this)
        recyclerViewAdapter = SongsRecyclerViewAdapter(songsList)
        recyclerView.adapter = recyclerViewAdapter

        tracker = SelectionTracker.Builder<Long>(
            "mySelection",
            recyclerView,
            StableIdKeyProvider(recyclerView),
            SongDetailsLookup(recyclerView),
            StorageStrategy.createLongStorage()
        ).withSelectionPredicate(
            SelectionPredicates.createSelectAnything()
        ).build()

        tracker?.addObserver(
            object : SelectionTracker.SelectionObserver<Long>() {
                override fun onSelectionChanged() {
                    super.onSelectionChanged()
                    val nItems: Int = tracker?.selection!!.size()
                    if (nItems > 0) {
                        errorTextView.text = null
                        getRecommendationsButton.visibility = View.VISIBLE
                        if (tracker?.selection != null) {
                            val selectedList = tracker!!.selection.map {
                                recyclerViewAdapter.getSongsList()[it.toInt()]
                            }.toList()

                            getRecommendationsButton.setOnClickListener {
                                CoroutineScope(Dispatchers.IO).launch{
                                     val listOfSongModels = spotifyViewModel.getRecommendations(selectedList.map { it.song_id })
                                     withContext(Dispatchers.Main) {
                                         errorTextView.text = "Loading..."
                                        if (listOfSongModels.isNullOrEmpty()) {
                                            errorTextView.setTextColor(resources.getColor(R.color.red))
                                            errorTextView.text = "No recommendations"
                                            listOfSongModels.add(SongModel("test", "testing", "2"))
                                        } else if (listOfSongModels.count() > 1) {
                                            errorTextView.setTextColor(resources.getColor(R.color.red))
                                            errorTextView.text = "Error"
                                        } else {
                                            errorTextView.setTextColor(resources.getColor(R.color.spotify_green))
                                            errorTextView.text = null
                                            val intent = Intent(this@UserSongsActivity, RecommendationActivity::class.java)
                                            intent.putExtra("recommendationsList", listOfSongModels)
                                            intent.putExtra("overallRetrievedSongs", songsList)
                                            startActivity(intent)
                                        }
                                     }
                                 }
                            }
                        }
                    } else {
                        errorTextView.text = null
                        getRecommendationsButton.visibility = View.INVISIBLE
                    }
                }
            })

        recyclerViewAdapter.tracker = tracker
    }
}