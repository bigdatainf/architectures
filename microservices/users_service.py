from flask import Flask, jsonify, request
import json
import os

app = Flask(__name__)

# Service-owned storage
DATA_DIR = "/data"
USERS_FILE = os.path.join(DATA_DIR, "users.json")

os.makedirs(DATA_DIR, exist_ok=True)


# -----------------------------
# Persistence
# -----------------------------

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    else:
        initial_users = [
            {"id": 101, "name": "Carlos"},
            {"id": 202, "name": "Ana"}
        ]
        save_users(initial_users)
        return initial_users


def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)


users = load_users()


# -----------------------------
# Read Operations
# -----------------------------

@app.route('/users', methods=['GET'])
def get_users():
    global users
    users = load_users()
    return jsonify(users)


@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    global users
    users = load_users()
    user = next((u for u in users if u['id'] == user_id), None)

    if user:
        return jsonify(user)
    return jsonify({"error": "User not found"}), 404


# -----------------------------
# Write Operations (Optional CRUD)
# -----------------------------

@app.route('/users', methods=['POST'])
def create_user():
    global users
    users = load_users()

    data = request.get_json()

    name = data.get("name")
    if not name:
        return jsonify({"error": "name is required"}), 400

    new_user = {
        "id": max([u["id"] for u in users], default=100) + 1,
        "name": name
    }

    users.append(new_user)
    save_users(users)

    return jsonify(new_user), 201


if __name__ == '__main__':
    app.run(port=5000, host='0.0.0.0')