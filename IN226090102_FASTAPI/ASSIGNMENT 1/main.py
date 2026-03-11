from fastapi import FastAPI
from typing import Optional, List
from pydantic import BaseModel, Field
app = FastAPI()

# product data
products = [
    {"id": 1, "name": "Wireless Mouse", "price": 599, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 120, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": False},
    {"id": 4, "name": "USB Cable", "price": 199, "category": "Electronics", "in_stock": True},

    {"id": 5, "name": "Laptop Stand", "price": 899, "category": "Electronics", "in_stock": True},
    {"id": 6, "name": "Mechanical Keyboard", "price": 2499, "category": "Electronics", "in_stock": True},
    {"id": 7, "name": "Webcam", "price": 1299, "category": "Electronics", "in_stock": False}
]


# show all products
@app.get("/products")
def show_products():

    total = len(products)

    return {
        "products": products,
        "total": total
    }


# filter by category
@app.get("/products/category/{category_name}")
def category_products(category_name: str):

    result = []

    # check each product
    for p in products:

        cat = p["category"].lower()

        if cat == category_name.lower():
            result.append(p)

    # if nothing found
    if not result:
        return {"error": "No products found in this category"}

    return {"products": result}


# show only available products
@app.get("/products/instock")
def instock_products():

    data = []

    for p in products:
        if p["in_stock"] == True:
            data.append(p)

    count = len(data)

    return {
        "in_stock_products": data,
        "count": count
    }


# store summary
@app.get("/store/summary")
def store_summary():

    total = len(products)

    instock = 0
    categories = []

    for p in products:

        # count stock
        if p["in_stock"]:
            instock += 1

        # store categories
        if p["category"] not in categories:
            categories.append(p["category"])

    outstock = total - instock

    return {
        "store_name": "My E-commerce Store",
        "total_products": total,
        "in_stock": instock,
        "out_of_stock": outstock,
        "categories": categories
    }


# search product by name
@app.get("/products/search/{keyword}")
def search_products(keyword: str):

    found = []

    for p in products:

        name = p["name"].lower()

        if keyword.lower() in name:
            found.append(p)

    if len(found) == 0:
        return {"message": "No products matched your search"}

    return {
        "products": found,
        "count": len(found)
    }


# bonus task - cheapest and most expensive product
@app.get("/products/deals")
def product_deals():

    cheapest = products[0]
    expensive = products[0]

    for p in products:

        if p["price"] < cheapest["price"]:
            cheapest = p

        if p["price"] > expensive["price"]:
            expensive = p

    return {
        "best_deal": cheapest,
        "premium_pick": expensive
    }
# -------------------- DAY 2 --------------------
@app.get("/products/filter")
def filter_products(min_price: Optional[int] = None,
                    max_price: Optional[int] = None,
                    category: Optional[str] = None):

    result = []

    for p in products:

        if min_price is not None and p["price"] < min_price:
            continue

        if max_price is not None and p["price"] > max_price:
            continue

        if category is not None and p["category"].lower() != category.lower():
            continue

        result.append(p)

    return {"filtered_products": result}


@app.get("/products/{product_id}/price")
def get_product_price(product_id: int):

    for p in products:
        if p["id"] == product_id:
            return {"name": p["name"], "price": p["price"]}

    return {"error": "Product not found"}


# -------------------- FEEDBACK --------------------

feedback_list = []

class CustomerFeedback(BaseModel):
    customer_name: str = Field(..., min_length=2)
    product_id: int = Field(..., gt=0)
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=300)


@app.post("/feedback")
def submit_feedback(data: CustomerFeedback):

    feedback_list.append(data.dict())

    return {
        "message": "Feedback submitted successfully",
        "feedback": data,
        "total_feedback": len(feedback_list)
    }


# -------------------- SUMMARY DASHBOARD --------------------

@app.get("/products/summary")
def product_summary():

    total = len(products)
    instock = 0
    cheapest = products[0]
    expensive = products[0]
    categories = []

    for p in products:

        if p["in_stock"]:
            instock += 1

        if p["price"] < cheapest["price"]:
            cheapest = p

        if p["price"] > expensive["price"]:
            expensive = p

        if p["category"] not in categories:
            categories.append(p["category"])

    return {
        "total_products": total,
        "in_stock_count": instock,
        "out_of_stock_count": total - instock,
        "most_expensive": {"name": expensive["name"], "price": expensive["price"]},
        "cheapest": {"name": cheapest["name"], "price": cheapest["price"]},
        "categories": categories
    }


# -------------------- BULK ORDER --------------------

class OrderItem(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., ge=1, le=50)

class BulkOrder(BaseModel):
    company_name: str = Field(..., min_length=2)
    contact_email: str = Field(..., min_length=5)
    items: List[OrderItem]


@app.post("/orders/bulk")
def bulk_order(order: BulkOrder):

    confirmed = []
    failed = []
    total = 0

    for item in order.items:

        product = None

        for p in products:
            if p["id"] == item.product_id:
                product = p
                break

        if product is None:
            failed.append({"product_id": item.product_id, "reason": "Product not found"})
            continue

        if not product["in_stock"]:
            failed.append({"product_id": item.product_id, "reason": f"{product['name']} is out of stock"})
            continue

        subtotal = product["price"] * item.quantity
        total += subtotal

        confirmed.append({
            "product": product["name"],
            "qty": item.quantity,
            "subtotal": subtotal
        })

    return {
        "company": order.company_name,
        "confirmed": confirmed,
        "failed": failed,
        "grand_total": total
    }
