import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# # Cargar datos
# movies_df = pd.read_csv("output_data/movies_data_final.csv")
# genres_df = pd.read_csv("output_data/genres_database.csv")
# actors_df = pd.read_csv("output_data/actors_database.csv")

# # Mapear IDs a nombres
# genre_map = dict(zip(genres_df['id'], genres_df['name']))
# actor_map = dict(zip(actors_df['id'], actors_df['name']))

# # Usar metadata_soup para TF-IDF (ya incluye keywords, géneros, actores y director)
# tfidf = TfidfVectorizer(stop_words='english')
# tfidf_matrix = tfidf.fit_transform(movies_df['metadata_soup'].values.astype('U'))

# # Calcular similitud
# cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

# Función de recomendación mejorada

DATA_PATH = "output_data/"


class Recommender:
    def __init__(self):
        # Cargar datos dentro de la clase
        self._movies_df = None
        self._genres_df = None
        self._actors_df = None
        self._genre_map = None
        self._actor_map = None
        self._tfidf_matrix = None
        self._cosine_sim = None
    
    # Solo cargamos datos cuando lo necesitamos
    @property
    def movies_df(self):
        if self._movies_df is None:
            self._movies_df = pd.read_csv(DATA_PATH + "movies_data_final.csv")
        return self._movies_df
    
    @property
    def genres_df(self):
        if self._genres_df is None:
            self._genres_df = pd.read_csv(DATA_PATH + "genres_database.csv")
        return self._genres_df

    @property
    def actors_df(self):
        if self._actors_df is None:
            self._actors_df = pd.read_csv(DATA_PATH + "actors_database.csv")
        return self._actors_df
    
    @property
    def actor_map(self):
        if self._actor_map is None:
            self._actor_map = dict(zip(self.actors_df['id'], self.actors_df['name']))
        return self._actor_map
    
    @property
    def genre_map(self):
        if self._genre_map is None:
            self._genre_map = dict(zip(self.genres_df['id'], self.genres_df['name']))
        return self._genre_map

    @property
    def cosine_sim(self):
        if self._cosine_sim is None:
            tfidf = TfidfVectorizer(stop_words='english')
            self._tfidf_matrix = tfidf.fit_transform(self.movies_df['metadata_soup'].astype(str))
            self._cosine_sim = cosine_similarity(self._tfidf_matrix, self._tfidf_matrix)
        return self._cosine_sim
    
    def _convert_genres(self, genre_str):
        return [self.genre_map[int(g)] if g.isdigit() else '' for g in genre_str.strip("[]").replace("'", "").split(", ")]

    def _convert_actors(self, actor_str):
        return [self.actor_map[int(a)] if a.isdigit() else '' for a in actor_str.strip("[]").replace("'", "").split(", ")]

    
    def recommend_movies(self, user_id, title=None, n=10, content_weight=0.7, rating_weight=0.3):

        if title:
            # Comprobamos que la película usada cómo parámetro está en la base de datos
            try:
                ids = [self.movies_df[self.movies_df['title'] == title].index[0]]
            except IndexError:
                return f"La película {title} no está en la base de datos"
        else:
            # Obtener películas mejor valoradas por el usuario
            user_df = pd.read_csv(DATA_PATH + "user{user_id}_data.csv".format(user_id = user_id))
            user_movies = user_df[user_df['visualized'] > 0.7]
            if user_movies.empty:
                return "No hay suficientes datos del usuario."
            #idx = user_movies.sample(1).index[0]
            ids = user_movies.index
        
        recommendations = {}
        for idx in ids:
            sim_scores = list(enumerate(self.cosine_sim[idx]))
            sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
            
            # Mezclar similitud, weight_rating y preferencias del usuario
            movie_indices = [i[0] for i in sim_scores[1:n*2]]
            for i in movie_indices:
                score = (self.cosine_sim[idx][i] * content_weight + 
                        self.movies_df.iloc[i]['weight_rating'] * rating_weight)
                
                # Si se recomienda una pelicula a partir de varias nos quedamos con el mejor score
                recommendation = recommendations.get(i)
                if(recommendation is None):
                    recommendations[i] = (i, score)
                else:
                    recommendations[i] = (i, max(recommendation[1], score))
        
        recommendations = sorted(recommendations.values(), key=lambda x: x[1], reverse=True)[:n]
            
        user_recommendations = self.movies_df[['title', 'genres', 'actors', 'overview', 'vote_average']].iloc[[i[0] for i in recommendations]]

        # Convertir géneros y actores a nombres
        user_recommendations['genres_names'] = user_recommendations['genres'].apply(
            self._convert_genres
        )
        user_recommendations['actors_names'] = user_recommendations['actors'].apply(
            self._convert_actors
        )

        # Mostrar detalles
        result = user_recommendations[['title', 'genres_names', 'actors_names', 'overview', 'vote_average']]
        return result

def main():
    recommender = Recommender()
    # Ejemplo: Recomendar basado en "Avatar" o preferencias del usuario
    print(recommender.recommend_movies(user_id=None, title='Avatar')) 
    # Usa las películas que el usuario ha visto
    print(recommender.recommend_movies(user_id=1))  # Usa las películas que el usuario ha visto

if __name__ == "__main__":
    main()