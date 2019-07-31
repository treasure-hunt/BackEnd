from models.room import RoomModel


class GraphTraversal:
    def __init__(self):
        pass

    # BFS to find path.
    def path_to_target(self, current_room, target_room): # id's of rooms passed in.
        print('Creating Path', current_room, target_room)
        all_rooms = RoomModel.find_all()
        rooms_dict = {}
        # make all rooms represent their JSON object, and insert into rooms dict.
        for i in range(len(all_rooms)):
            all_rooms[i] = all_rooms[i].json()
            rooms_dict[all_rooms['id']] = all_rooms[i]
        
        visited_rooms = set()
        queue = []
        path = []
        room = rooms_dict[current_room]
        queue.append([room])

        while len(queue) > 0:
            current_path = queue.pop(0)
            prev_room = current_path[-1]
            if prev_room['id'] not in visited_rooms:
                visited_rooms.add(prev_room['id'])
                for exit_dir in rooms_dict[prev_room]['exits']:
                    new_path = current_path[:]
                    new_path.append(rooms_dict[prev_room]['exits'][exit_dir])
                    if rooms_dict[prev_room]['exits'][exit_dir] == str(target_room):
                        return self.create_path(rooms_dict, current_path)
                    else:
                        queue.append(new_path)
                        path.append(exit_dir)
        # no path found. return None
        return None

    # BFS to find path.
    def path_to_unexplored(self, current_room):  # id's of rooms passed in.
        print('Creating Path', current_room)
        all_rooms = RoomModel.find_all()
        rooms_dict = {}
        # make all rooms represent their JSON object, and insert into rooms dict.
        for i in range(len(all_rooms)):
            rooms_dict[str(all_rooms[i].json()['id'])] = all_rooms[i].json()

        visited_rooms = set()
        queue = []
        path = []
        room = current_room  #id of room
        queue.append([room])

        while len(queue) > 0:
            current_path = queue.pop(0)
            prev_room = current_path[-1]
            if prev_room is not None:
                if prev_room not in visited_rooms:
                    visited_rooms.add(prev_room)
                    for exit_dir in rooms_dict[str(prev_room)]['exits']:
                        print(rooms_dict[str(prev_room)]['exits'][exit_dir])
                        new_path = current_path[:]
                        new_path.append(rooms_dict[str(prev_room)]['exits'][exit_dir])
                        if rooms_dict[str(prev_room)]['exits'][exit_dir] == '?':
                            print(rooms_dict[str(prev_room)]['exits'][exit_dir])
                            path = {"path": self.create_path(rooms_dict, current_path)}
                            return path
                        else:
                            queue.append(new_path)
                            path.append(exit_dir)
        # no path found. return None
        return None

    def create_path(self, rooms, path):
        index = 0
        directions = []
        while index < len(path) - 1:
            current_paths = rooms[str(path[index])]['exits']
            targetId = path[index + 1]
            for pathway in current_paths:
                if rooms[str(path[index])]['exits'][pathway] == targetId:
                    print(pathway)
                    directions.append(pathway)
            
            index += 1
        
        return directions
        

