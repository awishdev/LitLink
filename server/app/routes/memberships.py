from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from ..models import db, Club, Membership


memberships_bp = Blueprint('memberships', __name__, url_prefix='/api/clubs/<int:club_id>/memberships')

@memberships_bp.route('', methods=['GET'])
def list_members(club_id):
    Club.query.get_or_404(club_id)
    members = Membership.query.filter_by(club_id=club_id).all()
    # return user info, not just membership rows
    return jsonify([
        {
            'id': m.id,
            'user': {'id': m.user.id, 'username': m.user.username},
            'role': m.role
        }
        for m in members
    ]), 200

@memberships_bp.route('', methods=['POST'])
def join_club(club_id):
    verify_jwt_in_request()
    user_id = get_jwt_identity()
    Club.query.get_or_404(club_id)
    if Membership.query.filter_by(user_id=user_id, club_id=club_id).first():
        return jsonify({'message': 'Already a member'}), 400

    m = Membership(user_id=user_id, club_id=club_id, role='member')
    db.session.add(m)
    db.session.commit()
    return jsonify({
        'id': m.id,
        'user_id': m.user_id,
        'club_id': m.club_id,
        'role': m.role
    }), 201


@memberships_bp.route('/<int:membership_id>', methods=['DELETE'], endpoint='leave_club')
def leave_club(club_id, membership_id):
    verify_jwt_in_request()
    m = Membership.query.get_or_404(membership_id)
    if m.user_id != get_jwt_identity() or m.club_id != club_id:
        return jsonify({'message': 'You cannot leave this club'}), 403
    db.session.delete(m)
    db.session.commit()
    return 'deleted', 204

@memberships_bp.route('/<int:membership_id>', methods=['PATCH'], endpoint='update_membership_role')
def update_role(club_id, membership_id):
    verify_jwt_in_request()
    m = Membership.query.get_or_404(membership_id)
    if m.user_id != get_jwt_identity() or m.club_id != club_id:
        return jsonify({'message': 'You cannot update this club membership'}), 403
    
    data = request.get_json()
    m.role = data.get('role', m.role)
    db.session.commit()
    return jsonify(m.serialize()), 200