from flask import request, jsonify
from application import app, book_service, author_service
from application.book.book_service import BookFilters

SORT_FIELDS = {'title', 'publishedYear'}

@app.route('/api/books', methods=['POST'])
def create_book():
    request_data = request.json
    book, errors = book_service.create_book(request_data, author_service)
    if errors:
        return jsonify({'error': 'VALIDATION_ERROR', 'message': 'Invalid input', 'details': errors}), 400
    return jsonify(book_service.book_mapper.map_to_dict(book)), 201

@app.route('/api/books', methods=['GET'])
def get_books():
    page = request.args.get('page')
    size = request.args.get('size')
    genre = request.args.get('genre')
    status = request.args.get('status')
    author_id = request.args.get('authorId')
    year_from = request.args.get('publishedYearFrom')
    year_to = request.args.get('publishedYearTo')
    sort = request.args.get('sort', 'title')
    order = request.args.get('order', 'asc')

    try:
        page = int(page) if page is not None else 1
        size = int(size) if size is not None else 20
        if page < 1:
            return jsonify({'error': 'VALIDATION_ERROR', 'message': 'page must be >= 1'}), 400
        if not (1 <= size <= 100):
            return jsonify({'error': 'VALIDATION_ERROR', 'message': 'size must be between 1 and 100'}), 400
    except ValueError:
        return jsonify({'error': 'VALIDATION_ERROR', 'message': 'page and size must be integers'}), 400

    try:
        if year_from is not None:
            yf = int(year_from)
        if year_to is not None:
            yt = int(year_to)
        if yf is not None and yt is not None and yf > yt:
            return jsonify({'error': 'VALIDATION_ERROR', 'message': 'publishedYearFrom must be <= publishedYearTo'}), 400
    except ValueError:
        return jsonify({'error': 'VALIDATION_ERROR', 'message': 'year filters must be integers'}), 400

    if sort not in SORT_FIELDS:
        return jsonify({'error': 'VALIDATION_ERROR', 'message': f'sort must be one of: {", ".join(sorted(SORT_FIELDS))}'}), 400
    if order not in ('asc', 'desc'):
        return jsonify({'error': 'VALIDATION_ERROR', 'message': "order must be 'asc' or 'desc'"}), 400

    books = book_service.get_books(BookFilters(genre, status, author_id, yf, yt), page, size, sort, order)
    return jsonify(books.to_json()), 200

@app.route('/api/books/<book_id>', methods=['GET'])
def get_book(book_id):
    book = book_service.get_book(book_id)
    if book is None:
        return jsonify({'error': 'NOT_FOUND', 'message': f'Book not found: {book_id}'}), 404
    return jsonify(book_service.book_mapper.map_to_dict(book)), 200

@app.route('/api/books/<book_id>', methods=['PUT'])
def update_book(book_id):
    request_data = request.json
    book, errors = book_service.update_book(book_id, request_data, author_service)
    if book is None and errors is None:
        return jsonify({'error': 'NOT_FOUND', 'message': f'Book not found: {book_id}'}), 404
    if errors:
        return jsonify({'error': 'VALIDATION_ERROR', 'message': 'Invalid input', 'details': errors}), 400
    return jsonify(book_service.book_mapper.map_to_dict(book)), 200

@app.route('/api/books/<book_id>', methods=['DELETE'])
def delete_book(book_id):
    deleted = book_service.delete_book(book_id)
    if not deleted:
        return jsonify({'error': 'NOT_FOUND', 'message': f'Book not found: {book_id}'}), 404
    return '', 204