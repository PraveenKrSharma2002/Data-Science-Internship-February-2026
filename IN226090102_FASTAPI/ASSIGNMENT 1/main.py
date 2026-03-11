from fastapi import FastAPI

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
