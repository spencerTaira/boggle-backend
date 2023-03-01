from flask import Blueprint, jsonify

room = Blueprint("room", __name__)

@room.post("/create")
def create_room():
    """
    Create a game room
        Input:
        Output:
    """
    test_fact = {
        "test": "hi"
    }

    return jsonify(test_fact=test_fact)