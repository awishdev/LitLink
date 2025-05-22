from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)

    memberships = db.relationship("Membership", back_populates="user", cascade="all, delete")
    club_comments = db.relationship("ClubComment", back_populates="user", cascade="all, delete")
    meeting_comments = db.relationship("MeetingComment", back_populates="user", cascade="all, delete")


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    author = db.Column(db.String)


class Club(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String)

    memberships = db.relationship("Membership", back_populates="club", cascade="all, delete")
    meetings = db.relationship("Meeting", back_populates="club", cascade="all, delete")
    comments = db.relationship("ClubComment", back_populates="club", cascade="all, delete")


class Meeting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    location = db.Column(db.String)

    club_id = db.Column(db.Integer, db.ForeignKey('club.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'))

    club = db.relationship("Club", back_populates="meetings")
    comments = db.relationship("MeetingComment", back_populates="meeting", cascade="all, delete")


class Membership(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    club_id = db.Column(db.Integer, db.ForeignKey('club.id'))
    role = db.Column(db.String, default='member')

    user = db.relationship("User", back_populates="memberships")
    club = db.relationship("Club", back_populates="memberships")


class ClubComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    club_id = db.Column(db.Integer, db.ForeignKey('club.id'), nullable=False)

    user = db.relationship("User", back_populates="club_comments")
    club = db.relationship("Club", back_populates="comments")


class MeetingComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    meeting_id = db.Column(db.Integer, db.ForeignKey('meeting.id'), nullable=False)

    user = db.relationship("User", back_populates="meeting_comments")
    meeting = db.relationship("Meeting", back_populates="comments")
