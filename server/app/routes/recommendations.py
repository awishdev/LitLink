import os
import requests
from flask import Blueprint, request, jsonify, abort

rec_bp = Blueprint('recommendations', __name__,
                   url_prefix='/api/recommendations')

@rec_bp.route('', methods=['GET'])
def get_recs():
    title = request.args.get('title')
    if not title:
        return jsonify({'message': 'Missing query param: title'}), 400

    # load from environment
    key = os.getenv('TASTEDIVE_API_KEY')
    if not key:
        # fail early if someone forgot to set it
        abort(500, description="TASTEDIVE_KEY not configured")

    res = requests.get(
        'https://tastedive.com/api/similar',
        params={
            'q':       title,
            'type':    'books',
            'limit':   5,
            'k':       key
        },
        timeout=3
    )

    # if upstream failed, bubble the status
    if res.status_code != 200:
        return jsonify({'message': 'Tastedive error'}), res.status_code

    data = res.json().get('Similar', {}).get('Results', [])
    return jsonify(data), 200
