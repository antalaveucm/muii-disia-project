import pandas as pd
import json

def main():
    # Cargar datos asegurando que los IDs sean strings
    movies = pd.read_csv("movies_final.csv", converters={"actors": json.loads})
    actors_db = pd.read_csv("actors_database.csv", dtype={"id": str})  # IDs como strings

    # Ejemplo 1: Películas de Christopher Nolan
    director_name = "Christopher Nolan"
    nolan_movies = movies[movies["director"] == director_name]["title"]
    print(f"\nPelículas de {director_name}:")
    print(nolan_movies.to_string(index=False))

    # Ejemplo 2: Buscar por nombre de actor
    actor_name = "Christian Bale"
    actor_info = actors_db[actors_db["name"] == actor_name]
    
    if not actor_info.empty:
        actor_id = actor_info["id"].values[0]  # Obtener ID real
        print(f"\nPelículas de {actor_name}:")
        
        peliculas_actor = movies[
            movies["actors"].apply(
                lambda x: any(str(actor["id"]) == actor_id for actor in x)
            )]["title"]
        
        print(peliculas_actor.to_string(index=False))
    else:
        print(f"\nActor '{actor_name}' no encontrado.")

if __name__ == "__main__":
    main()