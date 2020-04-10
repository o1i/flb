from . import db


enrolment = db.Table("enrolment",
                  db.Column("lernbuero_id", db.Integer, db.ForeignKey("lernbueros.id")),
                  db.Column("user_id", db.Integer, db.ForeignKey("users.id")))


class Lernbuero(db.Model):
    __tablename__ = "lernbueros"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    start = db.Column(db.Integer())
    capacity = db.Column(db.Integer())
    participant_count = db.Column(db.Integer())
    end = db.Column(db.Integer())
    kw = db.Column(db.Integer())
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    owner = db.relationship("User", back_populates="lbs")
    enroled_sus = db.relationship("User", secondary=enrolment, back_populates="enroled_in")

    def __repr__(self) -> str:
        return f"id: {self.id}, name: {self.name}, capacity: {self.capacity}, participant_count: " \
               f"{self.participant_count}, kw: {self.kw}, owner: {self.owner}, enroled: {self.enroled_sus}"


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50))
    level = db.Column(db.String(10))
    lbs = db.relationship("Lernbuero", back_populates="owner")
    enroled_in = db.relationship("Lernbuero", secondary=enrolment, back_populates="enroled_sus")

    def __repr__(self) -> str:
        return f"email: {self.email}, level: {self.level}"