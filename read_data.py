import pandas as pd
import json

# Cargar y visualizar
movies = pd.read_csv("movies_final.csv")
movies['actors'] = movies['actors'].apply(json.loads)  # Convertir a lista de IDs

# Ejemplo: Buscar todas las películas de un director
director_name = "Christopher Nolan"
print(f"\nPelículas de {director_name}:")
print(movies[movies['director'] == director_name][['title', 'actors']])

# Ejemplo: Buscar actor por ID
actor_id = "64058c3e-9"  # Ejemplo
print("\nActor encontrado:")
actors_db = pd.read_csv("actors_database.csv")
actor_info = actors_db[actors_db['id'] == actor_id]
print(actor_info)

# Filtrar películas donde aparece el actor
if not actor_info.empty:
    print(f"\nPelículas en las que aparece el actor con ID '{actor_id}':")
    peliculas_actor = movies[movies['actors'].apply(lambda x: any(actor['id'] == actor_id for actor in x))][['title', 'director']]
    print(peliculas_actor)
else:
    print(f"\nNo se encontraron películas para el actor con ID '{actor_id}'.")