from flask import Flask, request, jsonify
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Internal service registry (NOT exposed externally)
services = {
    'books': 'http://books:5000',
    'loans': 'http://loans:5000',
    'notifications': 'http://notifications:5000',
    'users': 'http://users:5000',
}
# -----------------------------
# READ OPERATIONS (Business APIs)
# -----------------------------

@app.route('/available_books', methods=['GET'])
def available_books():
    try:
        response = requests.get(f"{services['books']}/books")
        books = response.json()
        available = [b for b in books if b.get('status') == "available"]
        return jsonify(available), 200
    except requests.exceptions.RequestException:
        return jsonify({"error": "Books service unavailable"}), 503


@app.route('/borrowed_books', methods=['GET'])
def borrowed_books():
    try:
        response = requests.get(f"{services['books']}/books")
        books = response.json()
        borrowed = [b for b in books if b.get('status') == "borrowed"]
        return jsonify(borrowed), 200
    except requests.exceptions.RequestException:
        return jsonify({"error": "Books service unavailable"}), 503


@app.route('/registered_users', methods=['GET'])
def registered_users():
    try:
        response = requests.get(f"{services['users']}/users")
        return jsonify(response.json()), 200
    except requests.exceptions.RequestException:
        return jsonify({"error": "Users service unavailable"}), 503


@app.route('/active_loans', methods=['GET'])
def active_loans():
    try:
        response = requests.get(f"{services['loans']}/loans")
        loans = response.json()
        active = [l for l in loans if l.get('status') == "active"]
        return jsonify(active), 200
    except requests.exceptions.RequestException:
        return jsonify({"error": "Loans service unavailable"}), 503


# -----------------------------
# WRITE OPERATIONS (Orchestration)
# -----------------------------

@app.route('/borrow_book', methods=['POST'])
def borrow_book():
    data = request.json
    book_id = data.get('book_id')
    user_id = data.get('user_id')

    if not book_id or not user_id:
        return jsonify({"error": "book_id and user_id are required"}), 400

    try:
        # Validate user
        user_response = requests.get(
            f"{services['users']}/users/{user_id}"
        )
        if not user_response.ok:
            return jsonify({"error": "User not found"}), 404

        # Validate book
        book_response = requests.get(
            f"{services['books']}/books/{book_id}"
        )
        if not book_response.ok:
            return jsonify({"error": "Book not found"}), 404

        book = book_response.json()

        if book.get('status') != "available":
            return jsonify({"error": "Book not available"}), 400

        # Update book status to borrowed (ESB responsibility)
        update_response = requests.put(
            f"{services['books']}/books/{book_id}/status",
            json={"status": "borrowed"}
        )
        if not update_response.ok:
            return jsonify({"error": "Failed to update book status"}), 500

        # Create loan
        loan_data = {
            "book_id": book_id,
            "user_id": user_id
        }

        loan_response = requests.post(
            f"{services['loans']}/loans",
            json=loan_data
        )

        if not loan_response.ok:
            # Optional compensation logic
            # Rollback book status
            requests.put(
                f"{services['books']}/books/{book_id}/status",
                json={"status": "available"}
            )
            return jsonify({"error": "Loan creation failed"}), 500

        # Send notification
        notif_data = {
            "user_id": user_id,
            "message": f"Book '{book.get('title')}' borrowed successfully"
        }

        requests.post(
            f"{services['notifications']}/notifications",
            json=notif_data
        )

        return jsonify({
            "message": "Borrow process completed",
            "loan": loan_response.json()
        }), 200

    except requests.exceptions.RequestException:
        return jsonify({"error": "Service communication failure"}), 503


@app.route('/return_book', methods=['PUT'])
def return_book():
    data = request.json
    loan_id = data.get('loan_id')

    if not loan_id:
        return jsonify({"error": "loan_id is required"}), 400

    try:
        # Get loan
        loan_response = requests.get(
            f"{services['loans']}/loans/{loan_id}"
        )
        if not loan_response.ok:
            return jsonify({"error": "Loan not found"}), 404

        loan = loan_response.json()

        if loan.get('status') != "active":
            return jsonify({"error": "Loan is not active"}), 400

        book_id = loan.get("book_id")

        # Update loan status
        update_loan_response = requests.put(
            f"{services['loans']}/loans/{loan_id}/return"
        )

        if not update_loan_response.ok:
            return jsonify({"error": "Failed to update loan"}), 500

        # Update book status (ESB responsibility)
        update_book_response = requests.put(
            f"{services['books']}/books/{book_id}/status",
            json={"status": "available"}
        )

        if not update_book_response.ok:
            return jsonify({"error": "Failed to update book status"}), 500

        return jsonify({
            "message": "Return process completed",
            "loan": update_loan_response.json()
        }), 200

    except requests.exceptions.RequestException:
        return jsonify({"error": "Service communication failure"}), 503


if __name__ == '__main__':
    app.run(port=5000, host='0.0.0.0')