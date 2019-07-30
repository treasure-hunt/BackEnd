from flask_restful import Resource
from models.room import RoomModel


class Rooms(Resource):

    def get(self):
        rooms = RoomModel.find_all()
        if rooms is None:
            return {'message': 'No rooms were found.'}, 404

        for i in range(len(rooms)):
            rooms[i] = rooms[i].json()
        
        return rooms, 200
