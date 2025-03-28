import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Cargar datos
movies_df = pd.read_csv("output_data/movies_data_final.csv")
genres_df = pd.read_csv("output_data/genres_database.csv")
actors_df = pd.read_csv("output_data/actors_database.csv")

# Mapear IDs a nombres
genre_map = dict(zip(genres_df['id'], genres_df['name']))
actor_map = dict(zip(actors_df['id'], actors_df['name']))

# Usar metadata_soup para TF-IDF (ya incluye keywords, géneros, actores y director)
tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(movies_df['metadata_soup'].values.astype('U'))

# Calcular similitud
cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

# Función de recomendación mejorada
def recommend_movies(user_id, title=None, n=10, content_weight=0.7, rating_weight=0.3):

    if title:
        ids = [movies_df[movies_df['title'] == title].index[0]]
    else:
        # Obtener películas mejor valoradas por el usuario
        user_df = pd.read_csv("output_data/user{user_id}_data.csv".format(user_id = user_id))
        user_movies = user_df[user_df['visualized'] > 0.7]
        if user_movies.empty:
            return "No hay suficientes datos del usuario."
        #idx = user_movies.sample(1).index[0]
        ids = user_movies.index
    
    recommendations = {}
    for idx in ids:
        sim_scores = list(enumerate(cosine_sim[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        
        # Mezclar similitud, weight_rating y preferencias del usuario
        movie_indices = [i[0] for i in sim_scores[1:n*2]]
        for i in movie_indices:
            score = (cosine_sim[idx][i] * content_weight + 
                    movies_df.iloc[i]['weight_rating'] * rating_weight)
            
            # Si se recomienda una pelicula a partir de varias nos quedamos con el mejor score
            recommendation = recommendations.get(i)
            if(recommendation is None):
                recommendations[i] = (i, score)
            else:
                recommendations[i] = (i, max(recommendation[1], score))
    
    recommendations = sorted(recommendations.values(), key=lambda x: x[1], reverse=True)[:n]
        
    user_recommendations = movies_df[['title', 'genres', 'actors', 'overview', 'vote_average']].iloc[[i[0] for i in recommendations]]

    # Convertir géneros y actores a nombres
    user_recommendations['genres_names'] = user_recommendations['genres'].apply(
        lambda x: [genre_map[int(g)] if str.isdigit(g) else '' for g in x.strip("[]").replace("'", "").split(", ")]
    )
    user_recommendations['actors_names'] = user_recommendations['actors'].apply(
        lambda x: [actor_map[int(a)] if str.isdigit(a) else '' for a in x.strip("[]").replace("'", "").split(", ")]
    )

    # Mostrar detalles
    result = user_recommendations[['title', 'genres_names', 'actors_names', 'overview', 'vote_average']]
    return result

# Ejemplo: Recomendar basado en "Avatar" o preferencias del usuario
print(recommend_movies(user_id=None, title='Avatar')) 
# Usa las películas que el usuario ha visto
print(recommend_movies(user_id=1))  # Usa las películas que el usuario ha visto
