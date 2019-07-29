from db import db


class RoomModel(db.Model):
    __tablename__ = "rooms"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(365), nullable=False)
    x = db.Column(db.Integer, nullable=False)  # Room coordinate
    y = db.Column(db.Integer, nullable=False)  # Room coordinate
    # Gets id of room to the north if any.
    n = db.Column(db.Integer, nullable=True)
    w = db.Column(db.Integer, nullable=True)
    e = db.Column(db.Integer, nullable=True)
    s = db.Column(db.Integer, nullable=True)

    def __init__(self, id, title, description, x, y, n, w, e, s):
        self.id = id
        self.title = title
        self.description = description
        self.x = x
        self.y = y
        self.n = n
        self.e = e
        self.w = w
        self.s = s

    def json(self):
        return {'id': self.id,
                'title': self.title,
                'description': self.description,
                'coords': {'x': self.x, 'y': self.y},
                'exits': {'n': self.n, 'w': self.w, 'e': self.e, 's': self.s}
                }

    @classmethod
    def find_by_title(cls, title):
        return cls.query.filter_by(title=title).first()

    @classmethod
    def find_by_id(cls, id):
        return cls.query.filter_by(id=id).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
