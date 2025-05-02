from db import db
from flask import Flask, request
import json
from db import Restaurant, User, Food, UserFoodReview
import urllib.parse
import difflib

## for scraper
import requests
from bs4 import BeautifulSoup
import re
import argparse
##

from convert import get_closest_match
from receiptparser import parse_receipt

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

@app.route("/api/restaurants/<string:restaurant_name>/menu/")
def get_restaurant_id_by_name(restaurant_name):
    """
    Gets the id of the restaurant based on the name
    """
    restaurant = Restaurant.query.filter_by(name = restaurant_name).first()
    if restaurant is None:
        return json.dumps({"error": "Restaurant not found!"}), 404
    return json.dumps({"restaurant_id": restaurant.id}), 200


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


@app.route("/api/payment/<int:user_id>/")
def send_pay_request(user_id):
    """
    Gets all favorited items of a user
    """
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return json.dumps({"error": "User not found!"}), 404
    body = json.loads(request.data)
    recipient_username = body.get("recipient_username")
    payment_amount = body.get("payment_amount")
    message = body.get("message", "Payment")
    encoded_note = urllib.parse.quote(message)

    link = f"https://venmo.com/{recipient_username}?txn=pay&amount={payment_amount}&note={encoded_note}"

    # example :https://venmo.com/jasonguo1?txn=pay&amount=15&note=Your+payment+request

    return json.dumps({"payment_link": link}), 200


# New endpoint to run the scraper
@app.route("/api/scrape/", methods=["POST"])
def scrape_restaurant():
    """
    Runs the scraper to populate the database with Pho Time restaurant data
    """
    success = run_scraper()
    if success:
        return (
            json.dumps({"success": "Restaurant data scraped and saved to database"}),
            200,
        )
    else:
        return json.dumps({"error": "Failed to scrape restaurant data"}), 500
    
# New endpoint to go from receipt item to db item
@app.route("/api/convert/")
def get_closest_item():
    body = json.loads(request.data)
    restaurant = body.get("restaurant")
    item = body.get("item")

    dbrestaurant, dbitem = convert(restaurant,item)
    
    return json.dumps({"restaurant":dbrestaurant, "item":dbitem})


@app.route("/api/receipts/", methods=["POST"])
def upload_receipt():
    if 'image' not in request.files:
        return {"error": "No image uploaded"}, 400

    image_bytes = request.files['image'].read()
    
    try:
        result = parse_receipt(image_bytes)

        # If result is a string, parse it as JSON
        if isinstance(result, str):
            result = json.loads(result)

        # Add item IDs
        for idx, item in enumerate(result.get("items", []), start=1):
            item["id"] = idx

        # Add assigned_friends field
        result["assigned_friends"] = []

        return result, 200
    except Exception as e:
        return {"error": str(e)}, 500

## end of routes

def convert(restaurant_name, item_name):
    # Step 1: Get all restaurants and match name
    all_restaurants = Restaurant.query.all()
    restaurant_names = [r.name for r in all_restaurants]
    best_restaurant_name = get_closest_match(restaurant_name, restaurant_names, context="restaurant names")

    if not best_restaurant_name:
        return None, None

    matched_restaurant = Restaurant.query.filter_by(name=best_restaurant_name).first()
    if matched_restaurant is None:
        return None, None

    # Step 2: Get menu and match item
    menu_items = matched_restaurant.menu
    item_names = [item.name for item in menu_items]
    best_item_name = get_closest_match(item_name, item_names, context="food items from the restaurant menu")

    return matched_restaurant.name, best_item_name


def convert(restaurant_name, item_name):
    # Step 1: Get all restaurants and match name
    all_restaurants = Restaurant.query.all()
    restaurant_names = [r.name for r in all_restaurants]
    best_restaurant_name = get_closest_match(restaurant_name, restaurant_names, context="restaurant names")

    if not best_restaurant_name:
        return None, None

    matched_restaurant = Restaurant.query.filter_by(name=best_restaurant_name).first()
    if matched_restaurant is None:
        return None, None

    # Step 2: Get menu and match item
    menu_items = matched_restaurant.menu
    item_names = [item.name for item in menu_items]
    best_item_name = get_closest_match(item_name, item_names, context="food items from the restaurant menu")

    return matched_restaurant.name, best_item_name



def scrape_pho_time_data(
    url="https://www.ithacatogo.com/order/restaurant/pho-time-vietnamese-menu/45",
):
    """Scrape restaurant and menu data from Pho Time using BeautifulSoup."""
    try:
        # Send an HTTP request to the URL
        print(f"Accessing {url}...")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers)

        # Check if the request was successful
        if response.status_code != 200:
            print(f"Failed to retrieve the page. Status code: {response.status_code}")
            return None

        # Parse the HTML content
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract restaurant information
        restaurant_info = soup.find(class_="media-heading")
        if not restaurant_info:
            print("Could not find restaurant info section")
            return None

        restaurant_name = restaurant_info.text.strip()

        # Try to find the address
        restaurant_info = soup.find(class_="media-body")
        address_elem = restaurant_info.find(class_="restaurant_menu_info-addresss")
        restaurant_address = (
            address_elem.text.strip() if address_elem else "Unknown Address, Ithaca, NY"
        )

        print(f"Restaurant: {restaurant_name}")
        print(f"Address: {restaurant_address}")

        # Extract menu categories and items
        menu_data = []

        # Find all menu categories
        categories = soup.find_all(
            class_="order_restaurant--restaurant_headings panel panel-default"
        )

        for category in categories:
            # print(category)
            # category_name = category.find('h3').text.strip()
            # print(f"\nCategory: {category_name}")

            # Find menu items within this category
            menu_items = category.find_all(
                class_="order_restaurant--menu_item clearfix"
            )
            for item in menu_items:
                try:
                    # order_restaurant--menu_item_name
                    # Extract item name
                    item_title = item.find(class_="order_restaurant--menu_item_name")
                    print(item_title.text.strip())
                    if not item_title:
                        continue
                    item_name = item_title.text.strip()

                    # Extract price
                    price_elem = item.find(class_="menu_item_price")
                    print(price_elem.text.strip())
                    price_text = price_elem.text.strip() if price_elem else "0.0"

                    # Extract numeric price using regex
                    price_match = re.search(r"\$(\d+\.\d+)", price_text)
                    if price_match:
                        item_price = float(price_match.group(1))
                    else:
                        # Try to convert directly after removing $ symbol
                        try:
                            item_price = float(price_text.replace("$", "").strip())
                        except ValueError:
                            item_price = 0.0

                    # Default rating
                    avg_rating = 0  # Default average rating

                    menu_data.append(
                        {
                            "name": item_name,
                            "price": item_price,
                            "category": "tbd",
                            "description": "tbd",
                            "image_url": "fakeurl",
                            "avg_rating": avg_rating,
                        }
                    )

                    print(f"  - {item_name}: ${item_price}")

                except Exception as e:
                    print(f"Error extracting menu item: {e}")
                    continue

        return {
            "restaurant": {"name": restaurant_name, "address": restaurant_address},
            "menu_items": menu_data,
        }

    except Exception as e:
        print(f"An error occurred during scraping: {e}")
        return None


def insert_into_database(data):
    """Insert scraped data into the database."""
    if not data:
        print("No data to insert into database.")
        return False

    try:
        # Check if restaurant already exists
        existing_restaurant = Restaurant.query.filter_by(
            name=data["restaurant"]["name"]
        ).first()

        if False:
            print(
                f"Restaurant {data['restaurant']['name']} already exists. Skipping insert."
            )
            restaurant = existing_restaurant
        else:
            # Create restaurant record
            restaurant = Restaurant(
                name=data["restaurant"]["name"], address=data["restaurant"]["address"]
            )

            # Add restaurant to session
            db.session.add(restaurant)
            db.session.flush()  # Flush to get restaurant ID

        # Create food items
        for item in data["menu_items"]:
            # Check if food item already exists in this restaurant
            existing_food = Food.query.filter_by(
                name=item["name"], restaurant_id=restaurant.id
            ).first()

            if existing_food:
                print(f"Food item {item['name']} already exists. Skipping insert.")
                continue

            food = Food(
                name=item["name"],
                price=item["price"],
                category=item["category"],
                img_url=item["image_url"],  # Using image_url from scraper data
                avg_rating=item["avg_rating"],
                restaurant_id=restaurant.id,
            )
            db.session.add(food)

        # Commit all changes
        db.session.commit()
        print(
            f"Successfully added {data['restaurant']['name']} with menu items to database."
        )
        return True

    except Exception as e:
        db.session.rollback()
        print(f"Database error: {e}")
        return False


def run_scraper():
    """Run the scraper and insert data into the database."""
    print("Starting scraper...")
    scraped_data = scrape_pho_time_data()

    if scraped_data:
        print("\nInserting data into database...")
        success = insert_into_database(scraped_data)
        return success
    else:
        print("Scraping failed. No data to insert.")
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Flask app with optional scraper")
    parser.add_argument("--scrape", action="store_true", help="Run scraper on startup")
    args = parser.parse_args()

    # Run the scraper if --scrape flag is provided
    if args.scrape:
        with app.app_context():
            run_scraper()
    app.run(host="0.0.0.0", port=5000, debug=True)
