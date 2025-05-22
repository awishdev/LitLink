from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import db, Club, Meeting

meetings_bp = Blueprint('meetings', __name__, url_prefix='/api')

@meetings_bp.route('/clubs/<int:club_id>/meetings', methods=['GET'])
def list_meetings(club_id):
    club = Club.query.get_or_404(club_id)
    return jsonify([m.serialize() for m in club.meetings]), 200

@meetings_bp.route('/clubs/<int:club_id>/meetings', methods=['POST'])
@jwt_required
def create_meeting(club_id):
    data = request.get_json()
    m = Meeting(club_id=club_id, date=data.get['date'], location=data['location'], book_id=data.get('book_id'))
    db.session.add(m)
    db.session.commit()
    return jsonify(m.serialize()), 201

@meetings_bp.route('/meetings/<int:meeting_id>', methods=['PATCH'])
@jwt_required
def update_meeting(meeting_id):
    m = Meeting.query.get_or_404(meeting_id)
    data = request.get_json()
    m.date = data.get('date', m.date)
    m.location = data.get('location', m.location)
    db.session.commit()
    return jsonify(m.serialize()), 200

@meetings_bp.route('/meetings/<int:meeting_id>', methods=['DELETE'])
@jwt_required
def delete_meeting(meeting_id):
    m = Meeting.query.get_or_404(meeting_id)
    db.session.delete(m)
    db.session.commit()
    return 'deleted', 204
    