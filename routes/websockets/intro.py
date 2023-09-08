from flask import request
from flask_socketio import Namespace, emit
from models.lobby import Lobby
from models.player_in_lobby import PlayerInLobby
from database import db

class IntroNamespace(Namespace):
    def on_connect(self):
        print("\033[95m"+"\nWEBSOCKET: IntroNamespace on_connect\n" + "\033[00m")

    def on_disconnect(self):
        print("\033[95m"+"\nWEBSOCKET: IntroNamespace on_disconnect\n" + "\033[00m")

    def on_intro_get_lobbys(self):
        """
        Get active public lobbys and send to front-end
        """

        print("\033[95m"+"\nWEBSOCKET: Intro-get-lobbys\n" + "\033[00m")

        """
            num_players_in_lobbys (list of tuples)

            create an empty list
            iterate through num_players_in_lobbys
            query.get(lobby_id)
            check if (num_players) is less than lobby.max_players
                if it is push into list


            SELECT lobbys.lobby_name, lobbys.max_players, pil.curr_players
                FROM lobbys
                LEFT JOIN (
                    SELECT lobby_id, COUNT(lobby_id) AS curr_players
                        FROM players_in_lobbys
                        GROUP BY lobby_id
                ) as pil
                ON lobbys.lobby_name = pil.lobby_id
                    WHERE pil.curr_players < lobbys.max_players
                        OR pil.curr_players is NULL;

        """

        # print("\033[95m"+"\nPre Sub Query\n" + "\033[00m")
        subquery = db.session.query(
            PlayerInLobby.lobby_id, db.func.count(PlayerInLobby.lobby_id)
                .label('curr_players')
            ).group_by(PlayerInLobby.lobby_id
        ).subquery()

        # print("\033[95m"+"\nPost Sub Query\n" + "\033[00m")
        query = db.session.query(
            Lobby.lobby_name, Lobby.max_players, subquery.c.curr_players
        ).outerjoin(
            subquery, Lobby.lobby_name == subquery.c.lobby_id
        ).filter(
            (subquery.c.curr_players < Lobby.max_players) | (subquery.c.curr_players == None)
        )

        non_full_lobbys = query.all()

        lobbys_serialized = []
        for row in non_full_lobbys:
            lobby = {
                "lobby_name":row.lobby_name,
                "max_players":row.max_players,
                "curr_players":row.curr_players
            }
            lobbys_serialized.append(lobby)

        emit('intro-send-lobbys', lobbys_serialized)

