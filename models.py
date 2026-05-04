from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    # Relationship (optional but good)
    opportunities = db.relationship('Opportunity', backref='creator', lazy=True)


class Opportunity(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # 🔹 BASIC
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)

    # 🔹 REQUIRED BY ASSIGNMENT
    duration = db.Column(db.String(50))
    start_date = db.Column(db.String(50))
    skills = db.Column(db.String(200))
    category = db.Column(db.String(50))
    future_opportunities = db.Column(db.String(200))
    max_applicants = db.Column(db.Integer)

    # 🔹 FOREIGN KEY
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False)