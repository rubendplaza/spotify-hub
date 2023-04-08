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
    private lateinit var countTextView : TextView
    private lateinit var spotifyViewModel : SpotifyViewModel
    private lateinit var recyclerViewAdapter: SongsRecyclerViewAdapter
    private var tracker: SelectionTracker<Long>? = null
    private val songsList = ArrayList<SongModel>()
    private var listOfRecommendedSongModels = ArrayList<SongModel>()
    private lateinit var username: String

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_display_songs)

        val recyclerView: RecyclerView = findViewById(R.id.songsRecyclerView)

        spotifyViewModel = ViewModelProvider(this).get(SpotifyViewModel::class.java)

        usernameTextView = findViewById(R.id.username)
        errorTextView = findViewById(R.id.errorMessage)
        getRecommendationsButton = findViewById(R.id.getRecommendationsButton)
        getRecommendationsButton.visibility = View.INVISIBLE
        countTextView = findViewById(R.id.recommendationsCountEditText)
        countTextView.visibility = View.INVISIBLE

        val bundle: Bundle? = intent.extras

        bundle?.let {
            bundle.apply {
                username = getString("username")!!
                usernameTextView.text = username

                val retrievedSongsList = getParcelableArrayList<SongModel>("songsList")
                if (retrievedSongsList != null) {
                    songsList.addAll(retrievedSongsList)
                }
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
                        countTextView.visibility = View.VISIBLE
                        if (tracker?.selection != null) {
                            val selectedList = tracker!!.selection.map {
                                recyclerViewAdapter.getSongsList()[it.toInt()]
                            }.toList()

                            getRecommendationsButton.setOnClickListener {
                                val numOfRecommendedSongs = countTextView.text.toString().toIntOrNull()
                                if (numOfRecommendedSongs == null || numOfRecommendedSongs <= 0) {
                                    errorTextView.setTextColor(resources.getColor(R.color.red))
                                    errorTextView.text = "Recommendations count must be a non-empty positive number."
                                } else {
                                    CoroutineScope(Dispatchers.IO).launch{
                                        // listOfRecommendedSongModels = spotifyViewModel.getRecommendations(selectedList.map { it.song_id }, numOfRecommendedSongs, username) // UNCOMMENT THIS LATER
                                        listOfRecommendedSongModels.add(SongModel("Bye", "MAdele", "5"))
                                        listOfRecommendedSongModels.add(SongModel("Won't", "Wryson Tiller", "6"))
                                        listOfRecommendedSongModels.add(SongModel("Wov", "Wariana Grande", "7"))
                                        listOfRecommendedSongModels.add(SongModel("Wadaption", "The Weekday", "8"))

                                        withContext(Dispatchers.Main) {
                                            errorTextView.text = "Loading..."
                                            if (listOfRecommendedSongModels.isNullOrEmpty()) {
                                                errorTextView.setTextColor(resources.getColor(R.color.red))
                                                errorTextView.text = "No recommendations"
                                                listOfRecommendedSongModels.add(SongModel("test", "testing", "2"))
                                            } else {
                                                errorTextView.text = null
                                                val intent = Intent(this@UserSongsActivity, RecommendationActivity::class.java)
                                                intent.putExtra("recommendationsSongsList", listOfRecommendedSongModels)
                                                intent.putExtra("overallRetrievedSongs", songsList)
                                                intent.putExtra("username", username)
                                                startActivity(intent)
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    } else {
                        errorTextView.text = null
                        getRecommendationsButton.visibility = View.INVISIBLE
                        countTextView.visibility = View.INVISIBLE
                    }
                }
            })

        recyclerViewAdapter.tracker = tracker
    }
}