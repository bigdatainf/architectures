from flask import Flask, request, jsonify
import requests
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

ESB_URL = "http://esb:5000/message"

def build_message(service, operation, body):
    return {
        "header": {
            "service": service,
            "operation": operation,
            "version": "1.0",
            "timestamp": datetime.utcnow().isoformat()
        },
        "body": body
    }

# -------------------------
# BOOKS
# -------------------------

@app.route('/available_books', methods=['GET'])
def available_books():
    message = build_message("BooksService", "available_books", {})
    response = requests.post(ESB_URL, json=message)
    return jsonify(response.json())


@app.route('/borrowed_books', methods=['GET'])
def borrowed_books():
    message = build_message("BooksService", "borrowed_books", {})
    response = requests.post(ESB_URL, json=message)
    return jsonify(response.json())


# -------------------------
# USERS
# -------------------------

@app.route('/registered_users', methods=['GET'])
def registered_users():
    message = build_message("UsersService", "registered_users", {})
    response = requests.post(ESB_URL, json=message)
    return jsonify(response.json())


# -------------------------
# LOANS
# -------------------------

@app.route('/active_loans', methods=['GET'])
def active_loans():
    message = build_message("LoansService", "active_loans", {})
    response = requests.post(ESB_URL, json=message)
    return jsonify(response.json())


@app.route('/borrow_book', methods=['POST'])
def borrow_book():
    data = request.json
    message = build_message("LoansService", "borrow_book", data)
    response = requests.post(ESB_URL, json=message)
    return jsonify(response.json())


@app.route('/return_book', methods=['PUT'])
def return_book():
    data = request.json
    message = build_message("LoansService", "return_book", data)
    response = requests.post(ESB_URL, json=message)
    return jsonify(response.json())


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)