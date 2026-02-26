# books_service.py
from flask import Flask, jsonify, request

app = Flask(__name__)

books = [
    {"id": 1, "title": "Don Quijote", "status": "available"},
    {"id": 2, "title": "Cien años de soledad", "status": "available"},
    {"id": 3, "title": "El principito", "status": "available"}
]

@app.route('/books', methods=['GET'])
def get_books():
    return jsonify(books)

@app.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    book = next((b for b in books if b['id'] == book_id), None)
    if book:
        return jsonify(book)
    return '', 404

@app.route('/books/<int:book_id>/status', methods=['PUT'])
def update_book_status(book_id):
    data = request.json
    book = next((b for b in books if b['id'] == book_id), None)
    
    if not book:
        return jsonify({"error": "Book not found"}), 404
    
    book['status'] = data.get('status', book['status'])
    return jsonify(book), 200

if __name__ == '__main__':
    app.run(port=5000, host='0.0.0.0')