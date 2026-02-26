# users_service.py
from flask import Flask, jsonify, request

app = Flask(__name__)

users = [
    {"id": 101, "name": "Carlos"},
    {"id": 202, "name": "Ana"}
]

@app.route('/users', methods=['GET'])
def get_users():
    return jsonify(users)

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = next((u for u in users if u['id'] == user_id), None)
    if user:
        return jsonify(user)
    return jsonify({"error": "User not found"}), 404

if __name__ == '__main__':
    app.run(port=5000, host='0.0.0.0')