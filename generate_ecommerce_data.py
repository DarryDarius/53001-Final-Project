import csv
import json
import random
import string
from datetime import datetime, timedelta

random.seed(42)

# -------------------------
# CONFIG
# -------------------------
N_USERS = 1000
N_PRODUCTS = 5000
N_ORDERS = 100000
N_EVENTS = 500000

# For sanity, control average items per order & carts
AVG_ITEMS_PER_ORDER = 2.5  # ~ 250k order_items
N_CARTS = 3000             # some converted, some abandoned

# Time window for orders/events
NOW = datetime.utcnow()
DAYS_BACK = 180

# -------------------------
# HELPERS
# -------------------------

def rand_date_within(days_back=DAYS_BACK):
    delta_days = random.randint(0, days_back)
    delta_secs = random.randint(0, 24 * 3600)
    return NOW - timedelta(days=delta_days, seconds=delta_secs)

def random_email(name, idx):
    return f"{name.lower().replace(' ', '.')}{idx}@example.com"

def random_name():
    first = random.choice([
        "Sarah", "John", "Emma", "Liam", "Olivia", "Noah",
        "Ava", "Sophia", "Ethan", "Mia", "Lucas", "Isabella"
    ])
    last = random.choice([
        "Smith", "Johnson", "Williams", "Brown", "Jones",
        "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"
    ])
    return f"{first} {last}"

def random_string(n=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=n))

# -------------------------
# 1. USERS
# -------------------------

users = []
for user_id in range(1, N_USERS + 1):
    name = random_name()
    email = random_email(name, user_id)
    users.append({
        "user_id": user_id,
        "name": name,
        "email": email,
        "created_at": rand_date_within(365).isoformat(timespec="seconds")
    })

with open("users.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["user_id", "name", "email", "created_at"])
    for u in users:
        writer.writerow([u["user_id"], u["name"], u["email"], u["created_at"]])

# -------------------------
# 2. CATEGORIES
# -------------------------
# Match your earlier design: fashion / electronics / home_decor / other

categories = [
    {"category_id": 1, "name": "fashion"},
    {"category_id": 2, "name": "electronics"},
    {"category_id": 3, "name": "home_decor"},
    {"category_id": 4, "name": "other"},
]

with open("categories.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["category_id", "name"])
    for c in categories:
        writer.writerow([c["category_id"], c["name"]])

# Helper to choose category with skewed distribution
def choose_category_id():
    # 0.35 fashion, 0.3 electronics, 0.2 home_decor, 0.15 other
    r = random.random()
    if r < 0.35:
        return 1
    elif r < 0.65:
        return 2
    elif r < 0.85:
        return 3
    else:
        return 4

# -------------------------
# 3. PRODUCTS (relational) + Mongo product docs
# -------------------------

# Attribute templates like your design
CATEGORY_TEMPLATES = {
    1: {  # fashion
        "attributes": [
            {"name": "size", "type": "string"},
            {"name": "color", "type": "string"},
            {"name": "material", "type": "string"},
        ]
    },
    2: {  # electronics
        "attributes": [
            {"name": "battery_life", "type": "number"},
            {"name": "connectivity", "type": "string"},
            {"name": "weight", "type": "number"},
        ]
    },
    3: {  # home_decor
        "attributes": [
            {"name": "height_cm", "type": "number"},
            {"name": "width_cm", "type": "number"},
            {"name": "material", "type": "string"},
        ]
    },
    4: {  # other
        "attributes": [
            {"name": "brand", "type": "string"},
            {"name": "tagline", "type": "string"},
        ]
    },
}

COLOR_CHOICES = ["blue", "aqua-blue", "red", "green", "black", "white", "beige"]
SIZE_CHOICES = ["XS", "S", "M", "L", "XL"]
MATERIAL_FABRIC = ["cotton", "polyester", "linen", "silk"]
MATERIAL_DECOR = ["ceramic", "glass", "wood", "metal"]
CONNECTIVITY_CHOICES = ["Bluetooth", "Wired", "Wireless-USB"]

products_rel = []
mongo_products = []

for product_id in range(1, N_PRODUCTS + 1):
    category_id = choose_category_id()
    base_price = round(random.uniform(5, 500), 2)
    stock_qty = random.randint(0, 500)

    # Simple product names
    if category_id == 1:
        name = f"Fashion Item {product_id}"
    elif category_id == 2:
        name = f"Electronic Item {product_id}"
    elif category_id == 3:
        name = f"Home Decor Item {product_id}"
    else:
        name = f"Misc Item {product_id}"

    products_rel.append({
        "product_id": product_id,
        "category_id": category_id,
        "name": name,
        "base_price": base_price,
        "stock_qty": stock_qty,
        "created_at": rand_date_within(365).isoformat(timespec="seconds")
    })

    # Build MongoDB attributes according to template
    tmpl = CATEGORY_TEMPLATES[category_id]
    attrs = {}
    for spec in tmpl["attributes"]:
        attr_name = spec["name"]
        attr_type = spec["type"]
        if category_id == 1:  # fashion
            if attr_name == "size":
                attrs["size"] = random.choice(SIZE_CHOICES)
            elif attr_name == "color":
                attrs["color"] = random.choice(COLOR_CHOICES)
            elif attr_name == "material":
                attrs["material"] = random.choice(MATERIAL_FABRIC)
        elif category_id == 2:  # electronics
            if attr_name == "battery_life":
                attrs["battery_life"] = random.randint(5, 40)
            elif attr_name == "connectivity":
                attrs["connectivity"] = random.choice(CONNECTIVITY_CHOICES)
            elif attr_name == "weight":
                attrs["weight"] = random.randint(100, 800)  # grams
        elif category_id == 3:  # home_decor
            if attr_name == "height_cm":
                attrs["height_cm"] = round(random.uniform(5, 60), 1)
            elif attr_name == "width_cm":
                attrs["width_cm"] = round(random.uniform(5, 40), 1)
            elif attr_name == "material":
                attrs["material"] = random.choice(MATERIAL_DECOR)
        else:  # other
            if attr_name == "brand":
                attrs["brand"] = random.choice(["Acme", "Globex", "Umbrella", "Wayne"])
            elif attr_name == "tagline":
                attrs["tagline"] = random.choice([
                    "Best in class", "Value choice", "Premium quality", "Limited edition"
                ])

    mongo_products.append({
        "product_id": product_id,        # matches MySQL PK
        "category_id": category_id,
        "attributes": attrs
    })

with open("products.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["product_id", "category_id", "name", "base_price", "stock_qty", "created_at"])
    for p in products_rel:
        writer.writerow([
            p["product_id"], p["category_id"], p["name"],
            p["base_price"], p["stock_qty"], p["created_at"]
        ])

with open("mongo_products.jsonl", "w") as f:
    for doc in mongo_products:
        f.write(json.dumps(doc) + "\n")

# -------------------------
# 4. SHIPPING OPTIONS
# -------------------------

shipping_options = [
    {"shipping_option_id": 1, "name": "Standard"},
    {"shipping_option_id": 2, "name": "Expedited"},
    {"shipping_option_id": 3, "name": "Overnight"},
]

with open("shipping_options.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["shipping_option_id", "name"])
    for s in shipping_options:
        writer.writerow([s["shipping_option_id"], s["name"]])

# -------------------------
# 5. ORDERS + ORDER_ITEMS
# -------------------------

payment_methods = ["credit_card", "debit_card", "paypal", "bank_transfer"]
order_statuses = ["completed", "pending", "cancelled", "refunded"]

orders = []
order_items = []

order_item_id_counter = 1

for order_id in range(1, N_ORDERS + 1):
    user_id = random.randint(1, N_USERS)
    order_date = rand_date_within()
    payment_method = random.choice(payment_methods)
    shipping_option_id = random.randint(1, len(shipping_options))
    status = random.choices(
        order_statuses,
        weights=[0.75, 0.15, 0.05, 0.05],
        k=1
    )[0]

    orders.append({
        "order_id": order_id,
        "user_id": user_id,
        "order_date": order_date.isoformat(timespec="seconds"),
        "payment_method": payment_method,
        "shipping_option_id": shipping_option_id,
        "status": status,
    })

    # number of items per order around AVG_ITEMS_PER_ORDER
    n_items = max(1, int(random.gauss(AVG_ITEMS_PER_ORDER, 1)))
    chosen_products = random.sample(range(1, N_PRODUCTS + 1), k=min(n_items, N_PRODUCTS))

    for pid in chosen_products:
        product = products_rel[pid - 1]
        quantity = random.randint(1, 3)
        unit_price = product["base_price"]
        order_items.append({
            "order_item_id": order_item_id_counter,
            "order_id": order_id,
            "product_id": pid,
            "quantity": quantity,
            "unit_price": unit_price
        })
        order_item_id_counter += 1

with open("orders.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "order_id", "user_id", "order_date",
        "payment_method", "shipping_option_id", "status"
    ])
    for o in orders:
        writer.writerow([
            o["order_id"], o["user_id"], o["order_date"],
            o["payment_method"], o["shipping_option_id"], o["status"]
        ])

with open("order_items.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["order_item_id", "order_id", "product_id", "quantity", "unit_price"])
    for oi in order_items:
        writer.writerow([
            oi["order_item_id"], oi["order_id"], oi["product_id"],
            oi["quantity"], oi["unit_price"]
        ])

# -------------------------
# 6. CARTS + CART_ITEMS
# -------------------------

device_types = ["laptop", "tablet", "phone"]

carts = []
cart_items = []
cart_item_id_counter = 1

# some carts linked to orders (converted), some not
for cart_id in range(1, N_CARTS + 1):
    user_id = random.randint(1, N_USERS)
    device_type = random.choice(device_types)
    device_id = random_string(10)
    created_at = rand_date_within()
    updated_at = created_at + timedelta(minutes=random.randint(0, 120))

    # 40% of carts convert
    if random.random() < 0.4:
        # pick a random order from this user if exists, else null
        user_orders = [o for o in orders if o["user_id"] == user_id]
        if user_orders:
            order_id = random.choice(user_orders)["order_id"]
        else:
            order_id = ""
    else:
        order_id = ""

    carts.append({
        "cart_id": cart_id,
        "user_id": user_id,
        "device_type": device_type,
        "device_id": device_id,
        "created_at": created_at.isoformat(timespec="seconds"),
        "updated_at": updated_at.isoformat(timespec="seconds"),
        "order_id": order_id
    })

    # cart items
    n_items = random.randint(0, 6)
    if n_items > 0:
        chosen_products = random.sample(range(1, N_PRODUCTS + 1), k=n_items)
        for pid in chosen_products:
            product = products_rel[pid - 1]
            quantity = random.randint(1, 3)
            cart_items.append({
                "cart_item_id": cart_item_id_counter,
                "cart_id": cart_id,
                "product_id": pid,
                "quantity": quantity,
                "unit_price": product["base_price"]
            })
            cart_item_id_counter += 1

with open("carts.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "cart_id", "user_id", "device_type", "device_id",
        "created_at", "updated_at", "order_id"
    ])
    for c in carts:
        writer.writerow([
            c["cart_id"], c["user_id"], c["device_type"], c["device_id"],
            c["created_at"], c["updated_at"], c["order_id"]
        ])

with open("cart_items.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["cart_item_id", "cart_id", "product_id", "quantity", "unit_price"])
    for ci in cart_items:
        writer.writerow([
            ci["cart_item_id"], ci["cart_id"], ci["product_id"],
            ci["quantity"], ci["unit_price"]
        ])

# -------------------------
# 7. SESSIONS + EVENTS (for MongoDB)
# -------------------------

# create some sessions per user
sessions = []
session_events = []

session_id_counter = 1

# each user gets 1–5 sessions
for u in users:
    n_sessions = random.randint(1, 5)
    for _ in range(n_sessions):
        session_id = f"sess_{session_id_counter}"
        session_id_counter += 1
        start_time = rand_date_within()
        device_type = random.choice(device_types)
        sessions.append({
            "session_id": session_id,
            "user_id": u["user_id"],
            "device_type": device_type,
            "start_time": start_time.isoformat(timespec="seconds")
        })

# Now generate events, tied to existing sessions/users/products
event_types = ["product_view", "search", "add_to_cart", "checkout", "purchase"]

events = []

for i in range(N_EVENTS):
    sess = random.choice(sessions)
    user_id = sess["user_id"]
    session_id = sess["session_id"]
    ts = rand_date_within()
    etype = random.choices(
        event_types,
        weights=[0.55, 0.25, 0.1, 0.05, 0.05],
        k=1
    )[0]

    event = {
        "user_id": user_id,
        "session_id": session_id,
        "event_type": etype,
        "timestamp": ts.isoformat(timespec="seconds")
    }

    if etype in ["product_view", "add_to_cart", "checkout", "purchase"]:
        event["product_id"] = random.randint(1, N_PRODUCTS)
    else:
        event["product_id"] = None

    if etype == "search":
        event["query_string"] = random.choice([
            "headphones", "dress", "vase", "bluetooth", "summer dress",
            "ceramic vase", "wireless earbuds", "lamp", "sofa"
        ])
    else:
        event["query_string"] = None

    # simple dwell time for product views
    if etype == "product_view":
        event["duration_ms"] = random.randint(1000, 60000)
    else:
        event["duration_ms"] = None

    events.append(event)

# Write sessions (relational-ish, but you can also import to Mongo if you want)
with open("sessions.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["session_id", "user_id", "device_type", "start_time"])
    for s in sessions:
        writer.writerow([s["session_id"], s["user_id"], s["device_type"], s["start_time"]])

# Write events JSONL for Mongo events collection
with open("events.jsonl", "w") as f:
    for ev in events:
        # Remove None fields to keep docs cleaner
        clean_ev = {k: v for k, v in ev.items() if v is not None}
        f.write(json.dumps(clean_ev) + "\n")

print("Data generation complete.")
print("Generated files:")
print("- users.csv")
print("- categories.csv")
print("- products.csv")
print("- orders.csv")
print("- order_items.csv")
print("- carts.csv")
print("- cart_items.csv")
print("- shipping_options.csv")
print("- sessions.csv")
print("- mongo_products.jsonl")
print("- events.jsonl")


