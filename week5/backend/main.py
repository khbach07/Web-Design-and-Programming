from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

class ItemCreate(BaseModel):
    name: str
    price: float

class ItemUpdate(BaseModel):
    name: str | None = None
    price: float | None = None

class ItemPublic(BaseModel):
    id: int
    name: str
    price: float

class ItemListResponse(BaseModel):
    items: list[ItemPublic]
    total: int
    skip: int
    limit: int

class HousePriceRequest(BaseModel):
    area_sqm: float = Field(gt=0)
    bedrooms: int = Field(ge=0)
    distance_to_center_km: float = Field(ge=0)

class HousePricePrediction(BaseModel):
    predicted_price: float
    currency: str = "VND"

app = FastAPI()
app.mount("/static", StaticFiles(directory="../frontend"), name="static")

_items: list[ItemPublic] = []
_next_id: int = 0

def _find(item_id: int) -> ItemPublic | None:
    for item in _items:
        if item.id == item_id:
            return item
    return None

def _name_exists(name: str, exclude_id: int | None = None) -> bool:
    for item in _items:
        if item.name.lower() == name.lower() and item.id != exclude_id:
            return True
    return False

@app.get("/")
def read_root():
    return FileResponse("../frontend/week5.html")

## GET AN ITEM
@app.get("/items/{item_id}")
def read_item(item_id: int):

    item = _find(item_id)

    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    return item

## GET ITEMS
@app.get("/items", response_model=ItemListResponse)
def list_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    min_price: float | None = None,
    max_price: float | None = None,
    q: str | None = Query(None, min_length=2),
    sort_by: str = Query("id", pattern="^(id|name|price)$"),
    order: str = Query("asc", pattern="^(asc|desc)$"),
):
    result = _items

    if min_price is not None:
        result = [item for item in result if item.price >= min_price]
    if max_price is not None:
        result = [item for item in result if item.price <= max_price]
    if q is not None:
        result = [item for item in result if q.lower() in item.name.lower()]

    reverse = (order == "desc")
    result = sorted(result, key=lambda item: getattr(item, sort_by), reverse=reverse)

    total = len(result)
    paged = result[skip : skip + limit]

    return ItemListResponse(items=paged, total=total, skip=skip, limit=limit)

## CREATE AN ITEM
@app.post("/items", response_model=ItemPublic, status_code=201)
def create_item(data: ItemCreate):
        global _next_id
        if _name_exists(data.name):
            raise HTTPException(status_code=409, detail="Item with this name already exists")
        newItem = ItemPublic(id=_next_id, name=data.name, price=data.price)
        _items.append(newItem)
        _next_id += 1
        return newItem

## UPDATE AN ITEM
@app.put("/items/{item_id}", response_model=ItemPublic)
def update_item(item_id: int, data: ItemCreate):
    item = _find(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    if data.name.lower() != item.name.lower() and _name_exists(data.name, exclude_id=item_id):
        raise HTTPException(status_code=409, detail="Item with this name already exists")

    updated = ItemPublic(id=item_id,name=data.name,price=data.price)
    index = _items.index(item)
    _items[index] = updated

    return updated

## PARTIALLY UPDATE AN ITEM
@app.patch("/items/{item_id}", response_model=ItemPublic)
def patch_item(item_id: int, data: ItemUpdate):
     item = _find(item_id)
     if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

     update_data = data.model_dump(exclude_unset=True)

     if "name" in update_data and update_data["name"].lower() != item.name.lower():
        if _name_exists(update_data["name"], exclude_id=item_id):
            raise HTTPException(status_code=409, detail="Item with this name already exists")
        
     index = _items.index(item)
     updated = item.model_copy(update=update_data)
     _items[index] = updated
     return updated

## DELETE AN ITEM
@app.delete("/items/{item_id}", status_code=204)
def delete_item(item_id: int):
    item = _find(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    _items.remove(item)
    return None

## PREDICT HOUSE PRICE
@app.post("/predict/house-price", response_model=HousePricePrediction)
def predict_house_price(data: HousePriceRequest):
    price = (
        data.area_sqm * 15_000_000
        - data.distance_to_center_km * 5_000_000
        + data.bedrooms * 20_000_000
    )
    return HousePricePrediction(predicted_price=price)

