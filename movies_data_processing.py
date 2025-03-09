import pandas as pd
import json
from ast import literal_eval
import traceback

def get_list(x, n):
    if isinstance(x, list):
        names = [i['id'] for i in x]
        #Check if more than N elements exist. If yes, return only first N elements. If no, return entire list.
        if len(names) > n and n>0:
            names = names[:n]
        return names

    #Return empty list in case of missing/malformed data
    return []

# Creamos la sopa de metadatos que utilizaremos para medir la similitud entre películas
def create_soup(x):
    features = ['keywords', 'genres', 'actors']
    soup = ''
    for feature in features:
        for e in x[feature]:
            value = feature[:3]+str(e)
            soup += value + ' '
    soup += ' ' + str.lower(x['director'].replace(" ", ""))
    return soup

# Configuración del parser JSON
class CustomJSONDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        super().__init__(object_hook=self.custom_hook, *args, **kwargs)
    
    def custom_hook(self, dct):
        return {k: v if v != 'null' else None for k, v in dct.items()}

# Parseo seguro de JSON
def safe_json_parse(json_str):
    if pd.isna(json_str):
        return []
    
    attempts = [
        {'replace': ("'", '"'), 'fix_unicode': True},
        {'replace': [], 'fix_unicode': False},
    ]
    
    for attempt in attempts:
        try:
            fixed_str = json_str
            for old, new in attempt['replace']:
                fixed_str = fixed_str.replace(old, new)
                
            if attempt['fix_unicode']:
                fixed_str = bytes(fixed_str, 'utf-8').decode('unicode_escape')
            
            return json.loads(fixed_str, cls=CustomJSONDecoder)
        except Exception:
            continue
    
    print(f"Error grave en JSON: {json_str[:100]}... (longitud: {len(json_str)})")
    return []

# Procesamiento de actores (usando ID original)
def process_cast(cast_str):
    try:
        cast = safe_json_parse(cast_str)
        if not isinstance(cast, list):
            return []
        
        valid_actors = []
        for entry in cast:
            try:
                if 'id' in entry and 'name' in entry:  # Usar ID existente
                    valid_actors.append({
                        "id": str(entry['id']),
                        "name": ' '.join(entry['name'].strip().title().split()),
                        "order": int(entry['order']) if str(entry['order']).isdigit() else 999
                    })
            except Exception as e:
                print(f"Error en actor: {entry} | Error: {str(e)}")
                continue
        
        return sorted(valid_actors, key=lambda x: x['order'])[:10]
    
    except Exception as e:
        print(f"Error catastrófico en cast: {str(e)}")
        traceback.print_exc()
        return []

# Procesamiento de director
def process_crew(crew_str):
    try:
        crew = safe_json_parse(crew_str)
        if not isinstance(crew, list):
            return None
        
        for member in crew:
            try:
                if isinstance(member, dict) and member.get('job', '').lower() == 'director':
                    name = member.get('name')
                    if name:
                        return ' '.join(name.strip().title().split())
            except Exception:
                continue
        return None
    except Exception as e:
        print(f"Error en crew: {str(e)}")
        return None

# Procesamiento principal
def process_credits():
    # Cargar datos
    df_credits = pd.read_csv("data/tmdb_5000_credits.csv")
    
    # Procesar
    df_credits['actors'] = df_credits['cast'].apply(lambda x: json.dumps(process_cast(x), ensure_ascii=False))
    df_credits['director'] = df_credits['crew'].apply(process_crew)
    
    return df_credits[['movie_id', 'actors', 'director']]


def main():
    # Cargar datos
    df = pd.read_csv("data/tmdb_5000_movies.csv")
    # Unir ambas bases de datos para tener datos más completos
    df_credits = process_credits()
    df_credits.rename(columns={'movie_id': 'id'}, inplace=True)
    df_movies = df.merge(df_credits, on='id', how='left')

    #Eliminación de variables no deseadas
    var_no_deseadas = ['budget','homepage','original_language','original_title','production_companies','production_countries','revenue','spoken_languages','tagline']
    df_movies.drop(columns=var_no_deseadas, inplace=True)
    
    # Procesar películas
    # No utilizaremos datos de películas que todavia no estan disponibles
    df_movies.drop(df_movies[df_movies['status']!='Released'].index, inplace=True)
    average_rating_movies = df_movies['vote_average'].mean() # media global de todas las películas
    min_votes = df_movies['vote_count'].quantile(0.9) # umbral minimo de votos (90% de las peliculas alcanzan este número de votos)
    # Las peliculas que no tengan una cantidad de votos minima tampoco se tendran en cuenta para las recomendaciones.
    df_movies.drop(df_movies[df_movies['vote_count']<min_votes].index, inplace=True)

    # Transformar los valores de las variables.
    features = ['keywords', 'genres', 'actors']
    for feature in features:
        #Parsear el string a su objeto de python correspondiente (lista, diccionario, etc)
        df_movies[feature] = df_movies[feature].apply(literal_eval)
        # Crear base de datos para saber que significa cada identificador
        all_features = []
        for features_list in df_movies[feature]:
            all_features.extend([{"id": a["id"], "name": a["name"]} for a in features_list])
        features_df = pd.DataFrame(all_features).drop_duplicates()
        features_df.to_csv('output_data/'+str(feature)+'_database.csv', index=False)
        #Solo nos interesan las 5 primeras ids de las variables.
        df_movies[feature] = df_movies[feature].apply(get_list, n=0)
        
    # Crear nuevas variables para las películas
    # Metadatos juntados para valorar la similitud entre películas
    df_movies['metadata_soup'] = df_movies.apply(create_soup, axis= 1)
    # Valoración ponderada por cantidad de votos
    weight_rating = (df_movies['vote_count']/(df_movies['vote_count']+min_votes))*df_movies['vote_average'] + (min_votes/(df_movies['vote_count']+min_votes))*average_rating_movies
    df_movies['weight_rating'] = round(weight_rating, 2)
    
    # Guardar resultados
    df_movies.to_csv('output_data/movies_data_final.csv', index=False)

if __name__ == "__main__":
    main()