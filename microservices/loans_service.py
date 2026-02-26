from flask import Flask, jsonify, request
import json
import os
from datetime import datetime
import requests

app = Flask(__name__)

# Persistence (service-owned storage)
DATA_DIR = '/data'
LOANS_FILE = os.path.join(DATA_DIR, 'loans.json')

# Service endpoints (direct communication)
BOOKS_SERVICE = "http://books:5000"
USERS_SERVICE = "http://users:5000"

loans = []


# -----------------------------
# Persistence
# -----------------------------

def save_loans():
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(LOANS_FILE, 'w') as f:
        json.dump(loans, f, indent=2)


def load_loans():
    global loans
    if os.path.exists(LOANS_FILE):
        with open(LOANS_FILE, 'r') as f:
            loans = json.load(f)


# -----------------------------
# Read Operations
# -----------------------------

@app.route('/loans', methods=['GET'])
def get_loans():
    load_loans()
    return jsonify(loans)


@app.route('/loans/<int:loan_id>', methods=['GET'])
def get_loan(loan_id):
    load_loans()
    loan = next((l for l in loans if l['id'] == loan_id), None)

    if loan:
        return jsonify(loan)
    return jsonify({"error": "Loan not found"}), 404


# -----------------------------
# Write Operations (Business Logic Here)
# -----------------------------

@app.route('/loans', methods=['POST'])
def borrow_book():

    load_loans()
    data = request.get_json()

    book_id = data.get("book_id")
    user_id = data.get("user_id")

    if not book_id or not user_id:
        return jsonify({"error": "book_id and user_id required"}), 400

    # Validate user
    user_response = requests.get(f"{USERS_SERVICE}/users/{user_id}")
    if not user_response.ok:
        return jsonify({"error": "User not found"}), 404

    # Validate book
    book_response = requests.get(f"{BOOKS_SERVICE}/books/{book_id}")
    if not book_response.ok:
        return jsonify({"error": "Book not found"}), 404

    book = book_response.json()

    if book.get("status") != "available":
        return jsonify({"error": "Book not available"}), 400

    # Update book status
    update_response = requests.put(
        f"{BOOKS_SERVICE}/books/{book_id}/status",
        json={"status": "borrowed"}
    )

    if not update_response.ok:
        return jsonify({"error": "Failed to update book status"}), 500

    # Create loan record
    new_loan = {
        "id": max([l["id"] for l in loans], default=0) + 1,
        "book_id": book_id,
        "user_id": user_id,
        "loan_date": datetime.now().isoformat(),
        "status": "active"
    }

    loans.append(new_loan)
    save_loans()

    return jsonify(new_loan), 201


@app.route('/loans/<int:loan_id>/return', methods=['PUT'])
def return_book(loan_id):

    load_loans()

    loan = next((l for l in loans if l['id'] == loan_id), None)

    if not loan:
        return jsonify({"error": "Loan not found"}), 404

    if loan['status'] != "active":
        return jsonify({"error": "Loan is not active"}), 400

    # Update book status
    update_response = requests.put(
        f"{BOOKS_SERVICE}/books/{loan['book_id']}/status",
        json={"status": "available"}
    )

    if not update_response.ok:
        return jsonify({"error": "Failed to update book status"}), 500

    # Update loan
    loan['status'] = "returned"
    loan['return_date'] = datetime.now().isoformat()

    save_loans()

    return jsonify(loan), 200


if __name__ == '__main__':
    os.makedirs(DATA_DIR, exist_ok=True)
    load_loans()
    app.run(host='0.0.0.0', port=5000)