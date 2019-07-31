from db import db

class PlayerModel(db.Model):
    __tablename__ = "players"

    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String, nullable=False)
    currentRoomId = db.Column(db.Integer, nullable=False)
    currentPath = db.Column(db.String)

    def __init__(self, password, currentRoomId, currentPath):
        self.password = password
        self.currentRoomId = currentRoomId
        self.currentPath = currentPath

    def json(self):
        return {
            'id': self.id,
            'password': self.password,
            'currentRoomId': self.currentRoomId,
            'currentPath': self.currentPath
            }

    @classmethod
    def find_by_password(cls, password):
        return cls.query.filter_by(password=password).first()
    
    @classmethod
    def find_all(cls):
        return cls.query.all()


    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    