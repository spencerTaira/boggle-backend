from flask_socketio import Namespace, emit, join_room, leave_room, disconnect
from models.lobby import Lobby
from models.player_in_lobby import PlayerInLobby
# from models.player_client_id import PlayerClientId
from models.player import Player
from database import db
from flask import request
from utils import get_players_info_in_lobby
from datetime import datetime

class LobbyNamespace(Namespace):

    def on_connect(self):
        print("\033[95m"+f"\nWEBSOCKET: LobbyNamespace on_connect\n" + "\033[00m")

        # # emit request for current player id
        player_id = request.args.get('player_id', 'Initial connect')
        print("\033[95m"+f"\nLOBBY WEBSOCKET: player_id: {player_id}\n" + "\033[00m")

        emit('is_connected')

    def on_player_data(self, player_data):
        print("\033[95m"+f"\nWEBSOCKET: LobbyNamespace on_player_data\n" + "\033[00m")

        current_lobby = player_data['currLobby']


        #TODO: Make new model connecting player id and lobby name and game id
        join_room(current_lobby)

        players_info = get_players_info_in_lobby(current_lobby)
        emit('update_players', players_info, to=current_lobby)
        emit('joined', 'joined the lobby')


    def on_disconnect(self):
        # Get current time
        # now = datetime.now()

        # Format time as human-readable string
        # current_time = now.strftime("%Y-%m-%d %H:%M:%S")

        # print("\033[95m"+f"\nWEBSOCKET: LobbyNamespace on_disconnect {current_time}\n" + "\033[00m")
        player_id = request.args['player_id']
        print("\033[95m"+f"\nWEBSOCKET: LobbyNamespace on_disconnect {request.namespace}\n" + "\033[00m")
        print("\033[95m"+f"\nWEBSOCKET: LobbyNamespace on_disconnect {player_id}\n" + "\033[00m")

        try:
            current_lobby = PlayerInLobby.query.get(player_id).lobby_id
            player_name = Player.query.get(player_id).name

            # remove from player from players in lobbys database
            PlayerInLobby.query.filter(PlayerInLobby.player_id==player_id).delete()
            db.session.commit()

            updated_players_info = get_players_info_in_lobby(current_lobby)

            # remove from websocket room
            leave_room(current_lobby)

            # emit 'chat_message'
            # emit 'update_players'
            emit(
                    'chat_message',
                    {
                        "playerName":player_name,
                        "message":f"{player_name} has left the lobby"
                    },
                    to=current_lobby
                )

            emit('update_players', updated_players_info, to=current_lobby)

        except Exception as e:
            print(f"Error: {e}")
            raise

        # sid = request.sid
        # player = PlayerClientId.query.get(sid)
        # if player:
        #     player_id = player.player_id
        #     current_lobby = PlayerInLobby.query.get(player_id).lobby_id
        #     player_name = Player.query.get(player_id).name

        #     print("\033[95m"+f"\nWEBSOCKET: LobbyNamespace on_disconnect {player_name} disconnected\n" + "\033[00m")

        #     PlayerClientId.query.filter(PlayerClientId.client_id==sid).delete()
        #     PlayerInLobby.query.filter(PlayerInLobby.player_id==player_id).delete()
        #     db.session.commit()

        #     if current_lobby:
        #         leave_room(current_lobby)
        #         players_info = get_players_info_in_lobby(current_lobby)

        #         emit(
        #             'chat_message',
        #             {
        #                 "playerName":player_name,
        #                 "message":f"{player_name} has left the lobby"
        #             },
        #             to=current_lobby
        #         )

        #         emit('update_players', players_info, to=current_lobby)
        # else:
        #     print("\033[95m"+f"\nWEBSOCKET: LobbyNamespace on_disconnect NO SID\n" + "\033[00m")
            # emit('test', request) #FIXME: request is not json serializable

        #TODO: see if you can replicate 5 minute disconnect
        #TODO: figure out what secondary on_connect happens before initial disconnect







    #Closing the window will not neccessarily trigger this event
    # def on_leave(self, player_data):
    #     print("\033[95m"+"\nWEBSOCKET: LobbyNamespace on_leave\n" + "\033[00m")

    #     player_name = player_data['playerName']
    #     current_lobby = player_data['currLobby']
    #     player_id = player_data['playerId']

    #     leave_room(current_lobby)

    #     PlayerInLobby.query.filter(PlayerInLobby.player_id==player_id).delete()
    #     db.session.commit()

    #     players_info = get_players_info_in_lobby(current_lobby)

    #     emit(
    #         'chat_message',
    #         {
    #             "playerName":player_name,
    #             "message":f"{player_name} has left the lobby"
    #         },
    #         to=current_lobby
    #     )

    #     emit('update_players', players_info, to=current_lobby)

    def on_chat(self, message_data, current_lobby, include_self=False):
        print("\033[95m"+f"\nWEBSOCKET: LobbyNamespace on_chat {message_data} {current_lobby}\n" + "\033[00m")
        emit('chat_message', message_data, to=current_lobby, include_self=include_self)

    # def on_test(self, message):
    #     print("\033[95m"+f"\nWEBSOCKET: LobbyNamespace on_test {message}\n" + "\033[00m")
