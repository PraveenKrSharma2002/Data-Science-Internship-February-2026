from fastapi import FastAPI, Query, Response, status
from pydantic import BaseModel, Field

app = FastAPI()

# ===== MODELS =====
class OrderRequest(BaseModel):
    customer_name: str = Field(..., min_length=2, max_length=100)
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0, le=100)
    delivery_address: str = Field(..., min_length=10)

class CheckoutRequest(BaseModel):
    customer_name: str = Field(..., min_length=2)
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
cart = []
order_counter = 1

# ===== HELPERS =====
def find_product(pid):
    for p in products:
        if p["id"] == pid:
            return p
    return None

def calc_total(p, qty):
    return p["price"] * qty

# ===== BASIC =====
@app.get("/")
def home():
    return {"msg": "Ecommerce API"}

@app.get("/products")
def get_products():
    return {"products": products, "total": len(products)}

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

# ===== CART SYSTEM =====
@app.post("/cart/add")
def add_cart(product_id: int = Query(...),
             quantity: int = Query(1),
             response: Response = None):

    p = find_product(product_id)

    if not p:
        response.status_code = 404
        return {"detail": "Product not found"}

    if not p["in_stock"]:
        response.status_code = 400
        return {"detail": f"{p['name']} is out of stock"}

    for item in cart:
        if item["product_id"] == product_id:
            item["quantity"] += quantity
            item["subtotal"] = calc_total(p, item["quantity"])
            return {"message": "Cart updated", "cart_item": item}

    new_item = {
        "product_id": product_id,
        "product_name": p["name"],
        "quantity": quantity,
        "unit_price": p["price"],
        "subtotal": calc_total(p, quantity)
    }

    cart.append(new_item)
    return {"message": "Added to cart", "cart_item": new_item}

@app.get("/cart")
def view_cart():
    if not cart:
        return {"message": "Cart is empty"}

    total = sum(i["subtotal"] for i in cart)

    return {
        "items": cart,
        "item_count": len(cart),
        "grand_total": total
    }

@app.post("/cart/checkout")
def checkout(data: CheckoutRequest, response: Response):
    global order_counter

    if not cart:
        response.status_code = 400
        return {"detail": "CART_EMPTY"}

    placed = []
    total = 0

    for item in cart:
        order = {
            "order_id": order_counter,
            "customer_name": data.customer_name,
            "product": item["product_name"],
            "quantity": item["quantity"],
            "delivery_address": data.delivery_address,
            "total_price": item["subtotal"]
        }

        orders.append(order)
        placed.append(order)
        total += item["subtotal"]
        order_counter += 1

    cart.clear()

    return {
        "message": "Checkout successful",
        "orders_placed": placed,
        "grand_total": total
    }

@app.delete("/cart/{pid}")
def remove_cart(pid: int, response: Response):
    for item in cart:
        if item["product_id"] == pid:
            cart.remove(item)
            return {"message": f"{item['product_name']} removed"}

    response.status_code = 404
    return {"error": "Product not in cart"}

# ===== ORDERS =====
@app.get("/orders")
def all_orders():
    return {"orders": orders, "total_orders": len(orders)}

# ===== VARIABLE ROUTE LAST =====
@app.get("/products/{pid}")
def get_one(pid: int):
    p = find_product(pid)
    if not p:
        return {"error": "Product not found"}
    return p