
### IV. Get All Users

```json
GET /api/users/
Response:
<HTTP STATUS CODE 200>
{
  "users": [
    {
      "id": <USER_ID>,
      "username": "jjasonguo",
      "email": "jhg294@cornell.edu",
      "phone": "7814676237",
      "venmo": "jasonguo1",
      "profile_image": "http://example.com/image.jpg",
      "foods": [<serialized food>],
      "received_requests": [<serialized requests>],
      "reviews": [
        {
          "food": [<simple serialized foods>],
          "rating": "9.5",
          "review": "Great meal"
        }
      ]
    }
  ]
}
```

### V. Create a New User

```json
POST /api/users/
Request:
{
  "username": "jjasonguo",
  "password": "password123",
  "email": "jhg294@cornell.edu",
  "phone": "7814676237",
  "profile_image": "http://example.com/image.jpg"
}

Response:
<HTTP STATUS CODE 201>
{
  "users": [
    {
      "id": <USER_ID>,
      "username": "jjasonguo",
      "email": "jhg294@cornell.edu",
      "phone": "7814676237",
      "venmo": "jasonguo1",
      "profile_image": "http://example.com/image.jpg",
      "foods": [<serialized food>],
      "received_requests": [<serialized requests>],
      "reviews": [
        {
          "food": [<simple serialized foods>],
          "rating": "4.5",
          "review": "Great meal"
        }
      ]
    }
  ]
}
```

### VI. Get a Specific User

```json
GET /api/users/{id}/
Response:
<HTTP STATUS CODE 200>
{
  "users": [
    {
      "id": <USER_ID>,
      "username": "jjasonguo",
      "email": "jhg294@cornell.edu",
      "phone": "7814676237",
      "venmo": "jasonguo1",
      "profile_image": "http://example.com/image.jpg",
      "foods": [<serialized food>],
      "received_requests": [<serialized requests>],
      "reviews": [
        {
          "food": [<simple serialized foods>],
          "rating": "4.5",
          "review": "Great meal"
        }
      ]
    }
  ]
}
```

### VII. Delete a Specific User

```json
DELETE /api/users/{id}/
Response:
<HTTP STATUS CODE 200>
{
  "users": [
    {
      "id": <USER_ID>,
      "username": "jjasonguo",
      "email": "jhg294@cornell.edu",
      "phone": "7814676237",
      "venmo": "jasonguo1",
      "profile_image": "http://example.com/image.jpg",
      "foods": [<serialized food>],
      "received_requests": [<serialized requests>],
      "reviews": [
        {
          "food": [<simple serialized foods>],
          "rating": "4.5",
          "review": "Great meal"
        }
      ]
    }
  ]
}
```
