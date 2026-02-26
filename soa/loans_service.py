# loans_service.py
from flask import Flask, jsonify, request
import json
import os
from datetime import datetime
import requests

app = Flask(__name__)

# Configuration for shared data persistence
DATA_DIR = '/data/library'
LOANS_FILE = os.path.join(DATA_DIR, 'loans.json')

# Initialize loans list
loans = []

def save_loans():
    """Save loans to JSON file in shared volume"""
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(LOANS_FILE, 'w') as f:
            json.dump(loans, f, indent=2)
    except Exception as e:
        print(f"Error saving loans: {e}")
        raise

def load_loans():
    """Load loans from JSON file if it exists"""
    global loans
    try:
        if os.path.exists(LOANS_FILE):
            with open(LOANS_FILE, 'r') as f:
                loans = json.load(f)
    except Exception as e:
        print(f"Error loading loans: {e}")
        # Keep empty list if file can't be loaded

@app.route('/loans', methods=['GET'])
def get_loans():
    load_loans()  # Reload to get latest data
    return jsonify(loans)

@app.route('/loans/<int:loan_id>', methods=['GET'])
def get_loan(loan_id):
    load_loans()  # Reload to get latest data
    loan = next((l for l in loans if l['id'] == loan_id), None)
    if loan:
        return jsonify(loan)
    return jsonify({"error": "Loan not found"}), 404

@app.route('/loans', methods=['POST'])
def create_loan():
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400

    load_loans()
    data = request.get_json()

    if not all(key in data for key in ['book_id', 'user_id']):
        return jsonify({"error": "Book ID and User ID are required"}), 400

    new_loan = {
        "id": max(l['id'] for l in loans) + 1 if loans else 1,
        "book_id": data['book_id'],
        "user_id": data['user_id'],
        "loan_date": datetime.now().isoformat(),
        "return_date": None,
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

    loan['status'] = "returned"
    loan['return_date'] = datetime.now().isoformat()

    save_loans()
    return jsonify(loan), 200

if __name__ == '__main__':
    # Ensure data directory exists
    os.makedirs(DATA_DIR, exist_ok=True)
    # Initialize data if needed
    if not os.path.exists(LOANS_FILE):
        save_loans()
    app.run(host='0.0.0.0', port=5000)