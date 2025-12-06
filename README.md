# E-commerce Database Performance Comparison
Sijie Guo, Yang Chen


This is our final project comparing MySQL and MongoDB performance on e-commerce queries.

## Overview

Generates synthetic e-commerce data and benchmarks query performance across both relational (MySQL) and document (MongoDB) databases.

## Data Generation
Run the Python script to generate all data files:

```bash
python generate_ecommerce_data.py
```

Generates:
- **CSV files**: users, products, orders, order_items, carts, cart_items, categories, shipping_options, sessions
- **JSONL files**: `mongo_products.jsonl` (product attributes), `events.jsonl` (user events)

## Database Setup

### MySQL
Import CSV files into MySQL tables. Run queries with profiling enabled:

```bash
mysql < mysql_queries_with_profiling.sql
```

### MongoDB
Import JSONL files:
```bash
mongoimport --db ecommerce --collection products --file mongo_products.jsonl
mongoimport --db ecommerce --collection events --file events.jsonl
```

Run queries:
```bash
mongosh ecommerce
load("mongo_queries.js")
runAllMongoQueries()
```

## Queries

**MySQL (9 queries):**
- Query 1: Fashion products
- Query 3: Low stock items
- Query 7: Carts with totals
- Query 8: Sarah's orders with details
- Query 9: Returned items by Sarah
- Query 10: Average days between purchases
- Query 11: Cart abandonment rate
- Query 12: Top 3 products purchased with headphones
- Query 13: Days since last purchase per user

**MongoDB (4 queries):**
- Query 2: Last 5 products viewed by user
- Query 4: Fashion products with attributes
- Query 5: Page view counts per product
- Query 6: Search terms by time-of-day

