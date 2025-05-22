from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import db, Club

clubs_bp = Blueprint('clubs', __name__)

@clubs_bp.route('/clubs', methods=['GET'])
def list_clubs():
    q = request.args.get('search')
    query = Club.query

    if q:
        query = query.filter(Club.name.ilike(f'%{q}%'))

    clubs = query.all()
    return jsonify([club.serialize() for club in clubs]), 200


@clubs_bp.route('/clubs', methods=['POST'])
@jwt_required
def create_club():
    data = request.get_json()
    club = Club(name=data['name'], description=data.get['description'])
    db.session.add(club)
    db.session.commit()
    return jsonify(club.serialize()), 201


@clubs_bp.route('/clubs/<int:club_id>', methods=['GET'])
def get_club(club_id):
    club = Club.query.get_or_404(club_id)
    return jsonify(club.serialize()), 200

@clubs_bp.route('/clubs/<int:club_id>', methods=['PATCH'])
@jwt_required
def update_club(club_id):
    club = Club.query.get_or_404(club_id)
    data = request.get_json()
    club.name = data.get('name', club.name)
    club.description = data.get('description', club.description)
    db.session.commit()
    return jsonify(club.serialize()), 200


@clubs_bp.route('/clubs/<int:club_id>', methods=['DELETE'])
@jwt_required
def delete_club(club_id):
    club = Club.query.get_or_404(club_id)
    db.session.delete(club)
    db.session.commit()
    return 'deleted', 204



