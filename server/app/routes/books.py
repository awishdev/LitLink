import os
import requests
from flask import Blueprint, request, jsonify

books_bp = Blueprint('books', __name__, url_prefix='/api/books')

GOOGLE_KEY = os.environ.get('GOOGLE_BOOKS_API_KEY')

@books_bp.route('', methods=['GET'])
def search_books():
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify({"error": "Query parameter `q` is required"}), 400

    params = {'q': q, 'maxResults': 10}
    if GOOGLE_KEY:
        params['key'] = GOOGLE_KEY

    resp = requests.get('https://www.googleapis.com/books/v1/volumes', params=params)
    if resp.status_code != 200:
        return jsonify({"error": "Google Books API failed"}), resp.status_code

    items = resp.json().get('items', [])
    simplified = []
    for item in items:
        info = item.get('volumeInfo', {})
        simplified.append({
            'id': item.get('id'),
            'title': info.get('title'),
            'authors': info.get('authors', []),
            'thumbnail': info.get('imageLinks', {}).get('thumbnail'),
            'publishedDate': info.get('publishedDate'),
            'description': info.get('description'),
        })

    return jsonify(simplified), 200
