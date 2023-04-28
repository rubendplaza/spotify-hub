package ca.nkrishnaswamy.capstonespotifyapp.ui

import android.content.Intent
import android.os.Bundle
import android.util.Log
import android.view.View
import android.widget.TextView
import android.widget.Toast
import android.widget.ToggleButton
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
import kotlinx.coroutines.selects.select
import kotlinx.coroutines.withContext

class UserSongsActivity : AppCompatActivity() {
    private lateinit var usernameTextView : TextView
    private lateinit var errorTextView : TextView
    private lateinit var getRecommendationsButton : MaterialButton
    private lateinit var countTextView : TextView
    private lateinit var recommendationTypeToggle : ToggleButton
    private lateinit var spotifyViewModel : SpotifyViewModel
    private lateinit var recyclerViewAdapter: SongsRecyclerViewAdapter
    private var tracker: SelectionTracker<Long>? = null
    private val songsList = ArrayList<SongModel>()
    private var listOfRecommendedSongModels = ArrayList<SongModel>()
    private lateinit var userId: String
    private lateinit var username: String
    private var isDynamic: Boolean = true

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
        recommendationTypeToggle = findViewById(R.id.recommendationTypeToggle)

        recommendationTypeToggle.setOnCheckedChangeListener { _, isChecked ->
            isDynamic = isChecked
            Toast.makeText(this, if(isChecked) "Dynamic Recommendation Mode ON" else "Dynamic Recommendation OFF", Toast.LENGTH_SHORT).show()
        }

        val bundle: Bundle? = intent.extras

        bundle?.let {
            bundle.apply {
                userId = getString("userId")!!
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
                                    errorTextView.text = "Loading..."
                                    CoroutineScope(Dispatchers.IO).launch{
                                        listOfRecommendedSongModels = spotifyViewModel.getRecommendations(selectedList.map { it.song_id }, numOfRecommendedSongs, userId, isDynamic)
                                        Log.d("TESTT", userId)
//                                        listOfRecommendedSongModels.add(SongModel("Ready or Not (with Busta Rhymes)", "Calvin Harris", "6"))
//                                        listOfRecommendedSongModels.add(SongModel("Countdown", "Beyoncé", "7"))
//                                        listOfRecommendedSongModels.add(SongModel("Glasgow", "David Guetta", "8"))
//                                        listOfRecommendedSongModels.add(SongModel("Closure", "Taylor Swift", "9"))

                                        withContext(Dispatchers.Main) {
                                            if (listOfRecommendedSongModels.isNullOrEmpty()) {
                                                errorTextView.setTextColor(resources.getColor(R.color.red))
                                                errorTextView.text = "No recommendations"
                                                listOfRecommendedSongModels.add(SongModel("test", "testing", "2"))
                                            } else {
                                                val intent = Intent(this@UserSongsActivity, RecommendationActivity::class.java)
                                                intent.putExtra("recommendationsSongsList", listOfRecommendedSongModels)
                                                intent.putExtra("overallRetrievedSongs", songsList)
                                                intent.putExtra("userId", userId)
                                                intent.putExtra("username", username)
                                                startActivity(intent)
                                                errorTextView.text = null
                                            }
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