from flask import Blueprint, request, jsonify
from models import db
from models.battle import Battle
from models.battle_participant import BattleParticipant

participant_bp = Blueprint('participant_bp', __name__)

@participant_bp.route("/battles/<int:battle_id>/participants", methods=["GET"])
def get_participants_for_battle(battle_id):
    battle = Battle.query.get(battle_id)
    if not battle:
        return jsonify({"error": "Nie znaleziono bitwy"}), 404
    parts = BattleParticipant.query.filter_by(battle_id=battle_id).all()
    return jsonify([p.to_dict() for p in parts]), 200


@participant_bp.route("/battles/<int:battle_id>/participants", methods=["POST"])
def add_participants_to_battle(battle_id):
    battle = Battle.query.get(battle_id)
    if not battle:
        return jsonify({"error": "Nie znaleziono bitwy"}), 404

    payload = request.get_json()

    def build_part(item):
        player_id = item.get("player_id")
        brawler_id = item.get("brawler_id")
        if player_id is None and brawler_id is None:
            return None, {"error": "Wymagane co najmniej player_id lub brawler_id"}
        is_winner = bool(item.get("is_winner", False))

        return BattleParticipant(
            battle_id=battle_id,
            player_id=player_id,
            brawler_id=brawler_id,
            is_winner=is_winner
        ), None

    created = []
    if isinstance(payload, list):
        for item in payload:
            obj, err = build_part(item)
            if err:
                return jsonify(err), 400
            db.session.add(obj)
            created.append(obj)
    else:
        obj, err = build_part(payload)
        if err:
            return jsonify(err), 400
        db.session.add(obj)
        created.append(obj)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Nie można dodać – możliwe zduplikowanie gracza w tej bitwie.", "details": str(e)}), 400

    if len(created) == 1:
        return jsonify({"message": "Dodano uczestnika", "participant": created[0].to_dict()}), 201
    return jsonify({"message": f"Dodano {len(created)} uczestników", "participants": [c.to_dict() for c in created]}), 201


@participant_bp.route("/participants/<int:participant_id>", methods=["DELETE"])
def delete_participant(participant_id):
    obj = BattleParticipant.query.get(participant_id)
    if not obj:
        return jsonify({"error": "Nie znaleziono uczestnika"}), 404
    db.session.delete(obj)
    db.session.commit()
    return jsonify({"message": f"Usunięto uczestnika {participant_id}"}), 200
