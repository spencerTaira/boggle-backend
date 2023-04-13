from flask_socketio import Namespace, emit, join_room, leave_room
from models.lobby import Lobby
from models.player_in_lobby import PlayerInLobby
from database import db

class LobbyNamespace(Namespace):
    def on_connect(self):
        print("\033[95m"+"\nWEBSOCKET: LobbyNamespace on_connect\n" + "\033[00m")

    def on_disconnect(self):
        print("\033[95m"+"\nWEBSOCKET: LobbyNamespace on_disconnect\n" + "\033[00m")
        # TODO:
        # PlayerInLobby.query.filter(PlayerInLobby.player_id==player_id).delete()
        # db.session.commit()

       
    def on_joining(self, player_data):
        print("\033[95m"+"\nWEBSOCKET: LobbyNamespace on_joining\n" + "\033[00m")

        player_name = player_data['playerName']
        current_lobby = player_data['currLobby']
        
        join_room(current_lobby)
        
        emit(
            'joined', 
            {
                "playerName":player_name, 
                "message":f"{player_name} has joined the lobby"
            },
            to=current_lobby
        )
        
    def on_leave(self, player_data):
        print("\033[95m"+"\nWEBSOCKET: LobbyNamespace on_leave\n" + "\033[00m")

        player_name = player_data['playerName']
        current_lobby = player_data['currLobby']
        player_id = player_data['playerId']
        
        leave_room(current_lobby)
        
        PlayerInLobby.query.filter(PlayerInLobby.player_id==player_id).delete()
        db.session.commit()
        
        emit(
            'left', 
            {
                "playerName":player_name, 
                "message":f"{player_name} has left the lobby"
            },
            to=current_lobby
        )