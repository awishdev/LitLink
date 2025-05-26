# app/routes/club_comments.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import db, Club, ClubComment

club_comments_bp = Blueprint(
    'club_comments', __name__,
    url_prefix='/api/clubs/<int:club_id>/comments'
)

@club_comments_bp.route('', methods=['GET'])
def list_comments(club_id):
    club = Club.query.get_or_404(club_id)
    return jsonify([c.serialize() for c in club.comments]), 200

@club_comments_bp.route('', methods=['POST'])
@jwt_required()
def post_comment(club_id):
    data = request.get_json() or {}
    if 'content' not in data:
        return jsonify({"msg": "Missing content"}), 400

    # ensure the club exists
    Club.query.get_or_404(club_id)

    c = ClubComment(
        club_id=club_id,
        user_id=get_jwt_identity(),
        content=data['content']
    )
    db.session.add(c)
    db.session.commit()
    return jsonify(c.serialize()), 201

@club_comments_bp.route('/<int:comment_id>', methods=['PATCH'])
@jwt_required()
def edit_comment(club_id, comment_id):
    user_id = get_jwt_identity()
    c = ClubComment.query.get_or_404(comment_id)
    if c.user_id != user_id or c.club_id != club_id:
        return jsonify({"msg": "Forbidden"}), 403

    data = request.get_json() or {}
    c.content = data.get('content', c.content)
    db.session.commit()
    return jsonify(c.serialize()), 200

@club_comments_bp.route('/<int:comment_id>', methods=['DELETE'])
@jwt_required()
def delete_comment(club_id, comment_id):
    user_id = get_jwt_identity()
    c = ClubComment.query.get_or_404(comment_id)
    if c.user_id != user_id or c.club_id != club_id:
        return jsonify({"msg": "Forbidden"}), 403

    db.session.delete(c)
    db.session.commit()
    return '', 204
