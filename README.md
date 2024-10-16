# Items-clockIn
# FastAPI Items and Clock-In Records

This FastAPI application allows for CRUD operations on **Items** and **User Clock-In Records** with filtering capabilities.

## Setup and Run

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Arulselvan22/Items-clockIn.git
   cd Items-clockIn
2.**Install Dependencies**:
   pip install -r requirements.txt
3.**run the Application**:
   uvicorn main:app --host 0.0.0.0 --port 8000


**Endpoints**
Items API
POST /items: Create a new item.
GET /items/{id}: Retrieve an item by ID.
GET /items/filter: Filter items based on:
Email (exact match).
Expiry Date (filter items expiring after the provided date).
Insert Date (filter items inserted after the provided date).
Quantity (items with quantity greater than or equal to the provided number).
DELETE /items/{id}: Delete an item based on its ID.
PUT /items/{id}: Update an item’s details by ID (excluding the Insert Date).
Clock-In Records API
POST /clock-in: Create a new clock-in entry.
GET /clock-in/{id}: Retrieve a clock-in record by ID.
GET /clock-in/filter: Filter clock-in records based on:
Email (exact match).
Location (exact match).
Insert DateTime (clock-ins after the provided date).
DELETE /clock-in/{id}: Delete a clock-in record based on its ID.
PUT /clock-in/{id}: Update a clock-in record by ID (excluding Insert DateTime).
