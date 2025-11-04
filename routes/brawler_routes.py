from flask import Blueprint, jsonify, request
from models.brawler import Brawler, db
from models.player import Player

brawler_bp = Blueprint('brawler_bp', __name__)

@brawler_bp.route("/brawlers", methods=["GET"])
def get_brawlers():
    brawlers = Brawler.query.all()
    return jsonify([b.to_dict() for b in brawlers])

@brawler_bp.route("/brawlers", methods=["POST"])
def add_brawler():
    data = request.get_json()

    # Jeśli przesłano listę — dodaj wielu brawlerów
    if isinstance(data, list):
        brawlers = []
        for item in data:
            new_brawler = Brawler(
                name=item["name"],
                rarity=item.get("rarity", "Common"),
                health=item.get("health", 1000),
                damage=item.get("damage", 100),
                speed=item.get("speed", 720),
                player_id=item.get("player_id")  # może być None
            )
            db.session.add(new_brawler)
            brawlers.append(new_brawler)

        db.session.commit()
        return jsonify({
            "message": f"Dodano {len(brawlers)} brawlerów!",
            "brawlers": [b.to_dict() for b in brawlers]
        }), 201

    # Jeśli przesłano pojedynczego brawlera
    else:
        new_brawler = Brawler(
            name=data["name"],
            rarity=data.get("rarity", "Common"),
            health=data.get("health", 1000),
            damage=data.get("damage", 100),
            speed=data.get("speed", 720),
            player_id=data.get("player_id")
        )
        db.session.add(new_brawler)
        db.session.commit()
        return jsonify({
            "message": "Dodano brawlera!",
            "brawler": new_brawler.to_dict()
        }), 201


    # --- ROUTE: aktualizacja brawlera ---
@brawler_bp.route("/brawlers/<int:brawler_id>", methods=["PUT"])
def update_brawler(brawler_id):
    brawler = Brawler.query.get(brawler_id)
    if not brawler:
        return jsonify({"error": "Brawler o podanym ID nie istnieje"}), 404

    data = request.get_json()
    brawler.name = data.get("name", brawler.name)
    brawler.rarity = data.get("rarity", brawler.rarity)
    brawler.health = data.get("health", brawler.health)
    brawler.damage = data.get("damage", brawler.damage)
    brawler.speed = data.get("speed", brawler.speed)
    brawler.player_id = data.get("player_id", brawler.player_id)

    db.session.commit()
    return jsonify({"message": "Dane brawlera zostały zaktualizowane", "brawler": brawler.to_dict()}), 200


# --- ROUTE: usuwanie brawlera ---
@brawler_bp.route("/brawlers/<int:brawler_id>", methods=["DELETE"])
def delete_brawler(brawler_id):
    brawler = Brawler.query.get(brawler_id)
    if not brawler:
        return jsonify({"error": "Brawler o podanym ID nie istnieje"}), 404

    db.session.delete(brawler)
    db.session.commit()
    return jsonify({"message": f"Brawler '{brawler.name}' został usunięty."}), 200
