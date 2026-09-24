from re import L

from fastapi import FastAPI, HTTPException, Query, Request, Depends, APIRouter, Header
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware
import time

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

app.add_middleware(CORSMiddleware, allow_origins=["http://127.0.0.1:5500"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()

    response = await call_next(request)

    process_time = time.perf_counter() - start

    print(
        f"{request.method} {request.url.path} "
        f"- {process_time:.4f}s"
    )

    response.headers["X-Process-Time"] = f"{process_time:.4f}"

    return response


@app.middleware("http")
async def catch_exceptions(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as exc:
        print(f"Unhandled error on {request.url.path}: {exc}")
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})

@app.middleware("http")
async def m1(request: Request, call_next):
    print("m1 before")
    response = await call_next(request)
    print("m1 after")
    return response

@app.middleware("http")
async def m2(request: Request, call_next):
    print("m2 before")
    response = await call_next(request)
    print("m2 after")
    return response

# @app.middleware("http")
def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != "secret-api-key":
        raise HTTPException(status_code=401, detail="API key err")
    return x_api_key

def pagination(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    min_price: float | None = None,
    max_price: float | None = None,
    q: str | None = Query(None, min_length=2),
    sort_by: str = Query("id", pattern="^(id|name|price)$"),
    order: str = Query("asc", pattern="^(asc|desc)$"),
):
    return {
        "skip": skip,
        "limit": limit,
        "min_price": min_price,
        "max_price": max_price,
        "q": q,
        "sort_by": sort_by,
        "order": order
    }


# ADMIN Routes
admin = APIRouter(
    prefix="/admin",
    dependencies=[Depends(verify_api_key)]
)


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
@admin.get("/items/{item_id}")
def read_item(item_id: int):
    item = _find(item_id)

    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    return item

## GET ITEMS
@admin.get("/items", response_model=ItemListResponse)
def list_items(page: dict = Depends(pagination)):
    result = _items

    skip = page["skip"]
    limit = page["limit"]
    min_price = page["min_price"]
    max_price = page["max_price"]
    q = page["q"]
    sort_by = page["sort_by"]
    order = page["order"]

    if min_price is not None:
        result = [item for item in result if item.price >= min_price]

    if max_price is not None:
        result = [item for item in result if item.price <= max_price]

    if q is not None:
        result = [item for item in result if q.lower() in item.name.lower()]

    reverse = order == "desc"

    result = sorted(
        result,
        key=lambda item: getattr(item, sort_by),
        reverse=reverse
    )

    total = len(result)
    paged = result[skip:skip + limit]

    return ItemListResponse(
        items=paged,
        total=total,
        skip=skip,
        limit=limit
    )

app.include_router(admin)

# @app.get("/items")
# def list_items(page: dict = Depends(pagination)):
#     print("-> getting items")
#     skip = page.get("skip")
#     limit = page.get("limit")
#     return _items[skip : skip + limit]

@app.get("/services")
def list_services(page: dict = Depends(pagination)):
    skip = page["skip"]
    limit = page["limit"]

    return []

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

_cart = []

@app.post("/cart/add")
def add_card_item(item: str):
    _cart.append(item)
    return _cart

@app.get("/cart")
def get_cart():
    return _cart
