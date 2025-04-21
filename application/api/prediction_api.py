from flask import Flask, request, jsonify
from application.model.model_v1 import Recommender
app = Flask(__name__)

# GET movies
# ejemplos llamada local: 
# curl http://192.168.1.208:5000/predict?user_id=1
# curl http://192.168.1.208:5000/predict?user_id=1&title=Avatar
@app.route('/predict', methods=['GET'])
def movie_get():
    user_id = request.args.get('user_id', type=int)  # no puede ser None
    title = request.args.get('title', type=str)      # puede ser None

    print(title)
    if not user_id :
        return jsonify({"error": "Debes enviar user_id como parámetro"}), 400

    # TODO cambiar la BBDD que se usa en el recomendador y hacer la llamada al API de BBDD para cargar los datos del usuario
    recommender = Recommender()
    recommendation = recommender.recommend_movies(user_id=user_id, title=title)
    return jsonify({"mensaje": "Recomendación realizada correctamente", "recommendation": recommendation.to_dict('index')}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)