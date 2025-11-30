from flask import Blueprint, request, jsonify
from models import db
from models.gamemode import GameMode
from models.battle import Battle

gamemode_bp = Blueprint('gamemode_bp', __name__)

@gamemode_bp.route("/gamemodes", methods=["GET"])
def get_gamemodes():
    modes = GameMode.query.all()
    return jsonify([m.to_dict() for m in modes])


@gamemode_bp.route("/gamemodes/<int:mode_id>/battles", methods=["GET"])
def get_battles_for_mode(mode_id):
    mode = GameMode.query.get(mode_id)
    if not mode:
        return jsonify({"error": "Nie znaleziono trybu gry"}), 404

    battles = Battle.query.filter_by(game_mode_id=mode_id).all()
    return jsonify([b.to_dict() for b in battles]), 200


@gamemode_bp.route("/gamemodes", methods=["POST"])
def add_gamemode():
    data = request.get_json()
    new_mode = GameMode(name=data["name"], description=data.get("description"))
    db.session.add(new_mode)
    db.session.commit()
    return jsonify({"message": "Dodano tryb gry!", "gamemode": new_mode.to_dict()})

@gamemode_bp.route("/gamemodes/<int:id>", methods=["DELETE"])
def delete_gamemode(id):
    mode = GameMode.query.get(id)
    if not mode:
        return jsonify({"error": "Nie znaleziono trybu gry"}), 404
    db.session.delete(mode)
    db.session.commit()
    return jsonify({"message": f"Tryb '{mode.name}' został usunięty."})
