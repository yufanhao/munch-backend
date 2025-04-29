from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


favorites_table = db.Table(
    "favorites",
    db.Model.metadata,
    db.Column("user_id", db.Integer, db.ForeignKey("users.id")),
    db.Column("food_id", db.Integer, db.ForeignKey("foods.id")),
)

user_food_association_table = db.Table(
    "user_food",
    db.Model.metadata,
    db.Column("user_id", db.Integer, db.ForeignKey("users.id")),
    db.Column("food_id", db.Integer, db.ForeignKey("foods.id")),
)


class Restaurant(db.Model):
    __tablename__ = "restaurants"
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String, nullable=False)
    menu = db.relationship("Food", cascade="delete")

    def __init__(self, **kwargs):
        self.address = kwargs.get("address", "")
        self.menu = kwargs.get("menu", "")

    def serialize(self):
        return {
            "id": self.id,
            "address": self.address,
            "menu": self.menu,
            # "assignments": [a.serialize_no_courses() for a in self.assignments],
            # "instructors": [i.serialize_no_courses() for i in self.instructors],
            # "students": [s.serialize_no_courses() for s in self.students],
        }

    # def serialize2(self):
    #     return {
    #         "id": self.id,
    #         "code": self.code,
    #         "name": self.name,
    #     }


class Food(db.Model):
    __tablename__ = "foods"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String, nullable=False)
    restuarant = db.Column(db.Integer, db.ForeignKey("restaurants.id"), nullable=False)
    users = db.relationship(
        "User", secondary=user_food_association_table, back_populates="foods"
    )
    favorited_by = db.relationship(
        "User", seconary=favorites_table, back_populates="favorite_foods"
    )

    def __init__(self, **kwargs):
        self.name = kwargs.get("name", "")
        self.price = kwargs.get("price", 0)
        self.category = kwargs.get("category", 0)

    # def serialize


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    phone = db.Column(db.Integer, nullable=False)
    foods = db.relationship(
        "Food", secondary=user_food_association_table, back_populates="users"
    )
    favorite_foods = db.relationship(
        "Food", secondary=favorites_table, back_populates="favorited_by"
    )

    def __init__(self, **kwargs):
        self.username = kwargs.get("username", "")
        self.password = kwargs.get("password", "")  # should probably encrypt
        self.email = kwargs.get("email", "")
        self.phone = kwargs.get("phone", 0)

    # def serialize(self):
