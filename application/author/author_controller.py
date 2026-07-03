from flask import request, jsonify
from application import app, author_service, book_service
from application.author.author_service import AuthorFilters


@app.route('/api/authors', methods=['POST'])
def create_author():
    request_data = request.json
    author_dict, errors = author_service.create_author(request_data)
    if errors:
        return jsonify({'error': 'VALIDATION_ERROR', 'message': 'Invalid input', 'details': errors}), 400
    return jsonify(author_dict), 201


@app.route('/api/authors/<author_id>', methods=['GET'])
def get_author(author_id):
    author_dict = author_service.get_author(author_id)
    if author_dict is None:
        return jsonify({'error': 'NOT_FOUND', 'message': f'Author not found: {author_id}'}), 404
    return jsonify(author_dict), 200

@app.route('/api/authors', methods=['GET'])
def get_authors():
    page = request.args.get('page')
    size = request.args.get('size')
    search = request.args.get('search')

    try:
        page = int(page) if page is not None else 1
        size = int(size) if size is not None else 20
        if page < 1:
            return jsonify({'error': 'VALIDATION_ERROR', 'message': 'page must be >= 1'}), 400
        if not (1 <= size <= 100):
            return jsonify({'error': 'VALIDATION_ERROR', 'message': 'size must be 1-100'}), 400
    except ValueError:
        return jsonify({'error': 'VALIDATION_ERROR', 'message': 'page and size must be integers'}), 400

    authors_page = author_service.get_authors(AuthorFilters(search), page, size)
    return jsonify(authors_page.to_json()), 200

@app.route('/api/authors/<author_id>', methods=['PUT'])
def update_author(author_id):
    request_data = request.json
    author_dict, errors = author_service.update_author(author_id, request_data)
    if author_dict is None and errors is None:
        return jsonify({'error': 'NOT_FOUND', 'message': f'Author not found: {author_id}'}), 404
    if errors:
        return jsonify({'error': 'VALIDATION_ERROR', 'message': 'Invalid input', 'details': errors}), 400
    return jsonify(author_dict), 200


@app.route('/api/authors/<author_id>', methods=['DELETE'])
def delete_author(author_id):
    books = book_service.books_by_author(author_id)
    if books:
        return jsonify({'error': 'CONFLICT','message': f'Cannot delete because author has {len(books)} books'}), 409

    deleted = author_service.delete_author(author_id)
    if not deleted:
        return jsonify({'error': 'NOT_FOUND', 'message': f'Author not found: {author_id}'}), 404
    return '', 204