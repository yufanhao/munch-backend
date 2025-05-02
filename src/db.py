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
            "menu": [food.serialize() for food in self.menu],
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
    image_url = db.Column(db.String, nullable=False)
    avg_rating = db.Column(db.Integer, nullable=False)
    restaurant_id = db.Column(
        db.Integer, db.ForeignKey("restaurants.id"), nullable=False
    )
    user_reviews = db.relationship("UserFoodReview", back_populates="food")
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
        self.image_url = kwargs.get("image_url", "")
        self.avg_rating = kwargs.get("avg_rating", "")

    def update_avg_rating(self, new_avg_rating):
        self.avg_rating = new_avg_rating
        db.session.commit()

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "category": self.category,
            "image_url": self.image_url,
            "avg_rating": self.avg_rating,
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
            "image_url": self.image_url,
            "avg_rating": self.avg_rating,
        }


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    phone = db.Column(db.Integer, nullable=False)
    venmo = db.Column(db.String, nullable=False)
    profile_image = db.Column(db.String, nullable=False)

    food_reviews = db.relationship("UserFoodReview", back_populates="user")
    sent_requests = db.relationship(
        "Request", foreign_keys="[Request.sender_id]", back_populates="sender"
    )
    received_requests = db.relationship(
        "Request", foreign_keys="[Request.receiver_id]", back_populates="receiver"
    )

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
        self.venmo = kwargs.get("venmo", "")
        self.profile_image = kwargs.get("profile_image", "")

    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "phone": self.phone,
            "venmo": self.venmo,
            "profile_image": self.profile_image,
            "foods": [food.simple_serialize() for food in self.foods],
            "favorites": [food.simple_serialize() for food in self.favorite_foods],
            "sent_requests": [sent.serialize() for sent in self.sent_requests],
            "received_requests": [
                received.serialize() for received in self.received_requests
            ],
            "reviews": [
                {
                    "food": review.food.simple_serialize(),
                    "rating": review.rating,
                    "review": review.review,
                }
                for review in self.food_reviews
            ],
        }


class UserFoodReview(db.Model):
    __tablename__ = "user_food_reviews"
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    food_id = db.Column(db.Integer, db.ForeignKey("foods.id"), primary_key=True)
    rating = db.Column(db.Integer, nullable=False)
    review = db.Column(db.String, nullable=False)

    user = db.relationship("User", back_populates="food_reviews")
    food = db.relationship("Food", back_populates="user_reviews")


class Request(db.Model):
    __tablename__ = "requests"
    sender_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    receiver_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    amount = db.Column(db.Integer, nullable=False)
    message = db.Column(db.String, nullable=False)

    sender = db.relationship(
        "User", foreign_keys=[sender_id], back_populates="sent_requests"
    )
    receiver = db.relationship(
        "User", foreign_keys=[receiver_id], back_populates="received_requests"
    )

    def serialize(self):
        return {
            "sender_id": self.sender_id,
            "receiver_id": self.receiver_id,
            "ampunt": self.amount,
            "message": self.message,
        }
