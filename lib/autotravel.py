import time
import json
from threading import Thread
from models.room import RoomModel
from models.player import PlayerModel
from resources.traverse import Traverse
from lib.graphtraversal import GraphTraversal
import requests


class AutoTravel(Thread):
    def __init__(self, app):
        Thread.__init__(self)
        self.daemon = True
        self.GraphTraversal = GraphTraversal()
        self.app = app
        self.start()

    def run(self):
        self.start_loop()

    def start_loop(self):
        with self.app.app_context():
            directions = ['n', 'e', 's', 'w']
            while True:
                time.sleep(1)
                # Get all players who are automatically traversing
                traversing_players = PlayerModel.find_all_by_single_path(False)
                if not traversing_players or len(traversing_players) < 1:
                    print('No one traversing automatically. Skipping.')
                    continue
                # Make every record of traversing_players the JSON dict available.
                for player in traversing_players:
                    player_data = player.json()
                    # Only register next move if the player is passed cooldown.
                    if int(time.time()) < player_data['nextAvailableMove'] + 2:
                        continue
                    player_path = json.loads(player_data["currentPath"])["path"]
                    # Player has a path, travel based on it.
                    if len(player_path) > 0:
                        direction = player_path.pop(0)
                        traverse_to_room = Traverse.TraverseOnce(player_data['password'], direction)
                        traverse_to_room = traverse_to_room[0]
                        if len(traverse_to_room['errors']) > 0:
                            setattr(player, 'nextAvailableMove', (int(time.time()) + int(traverse_to_room['cooldown'])))
                            player.save_to_db()
                            continue
                        setattr(player, 'nextAvailableMove', int(time.time()) + int(traverse_to_room['cooldown']))
                        setattr(player, 'currentRoomId', traverse_to_room['room_id'])
                        setattr(player, 'currentPath', json.dumps({"path": player_path})) 
                        player.save_to_db()
                        print(f"player traveled {direction} to {traverse_to_room['room_id']}")
                        continue
                        # return traverse_to_room

                    current_room = RoomModel.find_by_id(player_data['currentRoomId'])
                    current_room_data = None
                    if current_room:
                        current_room_data = current_room.json()
                    else:
                        # Get the room the player is currently in:
                        player_status_response = requests.get('https://lambda-treasure-hunt.herokuapp.com/api/adv/init/', headers={'authorization': player_data['password']}).json()
                        time.sleep(1)
                        if len(player_status_response['errors']) > 0:
                            setattr(player, 'nextAvailableMove', (int(time.time()) + int(player_status_response['cooldown'])))
                            player.save_to_db()
                            continue
                        direction = player_status_response['exits'][0]
                        traverse_to_room = Traverse.TraverseOnce(player_data['password'], direction)
                        traverse_to_room = traverse_to_room[0]
                        if len(traverse_to_room['errors']) > 0:
                            setattr(player, 'nextAvailableMove', (int(time.time()) + int(traverse_to_room['cooldown'])))
                            player.save_to_db()
                            continue
                        setattr(player, 'nextAvailableMove', (int(time.time()) + int(traverse_to_room['cooldown'])))
                        setattr(player, 'currentRoomId', traverse_to_room['room_id'])
                        player.save_to_db()
                        continue
                    # Check if any exits are unexplored by our database.
                    for direction in directions:
                        if current_room_data['exits'][direction] == '?':
                            # move to that room.
                            traverse_to_room = Traverse.TraverseOnce(player_data['password'], direction)
                            traverse_to_room = traverse_to_room[0]
                            if len(traverse_to_room['errors']) > 0:
                                setattr(player, 'nextAvailableMove', (int(time.time()) + int(traverse_to_room['cooldown'])))
                                player.save_to_db()
                                continue
                            setattr(player, 'nextAvailableMove', int(time.time()) + traverse_to_room['cooldown'])
                            setattr(player, 'currentRoomId', traverse_to_room['room_id'])
                            player.save_to_db()
                            continue
                    
                    # No unexplored directions found - get shortest path to room that DOES have an unexplored exit/room
                    player = PlayerModel.find_by_password(player_data['password'])
                    player_data = player.json()
                    travel_path = self.GraphTraversal.path_to_unexplored(player_data['currentRoomId'])
                    setattr(player, 'currentPath', json.dumps(travel_path))
                    player.save_to_db()
                    # return
                