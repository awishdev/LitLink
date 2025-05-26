# server/app/routes/meetings.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from ..models import db, Club, Meeting

meetings_bp = Blueprint('meetings', __name__, url_prefix='/api')

# List all meetings for a club
@meetings_bp.route('/clubs/<int:club_id>/meetings', methods=['GET'])
def list_meetings(club_id):
    # ensure club exists
    Club.query.get_or_404(club_id)
    meetings = Meeting.query.filter_by(club_id=club_id).all()
    return jsonify([m.serialize() for m in meetings]), 200

# Schedule a new meeting
@meetings_bp.route('/clubs/<int:club_id>/meetings', methods=['POST'])
def create_meeting(club_id):
    verify_jwt_in_request()
    data = request.get_json() or {}
    date = data.get('date')
    location = data.get('location')
    book_id = data.get('book_id')
    if not date or not location or book_id is None:
        return jsonify({'message': 'date, location, and book_id are required'}), 400
    # ensure club exists
    Club.query.get_or_404(club_id)
    m = Meeting(club_id=club_id, date=date, location=location, book_id=book_id)
    db.session.add(m)
    db.session.commit()
    return jsonify(m.serialize()), 201

# Get details for a single meeting
@meetings_bp.route('/meetings/<int:meeting_id>', methods=['GET'])
def get_meeting(meeting_id):
    m = Meeting.query.get_or_404(meeting_id)
    return jsonify(m.serialize()), 200

# Update meeting details
@meetings_bp.route('/meetings/<int:meeting_id>', methods=['PATCH'])
def update_meeting(meeting_id):
    verify_jwt_in_request()
    m = Meeting.query.get_or_404(meeting_id)
    data = request.get_json() or {}
    if 'date' in data:
        m.date = data['date']
    if 'location' in data:
        m.location = data['location']
    if 'book_id' in data:
        m.book_id = data['book_id']
    db.session.commit()
    return jsonify(m.serialize()), 200

# Cancel (delete) a meeting
@meetings_bp.route('/meetings/<int:meeting_id>', methods=['DELETE'])
def delete_meeting(meeting_id):
    verify_jwt_in_request()
    m = Meeting.query.get_or_404(meeting_id)
    db.session.delete(m)
    db.session.commit()
    return '', 204
