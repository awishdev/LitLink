from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from ..models import db, Club

clubs_bp = Blueprint('clubs', __name__, url_prefix='/api/clubs')

@clubs_bp.route('', methods=['GET'])
def list_clubs():
    q = request.args.get('search', '')
    query = Club.query

    if q:
        query = query.filter(Club.name.ilike(f'%{q}%'))

    clubs = query.all()
    return jsonify([club.serialize() for club in clubs]), 200


@clubs_bp.route('', methods=['POST'])
def create_club():
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return jsonify({"msg": "Missing Authorization Header"}), 401

    data = request.get_json() or {}
    if not data.get('name'):
        return jsonify({"msg": "Name required"}), 400

    club = Club(name=data['name'], description=data.get('description'))
    db.session.add(club)
    db.session.commit()
    return jsonify(club.serialize()), 201


@clubs_bp.route('/<int:club_id>', methods=['GET'])
def get_club(club_id):
    club = Club.query.get_or_404(club_id)
    return jsonify(club.serialize()), 200

@clubs_bp.route('/<int:club_id>', methods=['PATCH'], endpoint='update_club')
@jwt_required
def update_club(club_id):
    club = Club.query.get_or_404(club_id)
    data = request.get_json()
    club.name = data.get('name', club.name)
    club.description = data.get('description', club.description)
    db.session.commit()
    return jsonify(club.serialize()), 200


@clubs_bp.route('/<int:club_id>', methods=['DELETE'], endpoint='delete_club')
@jwt_required
def delete_club(club_id):
    club = Club.query.get_or_404(club_id)
    db.session.delete(club)
    db.session.commit()
    return 'deleted', 204



