import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pymongo import ASCENDING
import ssl
from fastapi import Query

load_dotenv()

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

mongodb_uri = os.getenv("MONGO_URI")
client = MongoClient(mongodb_uri)
db = client['FastAPIApp']
items_collection = db['Items']
clockin_collection = db['ClockInRecords']



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




class Item(BaseModel):
    name: str
    email: str
    item_name: str
    quantity: int
    expiry_date: str  # YYYY-MM-DD

class UpdateItem(BaseModel):
    name: Optional[str]
    email: Optional[str]
    item_name: Optional[str]
    quantity: Optional[int]
    expiry_date: Optional[str]

class ClockInRecord(BaseModel):
    email: str
    location: str

class UpdateClockInRecord(BaseModel):
    email: Optional[str]
    location: Optional[str]

# Helper function for converting ObjectId to string
def item_serializer(item) -> dict:
    return {
        "id": str(item["_id"]),
        "name": item["name"],
        "email": item["email"],
        "item_name": item["item_name"],
        "quantity": item["quantity"],
        "expiry_date": item["expiry_date"],
        "insert_date": item["insert_date"]
    }

def clockin_serializer(record) -> dict:
    return {
        "id": str(record["_id"]),
        "email": record["email"],
        "location": record["location"],
        "insert_datetime": record["insert_datetime"]
    }

# Items APIs 
app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve the frontend
@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open("static/index.html") as f:
        return HTMLResponse(content=f.read())
@app.post("/items")
def create_item(item: Item):
    insert_date = datetime.utcnow().strftime('%Y-%m-%d')
    item_data = {**item.dict(), "insert_date": insert_date}
    items_collection.insert_one(item_data)
    return {"message": "Item created successfully"}


@app.get("/items")
def get_all_items():
    items = items_collection.find()
    return [item_serializer(item) for item in items]

@app.get("/items/{id}")
def get_item(id: str):
    try:
        item = items_collection.find_one({"_id": ObjectId(id)})
        if item:
            return item_serializer(item)
        raise HTTPException(status_code=404, detail="Item not found")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID format")

@app.get("/items/filter")
async def filter_items(
    email: Optional[str] = Query(None),
    expiry_date: Optional[str] = Query(None),
    insert_date: Optional[str] = Query(None),
    quantity: Optional[int] = Query(None),
    id: Optional[str] = Query(None)  # Adding ID as an optional filter
):
    query = {}
    
    if email:
        query["email"] = email  
    
    
    if expiry_date:
        
        try:
            datetime.strptime(expiry_date, '%Y-%m-%d')  
            query["expiry_date"] = {"$gte": expiry_date}
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid expiry_date format. Use YYYY-MM-DD.")
    
    if insert_date:
       
        try:
            datetime.strptime(insert_date, '%Y-%m-%d')  # Check date format
            query["insert_date"] = {"$gte": insert_date}
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid insert_date format. Use YYYY-MM-DD.")
    
    if quantity is not None:
        query["quantity"] = {"$gte": quantity}
    
  
    results = await items_collection.find(query).to_list(length=100)
    
    if not results:
        return {"message": "No items found matching the criteria"}
    
    return results


@app.get("/items/aggregate")
def aggregate_items():
    pipeline = [
        {"$group": {"_id": "$email", "count": {"$sum": 1}}}
    ]
    result = list(items_collection.aggregate(pipeline))
    return result

@app.put("/items/{id}")
def update_item(id: str, update_data: UpdateItem):
    try:
        updated_item = {k: v for k, v in update_data.dict().items() if v is not None}
        if updated_item:
            result = items_collection.update_one({"_id": ObjectId(id)}, {"$set": updated_item})
            if result.matched_count:
                return {"message": "Item updated successfully"}
            else:
                raise HTTPException(status_code=404, detail="Item not found")
        raise HTTPException(status_code=400, detail="No valid fields to update")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID format")

@app.delete("/items/{id}")
def delete_item(id: str):
    try:
        result = items_collection.delete_one({"_id": ObjectId(id)})
        if result.deleted_count:
            return {"message": "Item deleted successfully"}
        raise HTTPException(status_code=404, detail="Item not found")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID format")

# Clock-In APIs
@app.post("/clock-in")
def create_clockin(record: ClockInRecord):
    insert_datetime = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    clockin_data = {**record.dict(), "insert_datetime": insert_datetime}
    clockin_collection.insert_one(clockin_data)
    return {"message": "Clock-In record created successfully"}

@app.get("/clock-in")
def get_all_clockins():
    records = clockin_collection.find()
    return [clockin_serializer(record) for record in records]

@app.get("/clock-in/{id}")
def get_clockin(id: str):
    try:
        record = clockin_collection.find_one({"_id": ObjectId(id)})
        if record:
            return clockin_serializer(record)
        raise HTTPException(status_code=404, detail="Record not found")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID format")



@app.get("/clock-in/filter")
async def filter_clock_in_records(
    email: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    insert_datetime: Optional[str] = Query(None)
):
    query = {}
    if email:
        query["email"] = email
    if location:
        query["location"] = location
    if insert_datetime:
        query["insert_datetime"] = {"$gte": insert_datetime}
    
    # Execute the query and return the filtered clock-in records
    results = await clockin_collection.find(query).sort("insert_datetime", ASCENDING).to_list(length=100)
    return results


@app.put("/clock-in/{id}")
def update_clockin(id: str, update_data: UpdateClockInRecord):
    try:
        updated_record = {k: v for k, v in update_data.dict().items() if v is not None}
        if updated_record:
            result = clockin_collection.update_one({"_id": ObjectId(id)}, {"$set": updated_record})
            if result.matched_count:
                return {"message": "Clock-In record updated successfully"}
            else:
                raise HTTPException(status_code=404, detail="Record not found")
        raise HTTPException(status_code=400, detail="No valid fields to update")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID format")

@app.delete("/clock-in/{id}")
def delete_clockin(id: str):
    try:
        result = clockin_collection.delete_one({"_id": ObjectId(id)})
        if result.deleted_count:
            return {"message": "Record deleted successfully"}
        raise HTTPException(status_code=404, detail="Record not found")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID format")