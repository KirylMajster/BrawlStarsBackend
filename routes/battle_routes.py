from flask import Blueprint, request, jsonify
from models import db
from models.battle import Battle
from datetime import datetime
from models.battle_participant import BattleParticipant

battle_bp = Blueprint('battle_bp', __name__)

participants = db.relationship('BattleParticipant', backref='battle', lazy=True, passive_deletes=True)


# GET – wszystkie bitwy
@battle_bp.route("/battles", methods=["GET"])
def get_battles():
    battles = Battle.query.all()
    return jsonify([b.to_dict() for b in battles])

# POST – dodanie jednej lub wielu bitew
@battle_bp.route("/battles", methods=["POST"])
def add_battle():
    data = request.get_json()

    def build_kwargs(payload):
        kwargs = {
            "game_mode_id": payload.get("game_mode_id"),
            "map_name": payload["map_name"],
            "result": payload.get("result"),
            "duration": payload.get("duration"),
        }
        # jeśli date jest podane i niepuste — sparsuj ISO "YYYY-MM-DD" na date
        date_str = payload.get("date")
        if date_str:
            kwargs["date"] = datetime.strptime(date_str, "%Y-%m-%d").date()
        # jeśli date nie ma — NIE dodajemy kwargs["date"] -> zadziała default
        return kwargs

    if isinstance(data, list):
        battles = []
        for item in data:
            new_battle = Battle(**build_kwargs(item))
            db.session.add(new_battle)
            battles.append(new_battle)
        db.session.commit()
        return jsonify({
            "message": f"Dodano {len(battles)} bitew!",
            "battles": [b.to_dict() for b in battles]
        }), 201
    else:
        new_battle = Battle(**build_kwargs(data))
        db.session.add(new_battle)
        db.session.commit()
        return jsonify({
            "message": "Dodano bitwę!",
            "battle": new_battle.to_dict()
        }), 201

# DELETE – usuń bitwę
@battle_bp.route("/battles/<int:id>", methods=["DELETE"])
def delete_battle(id):
    battle = Battle.query.get(id)
    if not battle:
        return jsonify({"error": "Nie znaleziono bitwy"}), 404
    db.session.delete(battle)
    db.session.commit()
    return jsonify({"message": f"Bitwa {id} została usunięta."})


@battle_bp.route("/battles/<int:battle_id>", methods=["GET"])
def get_battle(battle_id):
    battle = Battle.query.get(battle_id)
    if not battle:
        return jsonify({"error": "Nie znaleziono bitwy"}), 404

    data = battle.to_dict()

    # dołącz uczestników
    parts = BattleParticipant.query.filter_by(battle_id=battle_id).all()
    data["participants"] = [p.to_dict() for p in parts]

    return jsonify(data), 200


# --- PUT: częściowa aktualizacja bitwy ---
@battle_bp.route("/battles/<int:battle_id>", methods=["PUT"])
def update_battle(battle_id):
    battle = Battle.query.get(battle_id)
    if not battle:
        return jsonify({"error": "Nie znaleziono bitwy"}), 404

    payload = request.get_json() or {}

    # bezpieczne, częściowe zmiany
    if "map_name" in payload:
        if not payload["map_name"]:
            return jsonify({"error": "map_name nie może być pusty"}), 400
        battle.map_name = payload["map_name"]

    if "result" in payload:
        battle.result = payload["result"]

    if "duration" in payload:
        battle.duration = payload["duration"]

    if "game_mode_id" in payload:
        battle.game_mode_id = payload["game_mode_id"]

    if "date" in payload:
        date_str = payload["date"]
        if date_str is None or date_str == "":
            # jeśli chcesz wyczyścić -> ustaw NULL (opcjonalnie)
            battle.date = None
        else:
            try:
                battle.date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                return jsonify({"error": "date musi mieć format YYYY-MM-DD"}), 400

    db.session.commit()

    # zwróć z aktualną listą uczestników
    out = battle.to_dict()
    parts = BattleParticipant.query.filter_by(battle_id=battle_id).all()
    out["participants"] = [p.to_dict() for p in parts]

    return jsonify({"message": "Zaktualizowano bitwę", "battle": out}), 200