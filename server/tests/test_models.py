import pytest
import os
from app.models import User, Club, Membership, ClubComment

def test_user_membership_relationship(db):
    # create a user and a club
    user = User(username='alice')
    club = Club(name='SciFi Club', description='We read Sci-Fi')
    db.session.add_all([user, club])
    db.session.commit()

    # add a membership
    m = Membership(user_id=user.id, club_id=club.id, role='member')
    db.session.add(m)
    db.session.commit()

    # relationship access
    assert user.memberships[0].club == club
    assert club.memberships[0].user == user

def test_club_comment_model(db):
    user = User(username='bob')
    club = Club(name='History Club', description='All about history')
    db.session.add_all([user, club])
    db.session.commit()

    comment = ClubComment(user_id=user.id, club_id=club.id, content='Great club!')
    db.session.add(comment)
    db.session.commit()

    # ensure backrefs work
    assert club.comments[0].user == user
    assert user.club_comments[0].club == club
    assert comment.timestamp is not None
