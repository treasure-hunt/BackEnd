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

        opposite_dirs = {
            "n": "s",
            "e": "w",
            "s": "n",
            "w": "e"
        }

        move = direction.lower()
        # Get the room the player is currently in:
        player_status_response = requests.get('https://lambda-treasure-hunt.herokuapp.com/api/adv/init/', headers={'authorization': token}).json()
        if len(player_status_response['errors']) > 0:
            return player_status_response, 400
        time.sleep(1)
        # if the direction the player wants to move is in their current rooms direction list (if its a possible direction to move)
        if move in player_status_response["exits"]:
            # See if we have the players current room in our database.
            found_room = RoomModel.find_by_id(player_status_response['room_id'])
            # If we don't have the room in our database, we haven't seen it before. So we add it to our database.
            if not found_room:
                # room_coordinates turns "(32,45)" -> ["32", "45"]
                room_coordinates = re.findall(
                    r"\d+", player_status_response['coordinates'])
                
                avail_exits = {
                    "n": None if not "n" in player_status_response["exits"] else "?",
                    "w": None if not "w" in player_status_response["exits"] else "?",
                    "e": None if not "e" in player_status_response["exits"] else "?",
                    "s": None if not "s" in player_status_response["exits"] else "?",
                }

                new_room_data = {
                    "id": player_status_response['room_id'],
                    "title": player_status_response['title'],
                    "description": player_status_response['description'],
                    "x": int(room_coordinates[0]),
                    "y": int(room_coordinates[1]),
                    "terrain": player_status_response['terrain'],
                    "elevation": player_status_response['elevation']
                    
                }
                
                new_room_data.update(avail_exits)

                found_room = RoomModel(**new_room_data)

                # Now travel and save the next room result in the previous room
                player_travel_request = requests.post('https://lambda-treasure-hunt.herokuapp.com/api/adv/move/', json={"direction": move}, headers={'authorization': token}).json()
                try:
                    new_room_id = player_travel_request['room_id']
                    traveled_into_room = RoomModel.find_by_id(new_room_id)
                    print(traveled_into_room)
                    if not traveled_into_room:
                        # Create room record for the room we just traveled into if not found
                        new_room_coordinates = re.findall(
                        r"\d+", player_travel_request['coordinates'])

                        avail_exits = {
                            "n": None if not "n" in player_travel_request["exits"] else "?",
                            "w": None if not "w" in player_travel_request["exits"] else "?",
                            "e": None if not "e" in player_travel_request["exits"] else "?",
                            "s": None if not "s" in player_travel_request["exits"] else "?",
                        }


                        traveled_into_room_data = {
                            "id": new_room_id,
                            "title": player_travel_request['title'],
                            "description": player_travel_request['description'],
                            "x": int(new_room_coordinates[0]),
                            "y": int(new_room_coordinates[1]),
                            "terrain": player_travel_request['terrain'],
                            "elevation": player_travel_request['elevation']
                        }

                        traveled_into_room_data.update(avail_exits)
                        traveled_into_room = RoomModel(**traveled_into_room_data)

                    setattr(traveled_into_room, opposite_dirs[move], str(found_room.json()['id']))
                    setattr(found_room, move, new_room_id)
                    found_room.save_to_db()
                    return player_travel_request, 200
                except KeyError:
                    return player_travel_request, 400
            # Room is found
            else:
                # Check if we have the next room's id that the player is traveling to. If we do, travel there and return response to user.
                if move in found_room.json()["exits"] and found_room.json()["exits"][move] is not None and found_room.json()["exits"][move] is not "?":
                    print('we have current room, and next.')
                    next_room = found_room.json()["exits"][move]
                    player_travel_request = requests.post('https://lambda-treasure-hunt.herokuapp.com/api/adv/move/', json={"direction": move, "next_room_id": str(next_room)}, headers={'authorization': token}).json()
                    return player_travel_request, 200
                # If we don't, travel that direction without wise explorer bonus. Then save that direction result in our found_room for next time.
                else:
                    player_travel_request = requests.post('https://lambda-treasure-hunt.herokuapp.com/api/adv/move/', json={"direction": move}, headers={'authorization': token}).json()
                    try:
                        # Create new room we just traveled into, and save the direction to the previous room.
                        print('we have current room, not next')
                        new_found_room = RoomModel.find_by_id(player_travel_request["room_id"])
                        new_room_id = player_travel_request['room_id']
                        if not new_found_room:
                            room_coordinates = re.findall(
                                r"\d+", player_travel_request['coordinates'])

                            avail_exits = {
                                "n": None if not "n" in player_travel_request["exits"] else "?",
                                "w": None if not "w" in player_travel_request["exits"] else "?",
                                "e": None if not "e" in player_travel_request["exits"] else "?",
                                "s": None if not "s" in player_travel_request["exits"] else "?",
                            }

                            new_room_data = {
                                "id": new_room_id,
                                "title": player_travel_request['title'],
                                "description": player_travel_request['description'],
                                "x": int(room_coordinates[0]),
                                "y": int(room_coordinates[1]),
                                "terrain": player_travel_request['terrain'],
                                "elevation": player_travel_request['elevation']
                            }

                            new_room_data.update(avail_exits)
                            new_found_room = RoomModel(**new_room_data)

                        setattr(new_found_room, opposite_dirs[move], str(player_status_response["room_id"]))
                        setattr(found_room, move, new_room_id)
                        new_found_room.save_to_db()
                        found_room.save_to_db()
                        return player_travel_request, 200
                    except KeyError:
                        return player_travel_request, 400
        else:
            return {'error': True, 'message': 'There is no exit in that direction.'}, 400
