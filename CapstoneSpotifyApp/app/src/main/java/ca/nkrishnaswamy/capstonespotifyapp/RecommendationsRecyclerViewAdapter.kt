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

internal class RecommendationsRecyclerViewAdapter(private var itemsList: List<SongModel>) :
    RecyclerView.Adapter<RecommendationsRecyclerViewAdapter.MyViewHolder>() {
    internal inner class MyViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        var nameView: TextView = view.findViewById(R.id.songName)
        var artistView: TextView = view.findViewById(R.id.artistName)
    }
    @NonNull
    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): MyViewHolder {
        val itemView = LayoutInflater.from(parent.context)
            .inflate(R.layout.recommendation_card, parent, false)
        return MyViewHolder(itemView)
    }
    override fun onBindViewHolder(holder: MyViewHolder, position: Int) {
        val item = itemsList[position]
        holder.nameView.text = item.name
        holder.artistView.text = item.artist
    }
    override fun getItemCount(): Int {
        return itemsList.size
    }
}