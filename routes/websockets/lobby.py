from flask_socketio import Namespace, emit, join_room, leave_room
from models.lobby import Lobby
from models.player_in_lobby import PlayerInLobby
from models.player_client_id import PlayerClientId
from models.player import Player
from database import db
from flask import request
from utils import get_players_info_in_lobby

class LobbyNamespace(Namespace):
    def on_connect(self):
        print("\033[95m"+"\nWEBSOCKET: LobbyNamespace on_connect\n" + "\033[00m")

    def on_disconnect(self):
        print("\033[95m"+"\nWEBSOCKET: LobbyNamespace on_disconnect\n" + "\033[00m")
        sid = request.sid
        player_id = PlayerClientId.query.get(sid).player_id
        PlayerClientId.query.filter(PlayerClientId.client_id==sid).delete()
        PlayerInLobby.query.filter(PlayerInLobby.player_id==player_id).delete()
        db.session.commit()

    def on_joining(self, player_data):
        print("\033[95m"+"\nWEBSOCKET: LobbyNamespace on_joining\n" + "\033[00m")

        player_name = player_data['playerName']
        current_lobby = player_data['currLobby']
        player_id = player_data['playerId']

        sid = request.sid

        clientExists = PlayerClientId.query.get(sid)

        if not clientExists:
            player_client_id = PlayerClientId(
                player_id=player_id,
                client_id=sid
            )

            db.session.add(player_client_id)
            db.session.commit()

        join_room(current_lobby)

        players_info = get_players_info_in_lobby(current_lobby)

        emit(
            'message',
            {
                "playerName":player_name,
                "message":f"{player_name} has joined the lobby"
            },
            to=current_lobby
        )

        emit('update_players', players_info, to=current_lobby)

    def on_leave(self, player_data):
        print("\033[95m"+"\nWEBSOCKET: LobbyNamespace on_leave\n" + "\033[00m")

        player_name = player_data['playerName']
        current_lobby = player_data['currLobby']
        player_id = player_data['playerId']

        leave_room(current_lobby)

        PlayerInLobby.query.filter(PlayerInLobby.player_id==player_id).delete()
        db.session.commit()

        players_info = get_players_info_in_lobby(current_lobby)

        emit(
            'message',
            {
                "playerName":player_name,
                "message":f"{player_name} has left the lobby"
            },
            to=current_lobby
        )

        emit('update_players', players_info, to=current_lobby)