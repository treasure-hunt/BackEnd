import time
import requests
import re
from flask import request
from flask_restful import Resource
from models.room import RoomModel


class Traverse(Resource):
    # Direction will be n, e, s, or w

    def post(self, direction):
        token = request.headers.get('authorization')
        if not token:
            return {'error': True, 'message': 'Missing token in authorization header.'}, 401
        if not direction:
            return {'error': True, 'message': 'You must provide a direction. N, E, S, or W.'}, 400

        move = direction.lower()
        # Get the room the player is currently in:
        player_status_response = requests.get('https://lambda-treasure-hunt.herokuapp.com/api/adv/init/', headers={'authorization': token}).json()
        if len(player_status_response['errors']) > 0:
            return player_status_response, 400
        time.sleep(1)
        # if the direction the player wants to move is in their current rooms direction list (if its a possible direction to move)
        if move in player_status_response["exits"]:
            # See if we have the players current room in our database.
            found_room = RoomModel.find_by_id(
                player_status_response['room_id'])
            # If we don't have the room in our database, we haven't seen it before. So we add it to our database.
            if not found_room:
                # room_coordinates turns "(32,45)" -> ["32", "45"]
                room_coordinates = re.findall(
                    r"\d+", player_status_response['coordinates'])
                new_room_data = {
                    "id": player_status_response['room_id'],
                    "title": player_status_response['title'],
                    "description": player_status_response['description'],
                    "x": int(room_coordinates[0]),
                    "y": int(room_coordinates[1]),
                    "n": None,
                    "w": None,
                    "e": None,
                    "s": None,
                }
                found_room = RoomModel(**new_room_data)

                # Now travel and save the next room result in the previous room
                player_travel_request = requests.post('https://lambda-treasure-hunt.herokuapp.com/api/adv/move/', json={"direction": move}, headers={'authorization': token}).json()
                try:
                    new_room_id = player_travel_request['room_id']
                    # found_room[move] = new_room_id
                    setattr(found_room, move, new_room_id)
                    found_room.save_to_db()
                    return player_travel_request, 200
                except KeyError:
                    return player_travel_request, 400
            # Room is found
            else:
                # Check if we have the next room's id that the player is traveling to. If we do, travel there and return response to user.
                if move in found_room.json()["exits"] and found_room.json()["exits"][move]:
                    next_room = found_room.json()["exits"][move]
                    player_travel_request = requests.post('https://lambda-treasure-hunt.herokuapp.com/api/adv/move/', json={"direction": move, "next_room_id": str(next_room)}, headers={'authorization': token}).json()
                    return player_travel_request, 200
                # If we don't, travel that direction without wise explorer bonus. Then save that direction result in our found_room for next time.
                else:
                    player_travel_request = requests.post('https://lambda-treasure-hunt.herokuapp.com/api/adv/move/', json={"direction": move}, headers={'authorization': token}).json()
                    try:
                        new_room_id = player_travel_request['room_id']
                        setattr(found_room, move, new_room_id)
                        found_room.save_to_db()
                        return player_travel_request, 200
                    except KeyError:
                        return player_travel_request, 400
        else:
            return {'error': True, 'message': 'There is no exit in that direction.'}, 400