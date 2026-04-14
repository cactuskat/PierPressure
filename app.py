from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import JSON
import random

app = Flask(__name__)

# --- CONFIGURATION ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:yourpassword@localhost:3306/battleship'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- MODELS ---
class Game(db.Model):
    __tablename__ = 'battleship_games'
    id = db.Column(db.Integer, primary_key=True)
    player1_ships = db.Column(JSON)  # List of ship positions, e.g., [4, 10, 22]
    player2_ships = db.Column(JSON)
    player1_hits = db.Column(JSON)   # List of coordinates P1 has fired at
    player2_hits = db.Column(JSON)   # List of coordinates P2 has fired at
    current_turn = db.Column(db.Integer, default=1)
    winner = db.Column(db.Integer, nullable=True)

# Create the tables in MySQL automatically
with app.app_context():
    db.create_all()

# --- ROUTES ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/start', methods=['POST'])
def start_game():
    """Initializes a 5x5 game with 3 ships for each player."""
    # Randomly select 3 unique positions from 0-24 for each player
    p1_ships = random.sample(range(25), 3)
    p2_ships = random.sample(range(25), 3)
    
    new_game = Game(
        player1_ships=p1_ships,
        player2_ships=p2_ships,
        player1_hits=[],
        player2_hits=[],
        current_turn=1
    )
    
    db.session.add(new_game)
    db.session.commit()
    
    return jsonify({
        "game_id": new_game.id,
        "message": "Game started! Board size: 5x5. Ships placed: 3."
    }), 201

@app.route('/api/move', methods=['POST'])
def make_move():
    """Handles turn rotation and hit/miss logic."""
    data = request.get_json()
    game_id = data.get('game_id')
    player_num = int(data.get('player'))  # Who is firing? 1 or 2
    shot = int(data.get('shot'))          # Position 0-24

    game = Game.query.get(game_id)
    if not game:
        return jsonify({"error": "Game not found"}), 404
    
    if game.winner:
        return jsonify({"error": f"Game over. Player {game.winner} won."}), 400
    
    if game.current_turn != player_num:
        return jsonify({"error": "Not your turn!"}), 403

    # Process the shot
    is_hit = False
    if player_num == 1:
        # Check if they hit Player 2's ships
        if shot in game.player2_ships:
            is_hit = True
        
        # Update hits (must re-assign list for SQLAlchemy to detect JSON change)
        new_hits = list(game.player1_hits)
        if shot not in new_hits:
            new_hits.append(shot)
        game.player1_hits = new_hits
        
        # Check Win Condition
        if all(s in game.player1_hits for s in game.player2_ships):
            game.winner = 1
        
        game.current_turn = 2
        
    else: # Player 2 firing
        if shot in game.player1_ships:
            is_hit = True
            
        new_hits = list(game.player2_hits)
        if shot not in new_hits:
            new_hits.append(shot)
        game.player2_hits = new_hits
        
        if all(s in game.player2_hits for s in game.player1_ships):
            game.winner = 2
            
        game.current_turn = 1

    db.session.commit()
    
    return jsonify({
        "hit": is_hit,
        "winner": game.winner,
        "next_turn": game.current_turn,
        "result": "HIT!" if is_hit else "MISS"
    }), 200

if __name__ == '__main__':
    app.run(debug=True)
