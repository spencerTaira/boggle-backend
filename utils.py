from models.player_in_lobby import PlayerInLobby
from models.player import Player

def get_players_info_in_lobby(curr_lobby):
    players_in_lobby = PlayerInLobby.query.filter(PlayerInLobby.lobby_id==curr_lobby).all()
    playerIDs_in_lobby = [player.player_id for player in players_in_lobby]

    players_info_in_lobby = Player.query.filter(Player.id.in_(playerIDs_in_lobby)).all()
    players_serialized_info_in_lobby = [
        {
            "playerId": player.id,
            "playerName": player.name
        }
        for player in players_info_in_lobby
    ]

    return players_serialized_info_in_lobby

def get_num_players_in_lobby(lobby_id):
    return len(PlayerInLobby.query.filter_by(lobby_id=lobby_id).all())