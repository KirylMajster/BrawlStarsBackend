from flask import Blueprint, jsonify, request
from models import db
from models.player import Player
from models.battle_participant import BattleParticipant
from models.battle import Battle
from models.gamemode import GameMode


player_bp = Blueprint('player_bp', __name__)

@player_bp.route("/players", methods=["GET"])
def get_players():
    players = Player.query.all()
    return jsonify([p.to_dict() for p in players])

@player_bp.route("/players", methods=["POST"])
def add_player():
    data = request.get_json()

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


@player_bp.route("/players/<int:player_id>/brawlers", methods=["GET"])
def get_brawlers_for_player(player_id):
    from models.brawler import Brawler  

    player = Player.query.get(player_id)
    if not player:
        return jsonify({"error": "Gracz o podanym ID nie istnieje"}), 404

    brawlers = Brawler.query.filter_by(player_id=player_id).all()
    return jsonify([b.to_dict() for b in brawlers])

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


@player_bp.route("/players/<int:player_id>", methods=["DELETE"])
def delete_player(player_id):
    player = Player.query.get(player_id)
    if not player:
        return jsonify({"error": "Gracz o podanym ID nie istnieje"}), 404

    db.session.delete(player)
    db.session.commit()
    return jsonify({"message": f"Gracz '{player.nickname}' został usunięty."}), 200


@player_bp.route("/players/<int:player_id>/battles", methods=["GET"])
def get_battles_for_player(player_id):
    player = Player.query.get(player_id)
    if not player:
        return jsonify({"error": "Gracz o podanym ID nie istnieje"}), 404

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

        item.update({
            "participant_id": part.id,
            "brawler_id": part.brawler_id,
            "is_winner": part.is_winner,
        })
        out.append(item)

    return jsonify(out), 200

@player_bp.route("/players/<int:player_id>/winrate", methods=["GET"])
def get_player_winrate(player_id):
    """
    Zwraca statystyki wygranych/przegranych dla danego gracza
    na podstawie tabeli battle_participant.
    """


    player = Player.query.get(player_id)
    if not player:
        return jsonify({"error": "Player not found"}), 404


    wins = BattleParticipant.query.filter_by(
        player_id=player_id,
        is_winner=True
    ).count()

    losses = BattleParticipant.query.filter_by(
        player_id=player_id,
        is_winner=False
    ).count()

    total = wins + losses


    if total == 0:
        winrate = None
        winrate_percentage = None
    else:
        winrate = wins / total
        winrate_percentage = round(winrate * 100, 2)

    return jsonify({
        "player_id": player.id,
        "nickname": player.nickname,
        "wins": wins,
        "losses": losses,
        "total_battles": total,
        "winrate": winrate,                
        "winrate_percentage": winrate_percentage  
    }), 200

@player_bp.route("/players/leaderboard/wins", methods=["GET"])
def get_players_leaderboard_by_wins():
    """
    Ranking graczy według liczby wygranych.
    Opcjonalny parametr ?limit=N ogranicza liczbę graczy w odpowiedzi.
    """


    limit = request.args.get("limit", type=int)

    players = Player.query.all()
    stats = []

    for p in players:

        wins = BattleParticipant.query.filter_by(
            player_id=p.id,
            is_winner=True
        ).count()

        losses = BattleParticipant.query.filter_by(
            player_id=p.id,
            is_winner=False
        ).count()

        total = wins + losses

        if total == 0:
            winrate = None
            winrate_percentage = None
        else:
            winrate = wins / total
            winrate_percentage = round(winrate * 100, 2)

        stats.append({
            "player_id": p.id,
            "nickname": p.nickname,
            "wins": wins,
            "losses": losses,
            "total_battles": total,
            "winrate": winrate,
            "winrate_percentage": winrate_percentage,
        })


    stats.sort(
        key=lambda x: (
            -x["wins"],
            -(x["winrate"] or 0),
            x["nickname"].lower(),
        )
    )


    if limit is not None and limit > 0:
        stats = stats[:limit]

    return jsonify({
        "leaderboard_type": "wins",
        "players": stats,
    }), 200


@player_bp.route("/players/<int:player_id>/best_gamemode", methods=["GET"])
def get_player_best_gamemode(player_id):
    """
    Zwraca tryb(y) gry, w których dany gracz ma najlepsze statystyki.
    Parametr ?metric=winrate lub ?metric=wins decyduje o sposobie sortowania.
    """


    player = Player.query.get(player_id)
    if not player:
        return jsonify({"error": "Player not found"}), 404


    metric = request.args.get("metric", "winrate").lower()
    if metric not in ("winrate", "wins"):
        metric = "winrate"


    participations = BattleParticipant.query.filter_by(player_id=player_id).all()

    if not participations:
        return jsonify({
            "player_id": player.id,
            "nickname": player.nickname,
            "metric": metric,
            "message": "Gracz nie ma jeszcze żadnych bitew",
            "gamemodes": []
        }), 200


    stats_per_mode = {}

    for part in participations:
        battle = part.battle
        if not battle or not battle.game_mode_id:
            continue

        gm_id = battle.game_mode_id
        gm_name = battle.game_mode.name if battle.game_mode else None

        if gm_id not in stats_per_mode:
            stats_per_mode[gm_id] = {
                "game_mode_id": gm_id,
                "game_mode_name": gm_name,
                "wins": 0,
                "losses": 0,
                "total_battles": 0,
                "winrate": None,
                "winrate_percentage": None,
            }

        entry = stats_per_mode[gm_id]

        if part.is_winner:
            entry["wins"] += 1
        else:
            entry["losses"] += 1

        entry["total_battles"] += 1

    for entry in stats_per_mode.values():
        total = entry["total_battles"]
        if total > 0:
            wr = entry["wins"] / total
            entry["winrate"] = wr
            entry["winrate_percentage"] = round(wr * 100, 2)
        else:
            entry["winrate"] = None
            entry["winrate_percentage"] = None

    if not stats_per_mode:
        return jsonify({
            "player_id": player.id,
            "nickname": player.nickname,
            "metric": metric,
            "message": "Brak bitew z przypisanym trybem gry",
            "gamemodes": []
        }), 200


    modes_list = list(stats_per_mode.values())

    if metric == "wins":
        modes_list.sort(
            key=lambda m: (
                -m["wins"],
                -(m["winrate"] or 0),
                -m["total_battles"],
                (m["game_mode_name"] or "").lower(),
            )
        )
    else:  
        modes_list.sort(
            key=lambda m: (
                -(m["winrate"] or 0),
                -m["wins"],
                -m["total_battles"],
                (m["game_mode_name"] or "").lower(),
            )
        )

    best_mode = modes_list[0]

    return jsonify({
        "player_id": player.id,
        "nickname": player.nickname,
        "metric": metric,
        "best_gamemode": best_mode,
        "all_gamemodes": modes_list
    }), 200
