# app/routes/meeting_comments.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import db, Meeting, MeetingComment

meeting_comments_bp = Blueprint(
    'meeting_comments', __name__,
    url_prefix='/api/meetings/<int:meeting_id>/comments'
)

@meeting_comments_bp.route('', methods=['GET'])
def list_comments(meeting_id):
    # 404 if the meeting doesn't exist
    Meeting.query.get_or_404(meeting_id)
    comments = MeetingComment.query.filter_by(meeting_id=meeting_id).all()
    return jsonify([c.serialize() for c in comments]), 200

@meeting_comments_bp.route('', methods=['POST'])
@jwt_required()   # use () for consistency
def post_comment(meeting_id):
    data = request.get_json() or {}
    if 'content' not in data:
        return jsonify({"msg": "Missing content"}), 400

    # 404 if the meeting doesn't exist
    Meeting.query.get_or_404(meeting_id)

    c = MeetingComment(
        meeting_id=meeting_id,
        user_id=get_jwt_identity(),
        content=data['content']
    )
    db.session.add(c)
    db.session.commit()
    return jsonify(c.serialize()), 201

@meeting_comments_bp.route('/<int:comment_id>', methods=['PATCH'])
@jwt_required()
def edit_comment(meeting_id, comment_id):
    user_id = get_jwt_identity()
    c = MeetingComment.query.get_or_404(comment_id)

    # enforce both ownership and correct parent meeting
    if c.user_id != user_id or c.meeting_id != meeting_id:
        return jsonify({"msg": "Forbidden"}), 403

    data = request.get_json() or {}
    if 'content' in data:
        c.content = data['content']
        db.session.commit()

    return jsonify(c.serialize()), 200

@meeting_comments_bp.route('/<int:comment_id>', methods=['DELETE'])
@jwt_required()
def delete_comment(meeting_id, comment_id):
    user_id = get_jwt_identity()
    c = MeetingComment.query.get_or_404(comment_id)

    # enforce both ownership and correct parent meeting
    if c.user_id != user_id or c.meeting_id != meeting_id:
        return jsonify({"msg": "Forbidden"}), 403

    db.session.delete(c)
    db.session.commit()
    return '', 204
