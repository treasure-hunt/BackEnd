import os
from db import db
from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from resources.room import Room
from resources.rooms import Rooms
from resources.traverse import Traverse
from resources.autotraverse import AutoTraverse
from resources.targettraverse import TargetTraverse
from lib.autotravel import AutoTravel
from lib.targettravel import TargetTravel


load_dotenv()

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True
api = Api(app)

db.init_app(app)

@app.before_first_request
def create_tables():
    db.create_all()
# Start our AutoTravel process on a separate "thread"
AutoTravel(app)
TargetTravel(app)


api.add_resource(Rooms, '/rooms')
api.add_resource(Room, '/room/<string:id>')
api.add_resource(Traverse, '/traverse/<string:direction>')
api.add_resource(AutoTraverse, '/autotraverse')
api.add_resource(TargetTraverse, '/autotraverse/<string:id>')


if __name__ == '__main__':
    app.run(port=os.getenv("PORT"), debug=False)
