from db import db
from flask import Flask, request
import json
from db import Restaurant, User, Food


app = Flask(__name__)
db_filename = "munch.db"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///%s" % db_filename
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = False

db.init_app(app)
with app.app_context():
    db.create_all()

# User endpoints


@app.route("/api/users/")
def get_all_users():
    """
    Gets all users in the DB
    """
    users = []
    for user in User.query.all():
        users.append(user.serialize())
    return json.dumps({"users": users}), 200


@app.route("/api/users/", methods=["POST"])
def create_user():
    """
    Creates a new user in the DB
    """
    body = json.loads(request.data)
    username = body.get("username")
    password = body.get("password")
    email = body.get("email")
    phone = body.get("phone")
    if username is None or password is None or email is None or phone is None:
        return json.dumps({"error": "Invalid input"}), 400
    new_user = User(**body)
    db.session.add(new_user)
    db.session.commit()
    return json.dumps(new_user.serialize()), 201


@app.route("/api/users/<int:user_id>/")
def get_user_by_id(user_id):
    """
    Gets a user by id from DB
    """
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return json.dumps({"error": "User not found!"}), 404
    return json.dumps(user.serialize()), 200


@app.route("/api/users/<int:user_id>/", methods=["DELETE"])
def delete_user_by_id(user_id):
    """
    Deletes a user by its id from DB
    """
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return json.dumps({"error": 404})
    db.session.delete(user)
    db.session.commit()
    return json.dumps(user.serialize()), 200


# Restaurant endpoints


@app.route("/api/restaurants/")
def get_all_restaurants():
    """
    Gets all restaurants in the DB
    """
    restaurants = []
    for restaurant in Restaurant.query.all():
        restaurants.append(restaurant.serialize())
    return json.dumps({"restaurants": restaurants}), 200


@app.route("/api/restaurants/", methods=["POST"])
def create_restaurant():
    """
    Creates a new restaurant in the DB
    """
    body = json.loads(request.data)
    name = body.get("name")
    address = body.get("address")
    if name is None or address is None:
        return json.dumps({"error": "Invalid input"}), 400
    new_restaurant = Restaurant(**body)
    db.session.add(new_restaurant)
    db.session.commit()
    return json.dumps(new_restaurant.serialize()), 201


@app.route("/api/restaurants/<int:restaurant_id>/")
def get_restaurant_by_id(restaurant_id):
    """
    Gets a restaurant by its id from DB
    """
    restaurant = Restaurant.query.filter_by(id=restaurant_id).first()
    if restaurant is None:
        return json.dumps({"error": "Restaurant not found"}), 404
    return json.dumps(restaurant.serialize()), 200


@app.route("/api/restaurants/<int:restaurant_id>/", methods=["DELETE"])
def delete_restaurant_by_id(restaurant_id):
    """
    Deletes a restaurant by its id from DB
    """
    restaurant = User.query.filter_by(id=restaurant_id).first()
    if restaurant is None:
        return json.dumps({"error": 404})
    db.session.delete(restaurant)
    db.session.commit()
    return json.dumps(restaurant.serialize()), 200


# Food endpoints


@app.route("/api/food/")
def get_all_food():
    """
    Gets all food items in the DB
    """
    foods = []
    for food in Food.query.all():
        foods.append(food.serialize())
    return json.dumps({"food items": foods}), 200


@app.route("/api/restaurants/<int:restaurant_id>/food/", methods=["POST"])
def create_food(restaurant_id):
    """
    Creates a new food and adds it to a restaurant
    """
    restaurant = Restaurant.query.filter_by(id=restaurant_id).first()
    if restaurant is None:
        return json.dumps({"error": "Restaurant not found!"}), 404
    body = json.loads(request.data)
    name = body.get("name")
    price = body.get("price")
    category = body.get("category")
    if name is None or price is None or category is None:
        return json.dumps({"error": "Invalid input"}), 400
    new_food = Food(
        name=name, price=price, category=category, restaurant_id=restaurant_id
    )
    db.session.add(new_food)
    db.session.commit()
    return json.dumps(new_food.serialize()), 201


@app.route("/api/food/<int:food_id>/")
def get_food_by_id(food_id):
    """
    Gets a food item by id from DB
    """
    food = Food.query.filter_by(id=food_id).first()
    if food is None:
        return json.dumps({"error": "Food not found!"}), 404
    return json.dumps(food.serialize()), 200


@app.route("/api/users/<int:user_id>/food/", methods=["POST"])
def add_food_to_user(user_id):
    """
    Assigns a food to a user
    """
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return json.dumps({"error": "User not found!"}), 404
    body = json.loads(request.data)
    food_id = body.get("food_id")
    food = Food.query.filter_by(id=food_id).first()
    if food is None:
        return json.dumps({"error": "Food not found!"}), 404
    user.foods.append(food)
    db.session.commit()
    return json.dumps(user.serialize()), 200


@app.route("/api/users/<int:user_id>/favorites/", methods=["POST"])
def add_favorite(user_id):
    """
    Assigns a food to a user's favorite foods
    """
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return json.dumps({"error": "User not found!"}), 404
    body = json.loads(request.data)
    food_id = body.get("food_id")
    food = Food.query.filter_by(id=food_id).first()
    if food is None:
        return json.dumps({"error": "Food not found!"}), 404
    user.favorite_foods.append(food)
    db.session.commit()
    return json.dumps(user.serialize()), 200


@app.route("/api/users/<int:user_id>/favorites/")
def get_favorites(user_id):
    """
    Gets all favorited items of a user
    """
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return json.dumps({"error": "User not found!"}), 404

    favorited = [food.serialize() for food in user.favorite_foods]
    return json.dumps({"favorited_foods": favorited}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
