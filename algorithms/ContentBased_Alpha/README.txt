Data set used: https://www.kaggle.com/code/vatsalmavani/music-recommendation-system-using-spotify-dataset/data

This is an example implementation of a Content Based Algorithm.

- Input Song is Piano Man by Billy Joel
- Model "Database" is songs comprised of Billy Joel and Kanye West (total of 282 songs)

- Using only 2 features from the datasets in our recommender system (danceability and energy)

- Using Cosine Similarity to compare the Input Song Vector, against the "Database" vectors, to find the closest vector

- Plots the "Database" song vectors and the Top 10 Recommended song vectors, to show the value of the recommender system