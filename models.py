from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from flask import jsonify

db = SQLAlchemy()

class Player(db.Model):
    __tablename__ = 'players'
    
    # Native UUID handling
    player_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = db.Column(db.String(80), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())
    
    # Stats
    games_played = db.Column(db.Integer, default=0)
    total_wins = db.Column(db.Integer, default=0)
    total_losses = db.Column(db.Integer, default=0)
    total_moves = db.Column(db.Integer, default=0)
    total_shots = db.Column(db.Integer, default=0)
    total_hits = db.Column(db.Integer, default=0)

    matchs = db.relationship('GamePlayer', backref='player', lazy=True)
    ships = db.relationship('Ship', backref='player', lazy=True)
    moves = db.relationship('Move', backref='player', lazy=True)

    @property
    def accuracy(self):
        """Computed at read time — avoids storing a derived value."""
        if self.total_shots == 0:
            return 0.0
        return round(self.total_hits / self.total_shots, 4)
 
    def stats_dict(self):
        """Serializes the shape expected by GET /api/players/{id}/stats."""
        return {
            "games_played": self.games_played,
            "wins": self.total_wins,
            "losses": self.total_losses,
            "total_shots": self.total_shots,
            "total_hits": self.total_hits,
            "accuracy": self.accuracy,
        }

class GamePlayer(db.Model):
    __tablename__ = 'game_player'
    
    game_id = db.Column(UUID(as_uuid=True), db.ForeignKey('game.game_id'), primary_key=True)
    player_id = db.Column(UUID(as_uuid=True), db.ForeignKey('players.player_id'), primary_key=True)
    turn_order = db.Column(db.Integer, nullable=False, default=0)

    joined_at = db.Column(db.DateTime, default=datetime.now())
    is_eliminated = db.Column(db.Boolean, default=False)

class Game(db.Model):
    __tablename__ = 'game'

    game_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = db.Column(db.String(4), unique=True, nullable=False)
    creator_id = db.Column(UUID(as_uuid=True),db.ForeignKey('players.player_id'),nullable=False)
    grid_size = db.Column(db.Integer, nullable=False, default=5)
    max_players = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    game_status = db.Column(db.String(20), nullable=False, default='waiting') #'waiting','active', or 'finished'
    current_turn_index = db.Column(db.Integer, default=0)
    active_players = db.Column(db.Integer, default=0)

    winner_id = db.Column(UUID(as_uuid=True),db.ForeignKey('players.player_id'),nullable=True,default=None)
   
    matches = db.relationship('GamePlayer', backref='game', lazy=True)
    ships = db.relationship('Ship', backref='game', lazy=True)
    moves = db.relationship('Move', backref='game', lazy=True, order_by='Move.created_at')

    def to_dict(self):
        """Serializes the shape expected by GET /api/games/{id}."""
        return {
            "game_id": str(self.game_id),
            "grid_size": self.grid_size,
            "status": self.status,
            "current_turn_index": self.current_turn_index,
            "active_players": self.active_players,
        }
    
class Ship(db.Model):
    """
    NEW model — required by POST /api/games/{id}/place.
 
    Each player places exactly 3 single-cell ships per game.
    One row per ship cell, so each player will have exactly 3 rows
    in this table for a given game.
    """
    __tablename__ = 'ships'
 
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
 
    game_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey('game.game_id'),
        nullable=False
    )
    player_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey('players.player_id'),
        nullable=False
    )
 
    row = db.Column(db.Integer, nullable=False)
    col = db.Column(db.Integer, nullable=False)
 
    # True once this cell has been hit by an opponent
    is_hit = db.Column(db.Boolean, default=False)
 
    placed_at = db.Column(db.DateTime, default=datetime.now)
 
    # Prevent duplicate coordinates within the same game
    __table_args__ = (
        db.UniqueConstraint('game_id', 'player_id', 'row', 'col',
                            name='uq_ship_position'),
    )
 
    def to_dict(self):
        return {
            "row": self.row,
            "col": self.col,
            "is_hit": self.is_hit,
        }
 
 
class Move(db.Model):
    """
    Records every shot fired, in chronological order.
    """
    __tablename__ = 'moves'
 
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
 
    game_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey('game.game_id'),
        nullable=False
    )
    player_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey('players.player_id'),
        nullable=False
    )
 
    row = db.Column(db.Integer, nullable=False)
    col = db.Column(db.Integer, nullable=False)
 
    # 'hit' or 'miss'
    hit = db.Column(db.Boolean, default=False)
 
    created_at = db.Column(db.DateTime, default=datetime.now)
 
    def to_dict(self):
        """Serializes a single move for GET /api/games/{id}/moves."""
        return {
            "player_id": str(self.player_id),
            "row": self.row,
            "col": self.col,
            "result": "hit" if self.hit else "miss",
            "timestamp": self.created_at.isoformat(),
        }