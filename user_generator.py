import pandas as pd
from ast import literal_eval
import numpy as np

def main():
    # Cargamos nuestros datos de películas.
    df_movies = pd.read_csv("output_data/movies_data_final.csv")
    df_genres = pd.read_csv("output_data/genres_database.csv")
    df_keywords = pd.read_csv("output_data/keywords_database.csv")
    # Escogemos las peliculas segun los gustos de este usuario
    genre_filters = ['Action', 'Adventure', 'Animation']
    keyword_filters = ['pirate', 'shipwreck']
    genres_ids = df_genres[df_genres['name'].apply(lambda x: any(val in x for val in genre_filters))]
    keywords_ids = df_keywords[df_keywords['name'].apply(lambda x: any(val in x for val in keyword_filters))]
    genres_ids = genres_ids['id'].to_list()
    keywords_ids = keywords_ids['id'].to_list()
    # Las listas se guardan como strings en CVS.
    df_movies['genres'] = df_movies['genres'].apply(literal_eval)
    df_movies['keywords'] = df_movies['keywords'].apply(literal_eval)
    filtered_genres_df = df_movies[df_movies['genres'].apply(lambda x: any(val in x for val in genres_ids))]
    filtered_movies_df = filtered_genres_df[filtered_genres_df['keywords'].apply(lambda x: any(val in x for val in keywords_ids))]
    df_usuario = pd.DataFrame()
    # Solo cogemos 30% de las peliculas de ese tipo, para comprobar luego si el usuario es recomendado peliculas que tengan este tipo de genero y keywords por lo menos
    df_usuario['id'] = filtered_movies_df['id'].sample(int(0.4*filtered_movies_df.shape[0]), random_state=0)
    # Son peliculas que le han gustado
    np.random.seed(0)
    df_usuario['vote'] = np.random.uniform(7, 10,size=df_usuario.shape[0])
    df_usuario['visualized'] = np.random.uniform(0.7, 1,size=df_usuario.shape[0])
    df_usuario.to_csv('output_data/user1_data.csv', index=False)

if __name__ == "__main__":
    main()