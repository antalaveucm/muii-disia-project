import pandas as pd
from flask import Flask, request, jsonify
from sqlalchemy import create_engine, exc
import sqlalchemy.types as sqltypes

uid = 'database_admin'
pwd = '1234'
server = 'localhost'
database = 'movies_recomender'

engine = create_engine(f'postgresql+psycopg2://{uid}:{pwd}@{server}:5432/{database}')

app = Flask(__name__)

# GET users
# ejemplo llamada local: 
# curl http://192.168.1.208:5000/user?user_id=1
@app.route('/user', methods=['GET'])
def user_get():
    user_id = request.args.get('user_id', type=int)  # no puede ser None
    if not user_id :
        return jsonify({"error": "Debes enviar user_id como parámetro"}), 400
    
    try:
        sql = "SELECT * FROM users_watch_history WHERE user_id = %(user_id)s;"
        user_data = pd.read_sql_query(sql, engine, params={"user_id": user_id})

        if user_data.empty:
            return jsonify({"mensaje": f"No hay historial para el usuario {user_id}"}), 404

        user_data_dict = user_data.to_dict()
        return jsonify({"mensaje": f"Datos del usuario {user_id} recibidos correctamente"
                        , "data": user_data_dict
                        }), 200
    except exc.ProgrammingError:
        return jsonify({
            "mensaje": "Error de sintaxis en la consulta o la tabla no existe"
        }), 500

    except exc.SQLAlchemyError:
        return jsonify({
            "mensaje": "Error al acceder a la base de datos"
        }), 500


# POST user
# ejemplo llamada local: 
# curl -X POST http://192.168.1.208:5000/user -H "Content-Type: application/json" -d "{\"movie_id\": \"10\", \"user_id\": \"1\", \"vote\": \"8\", \"visualized\": \"1\"}"
@app.route('/user', methods=['POST'])
def user_post():
    data = request.json
    user_history_entry = pd.DataFrame([{
        "movie_id": data["movie_id"],
        "user_id": data["user_id"],
        "vote": data["vote"],
        "visualized": data["visualized"]
    }])
    try:
        user_history_entry.to_sql('users_watch_history', engine, index=False, if_exists='append', dtype={'user_id': sqltypes.INTEGER, 'movie_id': sqltypes.INTEGER})
        return jsonify({"mensaje": f"Valoracion de la pelicula {data["movie_id"]}, creada para el usuario {data["user_id"]}"}), 201
    except exc.IntegrityError as e:
        # Likely a foreign key constraint failure (user/movie ID doesn't exist)
        return jsonify({
            "mensaje": "Error de integridad: el usuario o la película no existen."
        }), 409  # Conflict

    except exc.DataError as e:
        # Wrong datatype, like a value being too long for a column
        return jsonify({
            "mensaje": "Error de datos: formato inválido o valor fuera de rango."
        }), 422  # Unprocessable Entity

    except exc.StatementError as e:
        # Probably a Python-side binding or type mismatch
        return jsonify({
            "mensaje": "Error de tipo: los datos enviados no son compatibles con la base de datos."
        }), 400  # Bad Request

    except exc.SQLAlchemyError as e:
        # Catch-all for unexpected SQL-related issues
        return jsonify({
            "mensaje": "Error inesperado al guardar en la base de datos."
        }), 500  # Internal Server Error

# GET movies
# ejemplo llamada local: 
# curl http://192.168.1.208:5000/movie
@app.route('/movie', methods=['GET'])
def movie_get():
    try:
        sql = "SELECT * FROM movies;"
        movies_df = pd.read_sql_query(sql, engine)
        movies_dict = movies_df.to_dict()
        return jsonify({"mensaje": f"Datos de películas recibidos correctamente"
                        , "data": movies_dict
                        }), 200
    except exc.ProgrammingError:
        return jsonify({
            "mensaje": "No existe la tabla 'movies' o hay un error de sintaxis en el SQL."
        }), 404
    
    except exc.SQLAlchemyError as e:
        return jsonify({
            "mensaje": "Error al acceder a la base de datos."
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

