from flask import Flask, request, jsonify
app = Flask(__name__)

# GET users
# ejemplo llamada local: 
# curl http://192.168.1.208:5000/user?user_id=1
@app.route('/user', methods=['GET'])
def user_get():
    user_id = request.args.get('user_id', type=int)  # no puede ser None
    if not user_id :
        return jsonify({"error": "Debes enviar user_id como parámetro"}), 400
    
    # TODO devolver los datos de ese usuario como dict
    # user_data.to_dict('index')
    return jsonify({"mensaje": f"Datos del usuario {user_id} recibidos correctamente"
                    #, "data": user_data.to_dict('index')
                    }), 200

# POST user
# ejemplo llamada local: 
# curl -X POST http://192.168.1.208:5000/user -H "Content-Type: application/json" -d "{\"movie_id\": \"10\", \"user_id\": \"1\", \"vote\": \"8\", \"visualized\": \"1\"}"
@app.route('/user', methods=['POST'])
def user_post():
    data = request.json
    movie_id = data["movie_id"]
    user_id = data["user_id"]
    vote = data["vote"]
    visualized = data["visualized"]
    # TODO añadir a BBDD
    return jsonify({"mensaje": f"Valoracion de la pelicula {movie_id}, creada para el usuario {user_id}"}), 201

# GET users
# ejemplo llamada local: 
# curl http://192.168.1.208:5000/movie
@app.route('/movie', methods=['GET'])
def movie_get():
    # TODO devolver los datos de todas las peliculas como dict
    return jsonify({"mensaje": f"¡Hola mundo!"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

