from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# Mapa de servicios
SERVICE_MAP = {
    "BooksService": "http://books:5000",
    "UsersService": "http://users:5000",
    "LoansService": "http://loans:5000",
    "NotificationsService": "http://notifications:5000"
}

# Mapa de endpoints internos
ROUTING_TABLE = {
    # Books
    "available_books": {"path": "books", "method": "GET"},
    "borrowed_books": {"path": "books", "method": "GET"},

    # Users
    "registered_users": {"path": "users", "method": "GET"},

    # Loans
    "active_loans": {"path": "loans", "method": "GET"},
    "borrow_book": {"path": "loans", "method": "POST"},
    "return_book": {"path": "loans", "method": "PUT"}
}

@app.route('/message', methods=['POST'])
def handle_message():
    message = request.json

    header = message.get("header", {})
    body = message.get("body", {})

    service = header.get("service")
    operation = header.get("operation")

    if service not in SERVICE_MAP:
        return jsonify({"error": "Unknown service"}), 400

    base_url = SERVICE_MAP[service]

    try:
        route = ROUTING_TABLE.get(operation)

        if not route:
            return jsonify({"error": "Unknown operation"}), 400

        method = route["method"]

        # Construcción base de la URL
        url = f"{base_url}/{route['path']}"

        # Special case SOLO para return_book
        if operation == "return_book":
            loan_id = body.get("loan_id")
            if not loan_id:
                return jsonify({"error": "loan_id is required"}), 400
            url = f"{base_url}/loans/{loan_id}/return"

        if method == "GET":
            response = requests.get(url)

        elif method == "POST":
            response = requests.post(url, json=body)

        elif method == "PUT":
            response = requests.put(url, json=body)

        else:
            return jsonify({"error": "Unsupported method"}), 400

        print(f"[ESB] Routing {service}.{operation} → {url}")
        return jsonify(response.json()), response.status_code

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)