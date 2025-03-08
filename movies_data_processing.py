import pandas as pd
from ast import literal_eval

def get_list(x, n):
    if isinstance(x, list):
        names = [i['name'] for i in x]
        #Check if more than N elements exist. If yes, return only first N elements. If no, return entire list.
        if len(names) > n and n>0:
            names = names[:n]
        return names

    #Return empty list in case of missing/malformed data
    return []

def clean_string_data(x):
    if isinstance(x, list):
        return [str.lower(i.replace(" ", "")) for i in x]
    else:
        #Check if data exists. If not, return empty string
        if isinstance(x, str):
            return str.lower(x.replace(" ", ""))
        else:
            return ''

# Creamos la sopa de metadatos que utilizaremos para medir la similitud entre películas
def create_soup(x):
    return ' '.join(x['keywords']) + ' '.join(x['genres'])


def main():
    # Cargar datos
    df_movies = pd.read_csv("data/tmdb_5000_movies.csv")

    #Eliminación de variables no deseadas
    var_no_deseadas = ['budget','homepage','original_language','original_title','overview',"revenue",'production_companies','production_countries','tagline']
    df_movies.drop(columns=var_no_deseadas, inplace=True)
    
    # Procesar películas
    # No utilizaremos datos de películas que todavia no estan disponibles
    df_movies.drop(df_movies[df_movies['status']!='Released'].index, inplace=True)
    average_rating_movies = df_movies['vote_average'].mean() # media global de todas las películas
    min_votes = df_movies['vote_count'].quantile(0.9) # umbral minimo de votos (90% de las peliculas alcanzan este número de votos)
    # Las peliculas que no tengan una cantidad de votos minima tampoco se tendran en cuenta para las recomendaciones.
    df_movies.drop(df_movies[df_movies['vote_count']<min_votes].index, inplace=True)

    # Transformar los valores de las variables.
    features = ['keywords', 'genres']
    for feature in features:
        #Parsear el string a su objeto de python correspondiente (lista, diccionario, etc)
        df_movies[feature] = df_movies[feature].apply(literal_eval)
        #Obtenemos los valores de los nombres, no nos interesa la id.
        df_movies[feature] = df_movies[feature].apply(get_list, n=3)
        #Limpiamos los valores string para que sean consistentes y diferentes (nombre y apellidos juntos para evitar confusiones con actores con el mismo nombre)
        df_movies[feature] = df_movies[feature].apply(clean_string_data)
        
    # Crear nuevas variables para las películas
    # Metadatos juntados para valorar la similitud entre películas
    df_movies['metadata_soup'] = df_movies.apply(create_soup, axis= 1)
    # Valoración ponderada por cantidad de votos
    weight_rating = (df_movies['vote_count']/(df_movies['vote_count']+min_votes))*df_movies['vote_average'] + (min_votes/(df_movies['vote_count']+min_votes))*average_rating_movies
    df_movies['weight_rating'] = round(weight_rating, 2)
    
    # Guardar resultados
    df_movies.to_csv("movies_data_final.csv", index=False)
    
    # Reporte final
    print(df_movies[['vote_count','vote_average','weight_rating']])

if __name__ == "__main__":
    main()