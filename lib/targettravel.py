import time
import json
from sqlalchemy import orm
from threading import Thread
from models.room import RoomModel
from models.player import PlayerModel
from resources.traverse import Traverse
from lib.graphtraversal import GraphTraversal
import requests


class TargetTravel(Thread):
    def __init__(self, app):
        Thread.__init__(self)
        self.name = "targettravel"
        self.daemon = True
        self.GraphTraversal = GraphTraversal()
        self.app = app
        self.start()

    def save_player(self, player):
        player_data = player.json()
        find_player = player.find_by_password(player_data["password"])
        
        if find_player:
            find_player.save_to_db()

    def run(self):
        self.start_loop()

    def start_loop(self):
        with self.app.app_context():
            directions = ['n', 'e', 's', 'w']

            while True:
                time.sleep(1)
                # Get all players who are automatically traversing
                traversing_players = PlayerModel.find_all_by_single_path(True)
                if not traversing_players or len(traversing_players) < 1:
                    print('No one traversing via target. Skip.')
                    continue
                # Make every record of traversing_players the JSON dict available.
                for player in traversing_players:
                    player_data = player.json()
                    # Only register next move if the player is passed cooldown.
                    if int(time.time()) < player_data['nextAvailableMove'] + 2:
                        time.sleep(player_data['nextAvailableMove'] + 1 - int(time.time()))

                    player_path = json.loads(player_data["currentPath"])["path"]
                    # Player has a path, travel based on it.
                    if len(player_path) > 0:
                        direction = player_path.pop(0)
                        traverse_to_room = Traverse.TraverseOnce(player_data['password'], direction)
                        traverse_to_room = traverse_to_room[0]

                        if len(traverse_to_room['errors']) > 0:
                            print(traverse_to_room['errors'], "ERROR", traverse_to_room['cooldown'])
                            setattr(player, 'nextAvailableMove', (int(time.time()) + 2 + int(traverse_to_room['cooldown'])))
                            self.save_player(player)
                            # player.save_to_db()
                            continue

                        setattr(player, 'nextAvailableMove', int(time.time()) + 2 + int(traverse_to_room['cooldown']))
                        setattr(player, 'currentRoomId', traverse_to_room['room_id'])
                        setattr(player, 'currentPath', json.dumps({"path": player_path})) 
                        # player.save_to_db()
                        self.save_player(player)
                        print(f"player traveled {direction} to {traverse_to_room['room_id']}")
                        continue
                        # return traverse_to_room
                    
                    else:
                        print("player has finished traversal")
                        delete_player = player.find_by_password(player_data["password"])
                        print(delete_player, "tester")
                        if delete_player:
                            delete_player.delete_from_db()

