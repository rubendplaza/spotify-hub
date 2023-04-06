package ca.nkrishnaswamy.capstonespotifyapp

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.annotation.NonNull
import androidx.recyclerview.selection.ItemDetailsLookup
import androidx.recyclerview.selection.SelectionTracker
import androidx.recyclerview.widget.RecyclerView
import ca.nkrishnaswamy.capstonespotifyapp.models.SongModel

internal class SongsRecyclerViewAdapter(private var songsList: List<SongModel>) :
    RecyclerView.Adapter<SongsRecyclerViewAdapter.MyViewHolder>() {

    var tracker: SelectionTracker<Long>? = null

    fun getSongsList(): List<SongModel> {
        return songsList
    }

    init {
        setHasStableIds(true)
    }

    internal inner class MyViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        var songNameTV: TextView = view.findViewById(R.id.songName)
        var artistNameTV: TextView = view.findViewById(R.id.artistName)

        fun bind(songName: String, artistName: String, isActivated: Boolean = false) {
            songNameTV.text = songName
            artistNameTV.text = artistName
            itemView.isActivated = isActivated
        }

        fun getItemDetails(): ItemDetailsLookup.ItemDetails<Long> =
            object : ItemDetailsLookup.ItemDetails<Long>() {
                override fun getPosition(): Int = adapterPosition
                override fun getSelectionKey(): Long = itemId
            }
    }
    @NonNull
    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): MyViewHolder {
        val itemView = LayoutInflater.from(parent.context)
            .inflate(R.layout.song_card, parent, false)
        return MyViewHolder(itemView)
    }
    override fun onBindViewHolder(holder: MyViewHolder, position: Int) {
        val song = songsList[position]
        tracker?.let {
            holder.bind(song.name, song.artist, it.isSelected(position.toLong()))
        }
    }
    override fun getItemCount(): Int {
        return songsList.size
    }
    override fun getItemId(position: Int): Long = position.toLong()
}