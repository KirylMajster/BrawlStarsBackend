from flask import Blueprint, jsonify, request
from models.player import Player, db
from models.battle import Battle
from models.battle_participant import BattleParticipant

player_bp = Blueprint('player_bp', __name__)

@player_bp.route("/players", methods=["GET"])
def get_players():
    players = Player.query.all()
    return jsonify([p.to_dict() for p in players])

@player_bp.route("/players", methods=["POST"])
def add_player():
    data = request.get_json()

    # Jeśli to lista – dodaj wielu graczy naraz
    if isinstance(data, list):
        players = []
        for item in data:
            new_player = Player(
                nickname=item["nickname"],
                level=item.get("level", 1),
                total_trophies=item.get("total_trophies", 0)
            )
            db.session.add(new_player)
            players.append(new_player)
        db.session.commit()
        return jsonify({
            "message": f"Dodano {len(players)} graczy!",
            "players": [p.to_dict() for p in players]
        }), 201

    # Jeśli to pojedynczy gracz – działa jak wcześniej
    else:
        new_player = Player(
            nickname=data["nickname"],
            level=data.get("level", 1),
            total_trophies=data.get("total_trophies", 0)
        )
        db.session.add(new_player)
        db.session.commit()
        return jsonify({
            "message": "Dodano gracza!",
            "player": new_player.to_dict()
        }), 201


    # --- ROUTE: pobierz wszystkich brawlerów konkretnego gracza ---
@player_bp.route("/players/<int:player_id>/brawlers", methods=["GET"])
def get_brawlers_for_player(player_id):
    from models.brawler import Brawler  # lokalny import, żeby uniknąć pętli importów

    player = Player.query.get(player_id)
    if not player:
        return jsonify({"error": "Gracz o podanym ID nie istnieje"}), 404

    brawlers = Brawler.query.filter_by(player_id=player_id).all()
    return jsonify([b.to_dict() for b in brawlers])

# --- ROUTE: aktualizacja danych gracza ---
@player_bp.route("/players/<int:player_id>", methods=["PUT"])
def update_player(player_id):
    player = Player.query.get(player_id)
    if not player:
        return jsonify({"error": "Gracz o podanym ID nie istnieje"}), 404

    data = request.get_json()
    player.nickname = data.get("nickname", player.nickname)
    player.level = data.get("level", player.level)
    player.total_trophies = data.get("total_trophies", player.total_trophies)

    db.session.commit()
    return jsonify({"message": "Dane gracza zostały zaktualizowane", "player": player.to_dict()}), 200


# --- ROUTE: usuwanie gracza ---
@player_bp.route("/players/<int:player_id>", methods=["DELETE"])
def delete_player(player_id):
    player = Player.query.get(player_id)
    if not player:
        return jsonify({"error": "Gracz o podanym ID nie istnieje"}), 404

    db.session.delete(player)
    db.session.commit()
    return jsonify({"message": f"Gracz '{player.nickname}' został usunięty."}), 200


# --- LISTA BITEW DLA KONKRETNEGO GRACZA ---
@player_bp.route("/players/<int:player_id>/battles", methods=["GET"])
def get_battles_for_player(player_id):
    player = Player.query.get(player_id)
    if not player:
        return jsonify({"error": "Gracz o podanym ID nie istnieje"}), 404

    # opcjonalne proste filtrowanie: ?result=win/lose/draw
    result_filter = request.args.get("result")

    q = (
        db.session.query(Battle, BattleParticipant)
        .join(BattleParticipant, Battle.id == BattleParticipant.battle_id)
        .filter(BattleParticipant.player_id == player_id)
    )
    if result_filter:
        q = q.filter(Battle.result == result_filter)

    rows = q.all()

    out = []
    for battle, part in rows:
        item = battle.to_dict()
        # wzbogacamy danymi “uczestnika”
        item.update({
            "participant_id": part.id,
            "brawler_id": part.brawler_id,
            "is_winner": part.is_winner,
        })
        out.append(item)

    return jsonify(out), 200