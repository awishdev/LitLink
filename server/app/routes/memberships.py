from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import db, Club, Membership

memberships_bp = Blueprint('memberships', __name__, url_prefix='/clubs/<int:club_id>/memberships')

@memberships_bp.route('', methods=['GET'])
@jwt_required
def join_club(club_id):
    user_id = get_jwt_identity()
    if Membership.query.filter_by(user_id=user_id, club_id=club_id).first():
        return jsonify({'message': 'Already a member of this club'}), 400
    
    m = Membership(user_id=user_id, club_id=club_id)
    db.session.add(m)
    db.session.commit()
    return jsonify(m.serialize()), 201


@memberships_bp.route('/<int:membership_id>', methods=['DELETE'])
@jwt_required
def leave_club(club_id, membership_id):
    m = Membership.query.get_or_404(membership_id)
    if m.user_id != get_jwt_identity() or m.club_id != club_id:
        return jsonify({'message': 'You cannot leave this club'}), 403
    db.session.delete(m)
    db.session.commit()
    return 'deleted', 204

@memberships_bp.route('/<int:membership_id>', methods=['PATCH'])
@jwt_required
def update_role(club_id, membership_id):
    m = Membership.query.get_or_404(membership_id)
    if m.user_id != get_jwt_identity() or m.club_id != club_id:
        return jsonify({'message': 'You cannot update this club membership'}), 403
    
    data = request.get_json()
    m.role = data.get('role', m.role)
    db.session.commit()
    return jsonify(m.serialize()), 200