from db import db


class RoomModel(db.Model):
    __tablename__ = "rooms"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(365), nullable=False)
    x = db.Column(db.Integer, nullable=False)  # Room coordinate
    y = db.Column(db.Integer, nullable=False)  # Room coordinate
    # Gets id of room to the north if any.
    n = db.Column(db.String, nullable=True)
    w = db.Column(db.String, nullable=True)
    e = db.Column(db.String, nullable=True)
    s = db.Column(db.String, nullable=True)
    elevation = db.Column(db.Integer, nullable=True)
    terrain = db.Column(db.String(80), nullable=False)

    def __init__(self, id, title, description, x, y, n, w, e, s, elevation, terrain):
        self.id = id
        self.title = title
        self.description = description
        self.x = x
        self.y = y
        self.n = n
        self.e = e
        self.w = w
        self.s = s
        self.elevation = elevation
        self.terrain = terrain

    def json(self):
        return {'id': self.id,
                'title': self.title,
                'description': self.description,
                'coords': {'x': self.x, 'y': self.y},
                'exits': {'n': self.n, 'w': self.w, 'e': self.e, 's': self.s},
                'elevation': self.elevation,
                'terrain': self.terrain
                }

    @classmethod
    def find_by_title(cls, title):
        return cls.query.filter_by(title=title).first()

    @classmethod
    def find_by_id(cls, id):
        return cls.query.filter_by(id=id).first()

    @classmethod
    def find_all(cls):
        return cls.query.all()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
