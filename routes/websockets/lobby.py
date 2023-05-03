from flask_socketio import Namespace, emit, join_room, leave_room
from models.lobby import Lobby
from models.player_in_lobby import PlayerInLobby
from models.player_client_id import PlayerClientId
from models.player import Player
from database import db
from flask import request
from utils import get_players_info_in_lobby
import pytz
from datetime import datetime

# Set the timezone to PST
pst_tz = pytz.timezone('America/Los_Angeles')

class LobbyNamespace(Namespace):
    def on_connect(self):
        # Get the current time in PST
        pst_time = datetime.now(pst_tz)

        # Get the timestamp in seconds
        timestamp = pst_time.timestamp()

        print("\033[95m"+f"\nWEBSOCKET: LobbyNamespace on_connect at {timestamp}\n" + "\033[00m")
        # emit request for current player id

    #listener for client response from connection
        # if not in database table player_and_client, add record
        # otherwise update client_id

    def on_disconnect(self):
        # Get the current time in PST
        pst_time = datetime.now(pst_tz)

        # Get the timestamp in seconds
        timestamp = pst_time.timestamp()

        print("\033[95m"+f"\nWEBSOCKET: LobbyNamespace on_disconnect {timestamp}\n" + "\033[00m")
        sid = request.sid
        player = PlayerClientId.query.get(sid)
        if player:
            player_id = player.player_id
            current_lobby = PlayerInLobby.query.get(player_id).lobby_id
            player_name = Player.query.get(player_id).name

            print("\033[95m"+f"\nWEBSOCKET: LobbyNamespace on_disconnect {player_name} disconnected\n" + "\033[00m")

            PlayerClientId.query.filter(PlayerClientId.client_id==sid).delete()
            PlayerInLobby.query.filter(PlayerInLobby.player_id==player_id).delete()
            db.session.commit()

            if current_lobby:
                leave_room(current_lobby)
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
        else:
            print("\033[95m"+f"\nWEBSOCKET: LobbyNamespace on_disconnect NO SID\n" + "\033[00m")
            # emit('test', request) #FIXME: request is not json serializable

        #TODO: see if you can replicate 5 minute disconnect
        #TODO: figure out what secondary on_connect happens before initial disconnect
        #TODO: Look into maintaining/retaining WS SID's


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

    def on_chat(self, message_data, current_lobby):
        print("\033[95m"+f"\nWEBSOCKET: LobbyNamespace on_chat {message_data} {current_lobby}\n" + "\033[00m")
        emit('message', message_data, to=current_lobby)

    def on_test(self, message):
        print("\033[95m"+f"\nWEBSOCKET: LobbyNamespace on_test {message}\n" + "\033[00m")
