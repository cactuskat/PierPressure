from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from models import db, Player, Game, Ship, Move
import uuid

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:password@localhost/datapierpressure"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "dev_secret_key_change_me"

db.init_app(app)

with app.app_context():
    db.create_all()


# -------------------------
# Helpers
# -------------------------
def get_current_player():
    player_id = session.get("player_id")
    if not player_id:
        return None
    return Player.query.filter_by(player_id=player_id).first()


# -------------------------
# Auth / Login Page
# -------------------------
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        username = request.form.get("username", "").strip()

        if not username:
            return jsonify({"error": "Username required"}), 400

        player = Player.query.filter_by(username=username).first()

        if not player:
            player = Player(username=username)
            db.session.add(player)
            db.session.commit()

        session["player_id"] = str(player.player_id)
        return redirect(url_for("dashboard"))

    return render_template("index.html")

# -------------------------
# Dashboard
# -------------------------
@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


# -------------------------
# API endpoints
# -------------------------
@app.route("/api/player/<int:player_id>/stats", methods=["GET"])
def get_player_stats(player_id):
    player = Player.query.get(player_id)

    if not player:
        return jsonify({"error": "Player not found"}), 404

    return jsonify(player.stats_dict())


# -------------------------
# Run app
# -------------------------
if __name__ == "__main__":
    app.run(debug=True)
