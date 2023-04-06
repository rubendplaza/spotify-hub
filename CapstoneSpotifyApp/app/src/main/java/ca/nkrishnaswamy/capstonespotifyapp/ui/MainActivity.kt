package ca.nkrishnaswamy.capstonespotifyapp.ui

import android.content.Intent
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.text.TextUtils
import android.widget.EditText
import android.widget.TextView
import androidx.lifecycle.ViewModelProvider
import ca.nkrishnaswamy.capstonespotifyapp.R
import ca.nkrishnaswamy.capstonespotifyapp.viewModels.SpotifyViewModel
import com.google.android.material.button.MaterialButton
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class MainActivity : AppCompatActivity() {
    private lateinit var enterUsernameText: EditText
    private lateinit var submitButton : MaterialButton
    private lateinit var errorMessageTextView : TextView
    private lateinit var spotifyViewModel : SpotifyViewModel
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        spotifyViewModel = ViewModelProvider(this).get(SpotifyViewModel::class.java)

        enterUsernameText = findViewById(R.id.usernameEnter)

        errorMessageTextView = findViewById(R.id.errorMessage)

        submitButton = findViewById(R.id.submitUsernameButton)
        submitButton.setOnClickListener {
            val username: String = enterUsernameText.text.toString()
            if (TextUtils.isEmpty(enterUsernameText.text)){
                errorMessageTextView.text = "Username is Empty"
            } else {
                errorMessageTextView.setTextColor(resources.getColor(R.color.spotify_green))
                errorMessageTextView.text = "Loading..."
                CoroutineScope(Dispatchers.IO).launch{
                    val listOfSongModels = spotifyViewModel.getUserSongs(username)
                    withContext(Dispatchers.Main) {
                        errorMessageTextView.setTextColor(resources.getColor(R.color.red))
                        if (listOfSongModels.isNullOrEmpty()) {
                            errorMessageTextView.text = "No songs found"
                        } else {
                            errorMessageTextView.text = null
                            val intent = Intent(this@MainActivity, UserSongsActivity::class.java)
                            intent.putExtra("username", username)
                            intent.putExtra("songsList", listOfSongModels)
                            startActivity(intent)
                        }
                    }
                }
            }
        }

    }
}