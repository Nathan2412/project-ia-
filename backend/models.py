"""
Modèles SQLAlchemy pour la base de données WhatToWatch.
Définit la structure des tables et leurs relations.
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

# Instance SQLAlchemy partagée - sera initialisée dans api.py
db = SQLAlchemy()

class User(db.Model):
    """Modèle pour la table des utilisateurs."""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    password_salt = db.Column(db.String(255), nullable=False)
    preferences = db.Column(db.JSON)  # Stocke toutes les préférences dans un seul champ JSON
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<User {self.name} ({self.email})>'
    
    def to_dict(self):
        """Convertit l'utilisateur en dictionnaire pour l'API."""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'preferences': self.preferences or {},
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def update_preferences(self, new_preferences):
        """Met à jour les préférences utilisateur."""
        if self.preferences is None:
            self.preferences = {}
        
        self.preferences.update(new_preferences)
        self.updated_at = datetime.utcnow()
    
    @staticmethod
    def find_by_email(email):
        """Trouve un utilisateur par son email."""
        return User.query.filter_by(email=email).first()
    
    @staticmethod
    def find_by_name(name):
        """Trouve un utilisateur par son nom."""
        return User.query.filter_by(name=name).first()

class UserSession(db.Model):
    """Modèle pour gérer les sessions utilisateur (optionnel)."""
    
    __tablename__ = 'user_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    token_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    
    user = db.relationship('User', backref=db.backref('sessions', lazy=True))
    
    def __repr__(self):
        return f'<UserSession {self.user_id} - {self.created_at}>'
