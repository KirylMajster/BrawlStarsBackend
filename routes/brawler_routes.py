from flask import Blueprint, jsonify, request
from models import db
from models.brawler import Brawler
from models.player import Player


brawler_bp = Blueprint("brawler_bp", __name__)


@brawler_bp.route("/brawlers", methods=["GET"])
def get_brawlers():
    brawlers = Brawler.query.all()
    return jsonify([b.to_dict() for b in brawlers]), 200


@brawler_bp.route("/brawlers", methods=["POST"])
def add_brawlers():
    payload = request.get_json()

    def make_brawler(item: dict) -> Brawler:
        name = item.get("name")
        if not name:
            raise ValueError("Pole 'name' jest wymagane")

        player_id = item.get("player_id")
        if player_id is None:
            raise ValueError("Dla relacji 1:1 wymagane jest pole 'player_id'")

        if not Player.query.get(player_id):
            raise ValueError(f"Gracz o id={player_id} nie istnieje")

        existing = Brawler.query.filter_by(player_id=player_id).first()
        if existing:
            raise ValueError(
                f"Gracz o id={player_id} ma już przypisanego brawlera (id={existing.id})"
            )

        b = Brawler(
            name=name,
            rarity=item.get("rarity"),
            health=item.get("health"),
            damage=item.get("damage"),
            speed=item.get("speed"),
            trophies=item.get("trophies", 0),
            player_id=player_id,
        )
        db.session.add(b)
        return b

    try:
        if isinstance(payload, list):
            created = [make_brawler(it) for it in payload]
            db.session.commit()
            return jsonify(
                {
                    "message": f"Dodano {len(created)} brawlerów!",
                    "brawlers": [b.to_dict() for b in created],
                }
            ), 201

        else:
            b = make_brawler(payload)
            db.session.commit()
            return jsonify(
                {
                    "message": "Dodano brawlera!",
                    "brawler": b.to_dict(),
                }
            ), 201
    except ValueError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400



@brawler_bp.route("/brawlers/<int:brawler_id>", methods=["PUT"])
def update_brawler(brawler_id):
    data = request.get_json() or {}
    b = Brawler.query.get(brawler_id)
    if not b:
        return jsonify({"error": "Brawler not found"}), 404


    new_player_id = data.get("player_id", b.player_id)
    if new_player_id is None:
        return jsonify(
            {"error": "Pole 'player_id' nie może być puste przy relacji 1:1"}
        ), 400

    if not Player.query.get(new_player_id):
        return jsonify({"error": f"Gracz o id={new_player_id} nie istnieje"}), 400

    existing = Brawler.query.filter(
        Brawler.player_id == new_player_id,
        Brawler.id != b.id,
    ).first()
    if existing:
        return jsonify(
            {
                "error": f"Gracz o id={new_player_id} ma już przypisanego brawlera (id={existing.id})"
            }
        ), 400

    for field in ["name", "rarity", "health", "damage", "speed", "trophies", "player_id"]:
        if field in data:
            setattr(b, field, data[field])

    db.session.commit()
    return jsonify({"message": "updated", "id": b.id}), 200


@brawler_bp.route("/brawlers/<int:brawler_id>", methods=["DELETE"])
def delete_brawler(brawler_id):
    brawler = Brawler.query.get(brawler_id)
    if not brawler:
        return jsonify({"error": "Brawler o podanym ID nie istnieje"}), 404

    db.session.delete(brawler)
    db.session.commit()
    return jsonify({"message": f"Brawler '{brawler.name}' został usunięty."}), 200
