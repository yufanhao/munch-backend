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
    name = db.Column(db.String, nullable=False)
    address = db.Column(db.String, nullable=False)
    menu = db.relationship("Food", cascade="delete")

    def __init__(self, **kwargs):
        self.name = kwargs.get("name", "")
        self.address = kwargs.get("address", "")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "address": self.address,
            "menu": [food.simple_serialize() for food in self.menu],
        }

    def simple_serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "address": self.address,
        }


class Food(db.Model):
    __tablename__ = "foods"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String, nullable=False)
    restaurant_id = db.Column(
        db.Integer, db.ForeignKey("restaurants.id"), nullable=False
    )
    users = db.relationship(
        "User", secondary=user_food_association_table, back_populates="foods"
    )
    favorited_by = db.relationship(
        "User", secondary=favorites_table, back_populates="favorite_foods"
    )

    def __init__(self, **kwargs):
        self.name = kwargs.get("name", "")
        self.price = kwargs.get("price", 0)
        self.category = kwargs.get("category", 0)
        self.restaurant_id = kwargs.get("restaurant_id", 0)

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "category": self.category,
            "restaurant": Restaurant.query.filter_by(id=self.restaurant_id)
            .first()
            .simple_serialize(),
        }

    def simple_serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "category": self.category,
        }


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
    favorite_foods = db.rexlationship(
        "Food", secondary=favorites_table, back_populates="favorited_by"
    )

    def __init__(self, **kwargs):
        self.username = kwargs.get("username", "")
        self.password = kwargs.get("password", "")  # should probably encrypt
        self.email = kwargs.get("email", "")
        self.phone = kwargs.get("phone", 0)

    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "phone": self.phone,
            "foods": [food.simple_serialize() for food in self.foods],
            "favorites": [food.simple_serialize() for food in self.favorite_foods],
        }
