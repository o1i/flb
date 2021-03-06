from . import db


class Enrolment(db.Model):
    __tablename__ = "enrolment"
    lbinstance_id = db.Column(db.Integer, db.ForeignKey("lbinstance.id"), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    enroled_sus_ = db.relationship("User", back_populates="enroled_in")
    enroled_in_ = db.relationship("LbInstance", back_populates="enroled_sus")
    forced = db.Column(db.Boolean, default=False)

    def __repr__(self) -> str:
        return f"Enrolment(lernbuero_id: {self.lbinstance_id}, user_id: {self.user_id}, forced: {self.forced})"


class Gruppe(db.Model):
    __tablename__ = "gruppe"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    users = db.relationship("User", back_populates="gruppe")
    lernbueros = db.relationship("Lernbuero", back_populates="gruppe")
    blocks = db.relationship("Block", back_populates="gruppe", cascade="all, delete")

    def __repr__(self) -> str:
        return f"Gruppe(id={self.id}, name='{self.name}')"


class Block(db.Model):
    __tablename__ = "block"
    id = db.Column(db.Integer, primary_key=True)
    weekday = db.Column(db.Integer)
    start = db.Column(db.String(30))
    end = db.Column(db.String(30))
    gruppe_id = db.Column(db.Integer, db.ForeignKey("gruppe.id"))
    gruppe = db.relationship("Gruppe", back_populates="blocks")
    lernbueros = db.relationship("Lernbuero", back_populates="block", cascade="all, delete")

    def __repr__(self) -> str:
        return f"Gruppe(id={self.id}, weekday={self.weekday}, start='{self.start}', end='{self.end}'," \
               f"gruppe_id={self.gruppe_id})"


class Lernbuero(db.Model):
    __tablename__ = "lernbuero"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    capacity = db.Column(db.Integer())
    lp_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    lp = db.relationship("User", back_populates="lbs")
    gruppe_id = db.Column(db.Integer, db.ForeignKey("gruppe.id"))
    gruppe = db.relationship("Gruppe", back_populates="lernbueros")
    block_id = db.Column(db.Integer, db.ForeignKey("block.id"), nullable=False)
    ort = db.Column(db.String(100))
    block = db.relationship("Block", back_populates="lernbueros")
    instances = db.relationship("LbInstance", back_populates="lernbuero", lazy='dynamic', cascade="all, delete")

    def get_dict(self):
        return({
            "id": self.id,
            "name": self.name,
            "capacity": self.capacity,
            "lp_id": self.lp_id,
            "gruppe_id": self.gruppe_id,
            "block_id": self.block_id,
            "lehrer": self.lp.email,
            "ort": self.ort
        })

    def __repr__(self) -> str:
        return "Lernbuero(" + str(self.get_dict()) + ")"


class LbInstance(db.Model):
    __tablename__ = "lbinstance"
    id = db.Column(db.Integer, primary_key=True)
    lernbuero_id = db.Column(db.Integer, db.ForeignKey("lernbuero.id"), nullable=False)
    lernbuero = db.relationship("Lernbuero", back_populates="instances")
    participant_count = db.Column(db.Integer())
    start = db.Column(db.Integer())
    kw = db.Column(db.Integer())
    enroled_sus = db.relationship("Enrolment", back_populates="enroled_in_", lazy='dynamic', cascade="delete")

    def __repr__(self):
        return f"LbInstance(id= {self.id}, lernbuero_id={self.lernbuero_id}, " \
               f"participant_count={self.participant_count}, start={self.start}, kw={self.kw})"


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50))
    type = db.Column(db.String(10))
    lbs = db.relationship("Lernbuero", back_populates="lp")
    enroled_in = db.relationship("Enrolment", back_populates="enroled_sus_", lazy='dynamic', cascade="delete")
    gruppe_id = db.Column(db.Integer, db.ForeignKey("gruppe.id"))
    gruppe = db.relationship("Gruppe", back_populates="users")

    def __repr__(self) -> str:
        return f"User(email: {self.email}, level: {self.type})"
