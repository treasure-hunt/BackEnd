from flask_restful import Resource
from models.room import RoomModel


class Room(Resource):

    def get(self, id):
        room = RoomModel.find_by_title(id)
        
        if room is None:
            try:
                room = RoomModel.find_by_id(int(id))
            except ValueError:
                return {'message': 'The Room was not found.'}, 404

        if room:
            return room.json()
        return {'message': 'The Room was not found.'}, 404
