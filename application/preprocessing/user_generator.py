import pandas as pd
import numpy as np

from sqlalchemy import create_engine, text
import sqlalchemy.types as sqltypes

uid = 'database_admin'
pwd = '1234'
server = 'localhost'
database = 'movies_recomender'

engine = create_engine(f'postgresql+psycopg2://{uid}:{pwd}@{server}:5432/{database}')

def generate_users():
    #Crear tabla de usuarios
    sql = text("""CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        name TEXT UNIQUE);""")
    with engine.connect() as conn:
        conn.execute(sql)
        conn.commit()

    #Generar los usuarios
    try:
        names = ['Jane Doe', 'John Doe', 'Ector Empty']
        df_usuarios = pd.DataFrame({'name': names})
        df_usuarios.to_sql('users', engine, index=False, if_exists='append')
    except Exception as e:
        print(f"Excepction: {e}")
    
    
def make_user_watch_movies(user_id, genres_filters, keyword_filters):
    sql = text("""CREATE TABLE IF NOT EXISTS users_watch_history (
        user_id INTEGER,
        movie_id INTEGER,
        vote FLOAT,
        visualized FLOAT,
        FOREIGN KEY (movie_id) REFERENCES movies(id),
        FOREIGN KEY (user_id) REFERENCES users(id));""")
    with engine.connect() as conn:
        conn.execute(sql)
        conn.commit()
    # df_movies = pd.read_csv("output_data/movies_data_final.csv")
    # df_genres = pd.read_csv("output_data/genres_database.csv")
    # df_keywords = pd.read_csv("output_data/keywords_database.csv")
    sql = "SELECT * FROM movies;"
    df_movies = pd.read_sql_query(sql, engine)
    sql = "SELECT * FROM genres;"
    df_genres = pd.read_sql_query(sql, engine)
    sql = "SELECT * FROM keywords;"
    df_keywords = pd.read_sql_query(sql, engine)
    # Escogemos las peliculas segun los gustos de este usuario
    genres_ids = df_genres[df_genres['name'].apply(lambda x: any(val in x for val in genres_filters))]
    keywords_ids = df_keywords[df_keywords['name'].apply(lambda x: any(val in x for val in keyword_filters))]
    genres_ids = genres_ids['id'].to_list()
    keywords_ids = keywords_ids['id'].to_list()
    # Las listas se guardan como strings en CVS.
    filtered_genres_df = df_movies[df_movies['genres'].apply(lambda x: any(val in x for val in genres_ids))]
    filtered_movies_df = filtered_genres_df[filtered_genres_df['keywords'].apply(lambda x: any(val in x for val in keywords_ids))]
    df_historial = pd.DataFrame()
    # Solo cogemos 30% de las peliculas de ese tipo, para comprobar luego si el usuario es recomendado peliculas que tengan este tipo de genero y keywords por lo menos
    df_historial['movie_id'] = filtered_movies_df['id'].sample(int(0.4*filtered_movies_df.shape[0]), random_state=0)
    df_historial['user_id'] = user_id
    # Son peliculas que le han gustado
    np.random.seed(0)
    df_historial['vote'] = np.random.uniform(7, 10,size=df_historial.shape[0])
    df_historial['visualized'] = np.random.uniform(0.7, 1,size=df_historial.shape[0])
    try:
        df_historial.to_sql('users_watch_history', engine, index=False, if_exists='append', dtype={'user_id': sqltypes.INTEGER, 'movie_id': sqltypes.INTEGER})
    except Exception as e:
        print(f"Exception: {e}")
    
def main():
    generate_users()
    make_user_watch_movies(1,['Action', 'Adventure', 'Animation', 'Drama', 'Science Fiction'],['pirate', 'shipwreck', 'alien', 'escape'])
    make_user_watch_movies(2,['Action', 'Comedy'], ['future'])

if __name__ == "__main__":
    main()