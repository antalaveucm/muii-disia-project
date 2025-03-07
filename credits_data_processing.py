import pandas as pd
import json
import uuid
from json import JSONDecoder
import traceback

# 1. Configuración inicial
class CustomJSONDecoder(JSONDecoder):
    def __init__(self, *args, **kwargs):
        super().__init__(object_hook=self.custom_hook, *args, **kwargs)
    
    def custom_hook(self, dct):
        return {k: v if v != 'null' else None for k, v in dct.items()}

# 2. Función de parseo ultra-robusta
def safe_json_parse(json_str):
    if pd.isna(json_str):
        return []
    
    attempts = [
        {'replace': ("'", '"'), 'fix_unicode': True},  # Intento 1: Comillas simples
        {'replace': [], 'fix_unicode': False},         # Intento 2: Datos crudos
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

# 3. Sistema de IDs único mejorado
class ActorRegistry:
    def __init__(self):
        self.registry = {}
    
    def get_id(self, name):
        if not name:
            return None
        
        # Normalización avanzada de nombres
        clean_name = ' '.join(name.strip().title().split())
        if not clean_name:
            return None
        
        if clean_name not in self.registry:
            self.registry[clean_name] = str(uuid.uuid5(uuid.NAMESPACE_DNS, clean_name))[:10]
        
        return {
            "id": self.registry[clean_name],
            "name": clean_name
        }

actor_registry = ActorRegistry()

# 4. Procesamiento de actores con registro detallado
def process_cast(cast_str):
    try:
        cast = safe_json_parse(cast_str)
        if not isinstance(cast, list):
            return []
        
        valid_actors = []
        for entry in cast:
            try:
                actor_info = actor_registry.get_id(entry.get('name'))
                if actor_info and 'order' in entry:
                    valid_actors.append({
                        **actor_info,
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

# 5. Procesamiento de director con validación exhaustiva
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

# 6. Procesamiento principal
def main():
    # Cargar datos
    df = pd.read_csv("data/tmdb_5000_credits.csv")
    
    # Procesar
    df['actors'] = df['cast'].apply(lambda x: json.dumps(process_cast(x), ensure_ascii=False))
    df['director'] = df['crew'].apply(process_crew)
    
    # Guardar resultados
    df[['movie_id', 'title', 'actors', 'director']].to_csv("movies_final.csv", index=False)
    
    # Guardar registro de actores
    pd.DataFrame(
        [{"id": v, "name": k} for k, v in actor_registry.registry.items()]
    ).to_csv("actors_database.csv", index=False)
    
    # Reporte final
    print("\n=== Reporte final ===")
    print(f"Total películas procesadas: {len(df)}")
    print(f"Películas sin director: {df['director'].isna().sum()}")
    print(f"Actores únicos registrados: {len(actor_registry.registry)}")
    print("\nEjemplo de datos:")
    print(df.sample(2)[['title', 'director', 'actors']])

if __name__ == "__main__":
    main()