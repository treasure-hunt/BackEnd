import time
import json
import requests
from flask import request
from flask_restful import Resource
from models.room import RoomModel
from models.player import PlayerModel
from lib.graphtraversal import GraphTraversal


# Technically CREATE PLAYER CLASS. NOT AUTO TRAVERSING
class TargetTraverse(Resource):

    def post(self, id):
        token = request.headers.get('authorization')

        if not token:
            return {'error': True, 'message': 'Missing token in authorization header.'}, 401

        # Gets the Room the player is currently in
        player_status_response = requests.get('https://lambda-treasure-hunt.herokuapp.com/api/adv/init/', headers={'authorization': token}).json()
        if len(player_status_response['errors']) > 0:
            return player_status_response, 400

        time.sleep(1)

        # finds the the player by their unique log in token
        foundTraversingPlayer = PlayerModel.find_by_password(token)

        if foundTraversingPlayer:
            return {"error": True, "message": "Your character is already traversing"}
        # If the player is not in the DB they are added
        elif not foundTraversingPlayer:

            found_path = GraphTraversal().path_to_target(player_status_response['room_id'], id)
            if not found_path:
                return {"error": True, "message": "there is no path to that room you bonobo"}

            new_player_data = {
                "password": token,
                "currentRoomId": player_status_response['room_id'],
                "currentPath": json.dumps(found_path),
                "nextAvailableMove": 0,
                "singlePath": True
            }

            foundTraversingPlayer = PlayerModel(**new_player_data)

            foundTraversingPlayer.save_to_db()

        return {'Message': 'Target Traverse has started.'}

    def delete(self):
        token = request.headers.get('authorization')

        if not token:
            return {'error': True, 'message': 'Missing token in authorization header.'}, 401

        deletePlayer = PlayerModel.find_by_password(token)
        
        if not deletePlayer:
            return {'error': True, 'message': 'Player not found.'}

        deletePlayer.delete_from_db()

        return {'Message': 'Target Traverse has been stopped.'}