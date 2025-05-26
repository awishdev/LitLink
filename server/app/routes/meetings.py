from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from ..models import db, Club, Meeting
from datetime import datetime

meetings_bp = Blueprint('meetings', __name__, url_prefix='/api')

@meetings_bp.route('/clubs/<int:club_id>/meetings', methods=['GET'])
def list_meetings(club_id):
    club = Club.query.get_or_404(club_id)
    return jsonify([m.serialize() for m in club.meetings]), 200

@meetings_bp.route('/clubs/<int:club_id>/meetings', methods=['POST'])
@jwt_required()
def create_meeting(club_id):
    # ensure club exists
    Club.query.get_or_404(club_id)

    data = request.get_json() or {}

    # required fields
    if 'date' not in data:
        return jsonify({'message': 'Missing required field: date'}), 400
    if 'location' not in data:
        return jsonify({'message': 'Missing required field: location'}), 400

    # parse date
    try:
        dt = datetime.fromisoformat(data['date'])
    except ValueError:
        return jsonify({'message': 'Invalid date format for field: date'}), 400

    m = Meeting(
        club_id=club_id,
        date=dt,
        location=data['location'],
        book_id=data.get('book_id')  # optional
    )
    db.session.add(m)
    db.session.commit()
    return jsonify(m.serialize()), 201

@meetings_bp.route('/meetings/<int:meeting_id>', methods=['GET'])
def get_meeting(meeting_id):
    m = Meeting.query.get_or_404(meeting_id)
    return jsonify(m.serialize()), 200

@meetings_bp.route('/meetings/<int:meeting_id>', methods=['PATCH'])
@jwt_required()
def update_meeting(meeting_id):
    m = Meeting.query.get_or_404(meeting_id)
    data = request.get_json() or {}

    if 'date' in data:
        try:
            m.date = datetime.fromisoformat(data['date'])
        except ValueError:
            return jsonify({'message': 'Invalid date format for field: date'}), 400

    if 'location' in data:
        m.location = data['location']

    db.session.commit()
    return jsonify(m.serialize()), 200

@meetings_bp.route('/meetings/<int:meeting_id>', methods=['DELETE'])
@jwt_required()
def delete_meeting(meeting_id):
    m = Meeting.query.get_or_404(meeting_id)
    db.session.delete(m)
    db.session.commit()
    return '', 204
