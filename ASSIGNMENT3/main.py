from fastapi import FastAPI, Query, Response, status
from pydantic import BaseModel, Field

app = FastAPI()

# ===== MODELS =====
class OrderRequest(BaseModel):
    customer_name: str = Field(..., min_length=2, max_length=100)
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0, le=100)
    delivery_address: str = Field(..., min_length=10)

class NewProduct(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    price: int = Field(..., gt=0)
    category: str = Field(..., min_length=2)
    in_stock: bool = True

# ===== DATA =====
products = [
    {'id': 1, 'name': 'Wireless Mouse', 'price': 499, 'category': 'Electronics', 'in_stock': True},
    {'id': 2, 'name': 'Notebook', 'price': 99, 'category': 'Stationery', 'in_stock': True},
    {'id': 3, 'name': 'USB Hub', 'price': 799, 'category': 'Electronics', 'in_stock': False},
    {'id': 4, 'name': 'Pen Set', 'price': 49, 'category': 'Stationery', 'in_stock': True},
]

orders = []
order_counter = 1

# ===== HELPERS =====
def find_product(pid):
    for p in products:
        if p["id"] == pid:
            return p
    return None

# ===== BASIC =====
@app.get("/")
def home():
    return {"msg": "Ecommerce API"}

@app.get("/products")
def get_products():
    return {"products": products, "total": len(products)}

# ===== Q5 AUDIT (ABOVE VARIABLE ROUTE) =====
@app.get("/products/audit")
def audit():
    total = len(products)
    in_stock = [p for p in products if p["in_stock"]]
    out_stock = [p["name"] for p in products if not p["in_stock"]]

    total_value = sum(p["price"] * 10 for p in in_stock)

    most_exp = max(products, key=lambda x: x["price"])

    return {
        "total_products": total,
        "in_stock_count": len(in_stock),
        "out_of_stock_names": out_stock,
        "total_stock_value": total_value,
        "most_expensive": {
            "name": most_exp["name"],
            "price": most_exp["price"]
        }
    }

# ===== BONUS DISCOUNT =====
@app.put("/products/discount")
def discount(category: str = Query(...), discount_percent: int = Query(...)):
    updated = []

    for p in products:
        if p["category"].lower() == category.lower():
            p["price"] = int(p["price"] * (1 - discount_percent / 100))
            updated.append(p)

    if not updated:
        return {"msg": "No products found"}

    return {"updated_count": len(updated), "products": updated}

# ===== CRUD =====
@app.post("/products")
def add_product(prod: NewProduct, response: Response):
    names = [p["name"].lower() for p in products]

    if prod.name.lower() in names:
        response.status_code = 400
        return {"error": "Product with this name already exists"}

    new_id = max(p["id"] for p in products) + 1

    new_p = prod.dict()
    new_p["id"] = new_id

    products.append(new_p)

    response.status_code = 201
    return {"message": "Product added", "product": new_p}

@app.put("/products/{pid}")
def update(pid: int, response: Response,
           in_stock: bool = Query(None),
           price: int = Query(None)):

    p = find_product(pid)

    if not p:
        response.status_code = 404
        return {"error": "Product not found"}

    if in_stock is not None:
        p["in_stock"] = in_stock
    if price is not None:
        p["price"] = price

    return {"msg": "updated", "product": p}

@app.delete("/products/{pid}")
def delete(pid: int, response: Response):

    p = find_product(pid)

    if not p:
        response.status_code = 404
        return {"error": "Product not found"}

    products.remove(p)
    return {"msg": f"Product '{p['name']}' deleted"}

# ===== VARIABLE ROUTE (LAST) =====
@app.get("/products/{pid}")
def get_one(pid: int):
    p = find_product(pid)
    if not p:
        return {"error": "Product not found"}
    return p