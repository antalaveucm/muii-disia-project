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

    
    def recommend_movies(self, user_id, title=None, n=10, content_weight=0.7, rating_weight=0.2, popularity_weight=0.1):
        user_movies=None
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
            # Visualizar las películas que ha visto el usuario para valorar si las recomendaciones son correctas
            print("\n------Películas del usuario------")
            user_movie_list = self.movies_df[self.movies_df['id'].isin(user_movies['id'])][['id','title','genres', 'overview']]
            user_movie_list = pd.merge(user_movie_list, user_movies, how='inner', on=['id'])
            user_movie_list['genres_names'] = user_movie_list['genres'].apply(self._convert_genres)
            print(user_movie_list[['id','title', 'genres_names', 'overview', 'vote']])
            if user_movies.empty:
                return "No hay suficientes datos del usuario."
            #idx = user_movies.sample(1).index[0]
            ids = self.movies_df[self.movies_df['id'].isin(user_movies['id'])].index
        
        recommendations = {}
        for idx in ids:
            sim_scores = list(enumerate(self.cosine_sim[idx]))
            sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
            
            # Mezclar similitud, weight_rating y preferencias del usuario
            movie_indices = [i[0] for i in sim_scores[1:n*100]]
            for i in movie_indices:
                user_rating = 1
                if isinstance(user_movies,pd.DataFrame):
                    user_vote = user_movies[user_movies['id']==self.movies_df.iloc[idx]['id']]['vote'].iloc[0]
                    if user_vote:
                        user_rating = user_vote/6
                score = (self.cosine_sim[idx][i] * content_weight * user_rating + 
                        self.movies_df.iloc[i]['weight_rating']/self.movies_df['weight_rating'].max() * rating_weight + self.movies_df.iloc[i]['popularity'] * popularity_weight)
                
                # Si se recomienda una pelicula a partir de varias nos quedamos con el mejor score
                recommendation = recommendations.get(i)
                if(recommendation is None):
                    recommendations[i] = (i, score)
                else:
                    recommendations[i] = (i, max(recommendation[1], score))
        
        recommendations = sorted(recommendations.values(), key=lambda x: x[1], reverse=True)[:n]
            
        user_recommendations = self.movies_df[['id','title', 'genres', 'actors', 'overview', 'vote_average']].iloc[[i[0] for i in recommendations]]

        # Convertir géneros y actores a nombres
        user_recommendations['genres_names'] = user_recommendations['genres'].apply(
            self._convert_genres
        )
        user_recommendations['actors_names'] = user_recommendations['actors'].apply(
            self._convert_actors
        )

        # Mostrar detalles
        if isinstance(user_movies,pd.DataFrame):
            print("\n------Películas recomendadas------")
            user_recommendations = user_recommendations[~user_recommendations['id'].isin(user_movies['id'])]
        result = user_recommendations[['id','title', 'genres_names', 'actors_names', 'overview', 'vote_average']]
        return result

def main():
    recommender = Recommender()
    # Ejemplo: Recomendar basado en "Avatar" o preferencias del usuario
    print(recommender.recommend_movies(user_id=None, title='Avatar')) 
    # Usa las películas que el usuario ha visto
    print(recommender.recommend_movies(user_id=2))  # Usa las películas que el usuario ha visto

if __name__ == "__main__":
    main()