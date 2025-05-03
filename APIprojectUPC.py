from flask import Flask, request, jsonify

app = Flask(__name__)
player_position = {"x": 0, "y": 0, "angle": 0}

@app.route('/position', methods=['GET'])
def get_position():
    return jsonify(player_position)

@app.route('/position', methods=['POST'])
def update_position():
    data = request.json
    player_position["x"] = data.get("x", 0)
    player_position["y"] = data.get("y", 0)
    player_position["angle"] = data.get("angle", 0)
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(port=5000)