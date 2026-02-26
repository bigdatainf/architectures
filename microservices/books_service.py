from flask import Flask, jsonify, request
import json
import os

app = Flask(__name__)

# Service-owned storage
DATA_DIR = "/data"
BOOKS_FILE = os.path.join(DATA_DIR, "books.json")

os.makedirs(DATA_DIR, exist_ok=True)


# -----------------------------
# Persistence
# -----------------------------

def load_books():
    if os.path.exists(BOOKS_FILE):
        with open(BOOKS_FILE, "r") as f:
            return json.load(f)
    else:
        initial_books = [
            {"id": 1, "title": "Don Quijote", "status": "available"},
            {"id": 2, "title": "Cien años de soledad", "status": "available"},
            {"id": 3, "title": "El principito", "status": "available"}
        ]
        save_books(initial_books)
        return initial_books


def save_books(books):
    with open(BOOKS_FILE, "w") as f:
        json.dump(books, f, indent=2)


books = load_books()


# -----------------------------
# Read Operations
# -----------------------------

@app.route('/books', methods=['GET'])
def get_books():
    global books
    books = load_books()
    return jsonify(books)


@app.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    global books
    books = load_books()
    book = next((b for b in books if b['id'] == book_id), None)

    if book:
        return jsonify(book)
    return jsonify({"error": "Book not found"}), 404


# -----------------------------
# Write Operations
# -----------------------------

@app.route('/books/<int:book_id>/status', methods=['PUT'])
def update_book_status(book_id):
    global books
    books = load_books()

    data = request.json
    book = next((b for b in books if b['id'] == book_id), None)

    if not book:
        return jsonify({"error": "Book not found"}), 404

    book['status'] = data.get('status', book['status'])

    save_books(books)

    return jsonify(book), 200


if __name__ == '__main__':
    app.run(port=5000, host='0.0.0.0')