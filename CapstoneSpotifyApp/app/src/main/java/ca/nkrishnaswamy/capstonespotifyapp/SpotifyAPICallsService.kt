package ca.nkrishnaswamy.capstonespotifyapp

import ca.nkrishnaswamy.capstonespotifyapp.models.JSONUserSongsResponseModel
import retrofit2.Response
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import okhttp3.OkHttpClient
import okhttp3.RequestBody
import okhttp3.ResponseBody
import retrofit2.http.*
import java.util.concurrent.TimeUnit


const val baseUrl = "http://10.0.2.2:8000"

interface SpotifyAPICallsService {

    companion object {
        operator fun invoke(): SpotifyAPICallsService {
            val client = OkHttpClient.Builder()
                .connectTimeout(150, TimeUnit.SECONDS)
                .writeTimeout(150, TimeUnit.SECONDS)
                .readTimeout(150, TimeUnit.SECONDS)
                .build()
            val retrofit = Retrofit.Builder().baseUrl(baseUrl).client(client).addConverterFactory(
                GsonConverterFactory.create()).build()
            return retrofit.create(SpotifyAPICallsService::class.java)
        }
    }

    @Headers("Content-Type:application/json; charset=UTF-8")
    @GET("/api/user_track_info")
    suspend fun getSongsOfUser(@Query("username") username: String): Response<JSONUserSongsResponseModel>

    @Headers("Content-Type:application/json; charset=UTF-8")
    @POST("/api/get_recommendations")
    suspend fun getRecommendations(@Body requestBody: RequestBody): Response<JSONUserSongsResponseModel>

}