import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Cargar datos
movies_df = pd.read_csv("output_data/movies_data_final.csv")
genres_df = pd.read_csv("output_data/genres_database.csv")
actors_df = pd.read_csv("output_data/actors_database.csv")
user1_df = pd.read_csv("output_data/user1_data.csv")

# Mapear IDs a nombres
genre_map = dict(zip(genres_df['id'], genres_df['name']))
actor_map = dict(zip(actors_df['id'], actors_df['name']))

# Convertir géneros y actores a nombres
movies_df['genres_names'] = movies_df['genres'].apply(
    lambda x: [genre_map[int(g)] for g in x.strip("[]").replace("'", "").split(", ")]
)
movies_df['actors_names'] = movies_df['actors'].apply(
    lambda x: [actor_map[int(a)] for a in x.strip("[]").replace("'", "").split(", ")]
)

# Usar metadata_soup para TF-IDF (ya incluye keywords, géneros, actores y director)
tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(movies_df['metadata_soup'])
print(tfidf_matrix.size)
# Calcular similitud
cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

# Función de recomendación mejorada
def recommend_movies(user_id, title=None, n=10, content_weight=0.7, rating_weight=0.3):
    if title:
        idx = movies_df[movies_df['title'] == title].index[0]
    else:
        # Obtener películas mejor valoradas por el usuario
        user_movies = user1_df[user1_df['visualized'] > 0.7]
        if user_movies.empty:
            return "No hay suficientes datos del usuario."
        idx = user_movies.sample(1).index[0]
    
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    
    # Mezclar similitud, weight_rating y preferencias del usuario
    movie_indices = [i[0] for i in sim_scores[1:n*2]]
    recommendations = []
    for i in movie_indices:
        score = (cosine_sim[idx][i] * content_weight + 
                movies_df.iloc[i]['weight_rating'] * rating_weight)
        recommendations.append((i, score))
    
    recommendations = sorted(recommendations, key=lambda x: x[1], reverse=True)[:n]
    print(recommendations)
    
    # Mostrar detalles
    result = movies_df[['title', 'genres_names', 'actors_names', 'overview', 'vote_average']].iloc[[i[0] for i in recommendations]]
    return result

# Ejemplo: Recomendar basado en "Avatar" o preferencias del usuario
print(recommend_movies(user_id=1))  # Usa las películas que el usuario ha visto
