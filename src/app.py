from db import db
from flask import Flask, request
import json
from db import Restaurant, User, Food, UserFoodReview, Request


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
    profile_image = body.get("profile_image")
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
        return json.dumps({"error": "User not found!"}), 404
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
    restaurant = Restaurant.query.filter_by(id=restaurant_id).first()
    if restaurant is None:
        return json.dumps({"error": "Restaurant not found!"}), 404
    db.session.delete(restaurant)
    db.session.commit()
    return json.dumps(restaurant.serialize()), 200


@app.route("/api/restaurants/<int:restaurant_id>/menu/")
def get_menu(restaurant_id):
    """
    Gets all food items on a restaurant's menu
    """
    restaurant = Restaurant.query.filter_by(id=restaurant_id).first()
    menu = []
    if restaurant is None:
        return json.dumps({"error": "Restaurant not found!"}), 404
    for food in restaurant.menu:
        menu.append(food.simple_serialize())
    return json.dumps(menu), 200


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
    img_url = body.get("img_url")
    if name is None or price is None or category is None:
        return json.dumps({"error": "Invalid input"}), 400
    new_food = Food(
        name=name,
        price=price,
        category=category,
        img_url=img_url,
        avg_rating=0,
        restaurant_id=restaurant_id,
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


@app.route("/api/food/<int:food_id>/name")
def get_food_name_by_id(food_id):
    """
    Gets a food item's name by id from DB
    """
    food = Food.query.filter_by(id=food_id).first()
    if food is None:
        return json.dumps({"error": "Food not found!"}), 404
    return json.dumps({"name": food.name}), 200


@app.route("/api/users/<int:user_id>/food/", methods=["POST"])
def add_food_to_user(user_id):
    """
    Assigns a food to a user, updates ratings and adds the user's review
    """
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return json.dumps({"error": "User not found!"}), 404
    body = json.loads(request.data)
    food_id = body.get("food_id")
    rating = body.get("rating")
    review = UserFoodReview(
        user_id=user_id, food_id=food_id, rating=rating, review=body.get("review")
    )
    food = Food.query.filter_by(id=food_id).first()
    if food is None:
        return json.dumps({"error": "Food not found!"}), 404
    review_count = UserFoodReview.query.filter_by(food_id=food_id).count()
    new_avg_rating = (food.avg_rating * review_count + rating) / (review_count + 1)
    food.update_avg_rating(new_avg_rating)
    user.foods.append(food)
    db.session.add(review)
    db.session.commit()
    return json.dumps(user.serialize()), 201


@app.route("/api/food/<int:food_id>/reviews/")
def get_reviews(food_id):
    """
    Gets all reviews associated with a food item
    """
    all_reviews = []
    reviews = UserFoodReview.query.filter_by(food_id=food_id).all()
    if reviews is None:
        return json.dumps({"error": "Reviews not found!"}), 404

    for item in reviews:
        user = item.user
        all_reviews.append(
            {
                "id": user.id,
                "username": user.username,
                "review": item.review,
                "rating": item.rating,
                "profile_image": user.profile_image,
            }
        )
    return json.dumps(all_reviews), 200


@app.route("/api/food/categories/")
def get_all_categories():
    """
    Gets all food categories
    """
    foods = Food.query.all()
    categories = []
    for food in foods:
        if food.category not in categories:
            categories.append(food.category)
    return json.dumps(categories), 200


@app.route("/api/food/<string:category>/reviews/")
def get_reviews_by_category(category):
    """
    Gets all reviews associated with a food item
    """
    all_reviews = []
    foods = Food.query.filter_by(category=category).all()
    if foods is None:
        return json.dumps({"error": "Food not found!"}), 404

    for food in foods:
        reviews = UserFoodReview.query.filter_by(food_id=food.id).all()
        if reviews is None:
            return json.dumps({"error": "Reviews not found!"}), 404

        for item in reviews:
            user = item.user
            all_reviews.append(
                {
                    "id": user.id,
                    "username": user.username,
                    "review": item.review,
                    "rating": item.rating,
                    "profile_image": user.profile_image,
                }
            )
    return json.dumps(all_reviews), 200


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


# Request enpoints


@app.route("/api/users/<int:user_id>/requests/received/")
def get_received_requests(user_id):
    """
    Gets all requests a user has received
    """
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return json.dumps({"error": "User not found!"}), 404
    received_requests = [
        received_request.serialize() for received_request in user.received_requests
    ]
    return json.dumps({"received_requests": received_requests}), 200


@app.route("/api/users/<int:user_id>/requests/sent/")
def get_sent_requests(user_id):
    """
    Gets all requests a user has sent
    """
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return json.dumps({"error": "User not found!"}), 404
    sent_requests = [sent_request.serialize() for sent_request in user.sent_requests]
    return json.dumps({"sent_requests": sent_requests}), 200


@app.route("/api/users/<int:sender_id>/requests/create", methods=["POST"])
def create_request(sender_id):
    """
    Creates a new request and assigns it to a user
    """
    body = json.loads(request.data)
    sender = User.query.filter_by(id=sender_id).first()
    receiver_id = body.get("receiver_id")
    receiver = User.query.filter_by(id=receiver_id).first()
    if sender is None or receiver is None:
        return json.dumps({"error": "User not found!"}), 404

    amount = body.get("amount")
    message = body.get("message")
    new_request = Request(
        sender_id=sender_id, receiver_id=receiver_id, amount=amount, message=message
    )
    # sender.sent_requests.append(new_request)
    db.session.add(new_request)
    db.session.commit()
    return json.dumps(new_request.serialize()), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
