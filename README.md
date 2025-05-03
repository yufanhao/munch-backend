
# Munch

🥇 Built with care @ Cornell AppDev Hackathon – a platform to **track meals**, **review foods**, and **split the bill** with friends.

🍽️ A feature-rich backend for **restaurant discovery**, **receipt parsing**, and **payment coordination** is fully functional and deployed!

🔨 Backend Developers: Jason Guo, Fanhao Yu  
📱 Frontend Developers and Repository: Andrew Gao, Jimmy Chen

---

## Table of Contents

- [Application Description](#application-description)  
- [Tech Stack and Tools](#tech-stack-and-tools)  
- [System Design Overview](#system-design-overview)  
- [Database Schema](#database-schema)  
- [Relationships](#relationships)  
- [Key Features](#key-features)  
- [API Endpoints Overview](#api-endpoints-overview)  
- [Appendix](#appendix)

---

## Application Description

**MunchMate** is a social food tracking application that allows users to:

- Log their favorite meals  
- Review and rate food from local restaurants  
- Automatically extract itemized data from receipts  
- Split the bill and generate Venmo payment links  
- Scrape online restaurant menus for rapid onboarding  

It’s your all-in-one hub for food recommendations, receipts, and reviews.

---

## Tech Stack and Tools

- **Flask** – Python-based server framework for all API logic.  
- **SQLAlchemy** – ORM layer for database access and relationships.  
- **SQLite** – Lightweight, persistent backend database for rapid development.  
- **OpenAI API** – Used for:
  - Receipt parsing via `gpt-4o`
  - Fuzzy matching restaurant/food names from OCR data  
- **BeautifulSoup & Requests** – Used in custom web scraper for importing online restaurant menus.  
- **Pydantic** – Enforces JSON schema structure for parsed receipts.  
- **Docker (planned)** – Will be used for future containerization and scalable deployment.  

---

## System Design Overview

The backend was built with modularity in mind. Here's a high-level overview of the architecture:

- Flask routes are organized by resource (Users, Food, Restaurants, etc.)  
- SQLAlchemy models encapsulate all relationship logic  
- Third-party APIs (OpenAI) are used in isolation via `convert.py` and `receiptparser.py`  
- Tasks like scraping and parsing are cleanly separated for potential async or background handling  

---

## Database Schema

Our database consists of 3 core models:

- **Users**  
- **Foods**  
- **Restaurants**  

And 4 join tables that support many-to-many or enriched relationships:

- `favorites_table`  
- `user_food_association_table`  
- `user_food_reviews`  
- `requests`  

Each model implements a `.serialize()` method to cleanly output JSON.

---

## Relationships

- **Users ↔️ Foods (Consumption):** Many-to-many via `user_food_association_table`. A user can log multiple foods, and a food can be eaten by multiple users.  
- **Users ↔️ Foods (Favorites):** Many-to-many via `favorites_table`. A user can favorite many foods and vice versa.  
- **Users ↔️ Foods (Reviews):** Many-to-many via `user_food_reviews`, with additional fields `rating` and `review`. This is implemented as a full SQLAlchemy model.  
- **Restaurants → Foods:** One-to-many. A restaurant can serve many foods. This is represented by a foreign key in the `foods` table.  
- **Users ↔️ Users (Payment Requests):** Many-to-many via the `requests` table. Users can send each other payment requests, and this model includes `amount` and `message` fields for additional context.  

---

## Key Features

### 🍱 Food Logging
- Add and fetch foods  
- Sort by category  
- View aggregate ratings and reviews  

### 🏬 Restaurant Management
- Add, retrieve, and delete restaurants  
- View restaurant-specific menus  
- Scrape restaurants (currently Pho Time) with one command  

### 🧾 Receipt Parsing
- Upload receipt images  
- Parse itemized data using GPT-4o  
- Auto-split receipt items between friends (pending UI)  

### 🔍 Fuzzy Matching
- Convert scanned receipt items to best-match database entries using OpenAI  

### 💸 Payment Coordination
- Generate Venmo links pre-filled with message and amount  
- Request payments between users  

---

## API Endpoints Overview

All routes are described in the API specification. All responses are JSON-formatted and follow RESTful conventions.

### Users

- `GET /api/users/` – Get all users  
- `POST /api/users/` – Create new user  
- `GET /api/users/<id>/` – Fetch a specific user  
- `DELETE /api/users/<id>/` – Delete user by ID  
- `POST /api/users/<id>/food/` – Add review and rating for food  
- `POST /api/users/<id>/favorites/` – Favorite a food item  
- `GET /api/users/<id>/favorites/` – Get all favorited foods  
- `POST /api/payment/<id>/` – Generate Venmo link  

### Restaurants

- `GET /api/restaurants/` – Get all restaurants  
- `POST /api/restaurants/` – Add a new restaurant  
- `GET /api/restaurants/<id>/` – Get a restaurant by ID  
- `DELETE /api/restaurants/<id>/` – Delete a restaurant  
- `GET /api/restaurants/<id>/menu/` – Get full menu  
- `GET /api/restaurants/<restaurant_name>/menu/` – Get restaurant ID by name  

### Food

- `GET /api/food/` – Get all foods  
- `GET /api/food/categories/` – Get all categories  
- `GET /api/<category>/foods/` – Foods by category  
- `GET /api/food/<id>/` – Get food by ID  
- `DELETE /api/food/<id>/` – Delete food  
- `GET /api/food/<id>/name` – Get name from food ID  
- `POST /api/restaurants/<id>/food/` – Add food to restaurant  
- `POST /api/food/<id>/image/` – Update food image  
- `POST /api/food/<id>/category/` – Update food category  
- `GET /api/food/<id>/reviews/` – All reviews for food  
- `GET /api/food/<category>/reviews/` – All reviews for category  
- `POST /api/food/reviews/` – Submit a new review  

### Receipt / Conversion

- `POST /api/receipts/` – Upload receipt image (form-data: `image`)  
- `GET /api/convert/` – Match restaurant/item text to known DB entries  
- `POST /api/scrape/` – Run restaurant web scraper (currently targets Pho Time)  

---

## Appendix

### I. Authentication

Authentication is currently not enforced. Future versions may implement:

- Firebase Auth  
- OAuth for social login  
- Admin-level token permissions  

### II. Sample Response: Food Review

```json
{
  "id": 1,
  "username": "jjasonguo",
  "review": "pho 1 is delicious",
  "rating": 4.1,
  "profile_image": "http://example.com/image.jpg"
}
```

### III. Venmo Payment

```json
POST /api/payment/1/
{
  "recipient_username": "jasonguo1",
  "payment_amount": "15",
  "message": "Lunch payment"
}

Response:
{
  "payment_link": "https://venmo.com/jasonguo1?txn=pay&amount=15&note=Lunch+payment"
}
```
