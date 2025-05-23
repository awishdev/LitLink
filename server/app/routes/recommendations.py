import requests
from flask import Blueprint, request, jsonify

rec_bp = Blueprint('recommendations', __name__, url_prefix='/api/recommendations')
TASTEDIVE_KEY = '1051087-LitLink-1E72946C'

@rec_bp.route('', methods=['GET'])
def get_recs():
    tite = request.args.get('title')
    res = requests.get(
        'https://tastedive.com/api/similar',
        params={'q': title, 'type':'books', 'limit': 5,'k': TASTEDIVE_KEY}
    )
    data = res.json().get('Similar', {}).get('Results', [])
    return jsonify(data), res.status_code