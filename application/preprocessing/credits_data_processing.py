import pandas as pd
import json
import traceback

# 1. Configuración del parser JSON
class CustomJSONDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        super().__init__(object_hook=self.custom_hook, *args, **kwargs)
    
    def custom_hook(self, dct):
        return {k: v if v != 'null' else None for k, v in dct.items()}

# 2. Parseo seguro de JSON
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

# 3. Procesamiento de actores (usando ID original)
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

# 4. Procesamiento de director
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

# 5. Procesamiento principal
def main():
    # Cargar datos
    df = pd.read_csv("/tmp/tmdb_5000_credits.csv")
    
    # Procesar
    df['actors'] = df['cast'].apply(lambda x: json.dumps(process_cast(x), ensure_ascii=False))
    df['director'] = df['crew'].apply(process_crew)
    
    # Guardar resultados
    df[['movie_id', 'title', 'actors', 'director']].to_csv("credits_final.csv", index=False)
    
    # Generar base de datos de actores (sin IDs generados)
    all_actors = []
    for actors_list in df['actors'].apply(json.loads):
        all_actors.extend([{"id": a["id"], "name": a["name"]} for a in actors_list])
    
    actors_df = pd.DataFrame(all_actors).drop_duplicates()
    actors_df.to_csv("actors_database.csv", index=False)
    
    # Reporte final
    print("\n=== Reporte final ===")
    print(f"Total películas procesadas: {len(df)}")
    print(f"Películas sin director: {df['director'].isna().sum()}")
    print(f"Actores únicos registrados: {len(actors_df)}")
    print("\nEjemplo de datos:")
    print(df.sample(2)[['title', 'director', 'actors']])

if __name__ == "__main__":
    main()
