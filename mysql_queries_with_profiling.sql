-- mysql_queries_with_profiling.sql
-- Run-time measurement for MySQL queries (for the 13-task assignment)

-- Select database
USE ecommerce;

-- Enable profiling so MySQL records the execution time of each statement
SET profiling = 1;

-- Assume user_id = 1 represents “Sarah” in the synthetic dataset
SET @sarah_id := 1;

-- ------------------------------------------------------------
-- Query 1 (MySQL part) – fashion products core data
-- Retrieve all products in the "fashion" category (core fields)
-- ------------------------------------------------------------
SELECT
  p.product_id,
  p.name,
  p.base_price
FROM products p
JOIN categories c
  ON p.category_id = c.category_id
WHERE c.name = 'fashion';


-- ------------------------------------------------------------
-- Query 3 – Low stock items
-- Check current stock level and return items with stock < 5
-- ------------------------------------------------------------
SELECT
  product_id,
  name,
  stock_qty
FROM products
WHERE stock_qty < 5
ORDER BY stock_qty ASC;


-- ------------------------------------------------------------
-- Query 7 – All carts with device type, item count, and total amount
-- ------------------------------------------------------------
SELECT
  c.cart_id,
  c.user_id,
  c.device_type,
  COUNT(ci.cart_item_id) AS item_count,
  COALESCE(SUM(ci.quantity * ci.unit_price), 0) AS total_amount
FROM carts c
LEFT JOIN cart_items ci
  ON c.cart_id = ci.cart_id
GROUP BY
  c.cart_id,
  c.user_id,
  c.device_type
ORDER BY c.updated_at DESC;


-- ------------------------------------------------------------
-- Query 8 – All orders placed by Sarah with item details, payment, shipping, status
-- ------------------------------------------------------------
SELECT
  o.order_id,
  o.order_date,
  o.payment_method,
  so.name AS shipping_option,
  o.status AS order_status,
  oi.order_item_id,
  p.product_id,
  p.name AS product_name,
  oi.quantity,
  oi.unit_price,
  (oi.quantity * oi.unit_price) AS line_total
FROM orders o
JOIN users u
  ON o.user_id = u.user_id
JOIN order_items oi
  ON o.order_id = oi.order_id
JOIN products p
  ON oi.product_id = p.product_id
LEFT JOIN shipping_options so
  ON o.shipping_option_id = so.shipping_option_id
WHERE u.user_id = @sarah_id
ORDER BY
  o.order_date DESC,
  o.order_id,
  oi.order_item_id;


-- ------------------------------------------------------------
-- Query 9 – Returned items by Sarah with refund status, amount, fees
-- ------------------------------------------------------------
SELECT
  r.return_id,
  r.created_at,
  o.order_id,
  p.product_id,
  p.name AS product_name,
  r.refund_status,
  r.refund_amount,
  r.restocking_fee
FROM returns r
JOIN order_items oi
  ON r.order_item_id = oi.order_item_id
JOIN orders o
  ON oi.order_id = o.order_id
JOIN users u
  ON o.user_id = u.user_id
JOIN products p
  ON oi.product_id = p.product_id
WHERE u.user_id = @sarah_id
ORDER BY r.created_at DESC;


-- ------------------------------------------------------------
-- Query 10 – Average number of days between purchases for Sarah
-- ------------------------------------------------------------
WITH user_orders AS (
  SELECT
    o.order_id,
    o.user_id,
    o.order_date,
    ROW_NUMBER() OVER (
      PARTITION BY o.user_id
      ORDER BY o.order_date
    ) AS rn
  FROM orders o
  WHERE o.user_id = @sarah_id
),
order_pairs AS (
  SELECT
    cur.order_id,
    DATEDIFF(cur.order_date, prev.order_date) AS days_since_prev
  FROM user_orders cur
  JOIN user_orders prev
    ON cur.rn = prev.rn + 1
)
SELECT
  AVG(days_since_prev) AS avg_days_between_purchases
FROM order_pairs;


-- ------------------------------------------------------------
-- Query 11 – Cart abandonment rate in the past 30 days
-- ------------------------------------------------------------
WITH recent_carts AS (
  SELECT
    cart_id,
    order_id
  FROM carts
  WHERE created_at >= NOW() - INTERVAL 30 DAY
),
agg AS (
  SELECT
    COUNT(*) AS total_carts,
    SUM(CASE WHEN order_id IS NULL THEN 1 ELSE 0 END) AS abandoned_carts
  FROM recent_carts
)
SELECT
  abandoned_carts,
  total_carts,
  (abandoned_carts / total_carts) * 100 AS abandonment_rate_percent
FROM agg;


-- ------------------------------------------------------------
-- Query 12 – Top 3 products most frequently purchased together with "headphones"
-- Note: This assumes there is a category named 'headphones'. In the current data
-- generation script, categories only include fashion / electronics / home_decor / other,
-- so this query will return an empty result set for now, but it is still valid for performance testing.
-- ------------------------------------------------------------
WITH headphone_orders AS (
  SELECT DISTINCT oi.order_id
  FROM order_items oi
  JOIN products p
    ON oi.product_id = p.product_id
  JOIN categories c
    ON p.category_id = c.category_id
  WHERE c.name = 'headphones'
),
co_purchased AS (
  SELECT
    oi.product_id,
    COUNT(DISTINCT oi.order_id) AS co_purchase_count
  FROM order_items oi
  JOIN headphone_orders ho
    ON oi.order_id = ho.order_id
  JOIN products p2
    ON oi.product_id = p2.product_id
  JOIN categories c2
    ON p2.category_id = c2.category_id
  WHERE c2.name <> 'headphones'
  GROUP BY oi.product_id
)
SELECT
  cp.product_id,
  p.name AS product_name,
  cp.co_purchase_count
FROM co_purchased cp
JOIN products p
  ON cp.product_id = p.product_id
ORDER BY cp.co_purchase_count DESC
LIMIT 3;


-- ------------------------------------------------------------
-- Query 13 – For each user: days since last purchase and total order count
-- ------------------------------------------------------------
WITH user_last_order AS (
  SELECT
    o.user_id,
    MAX(o.order_date) AS last_order_date,
    COUNT(*)          AS order_count
  FROM orders o
  GROUP BY o.user_id
)
SELECT
  u.user_id,
  u.name,
  ulo.order_count,
  DATEDIFF(CURDATE(), ulo.last_order_date) AS days_since_last_purchase
FROM users u
LEFT JOIN user_last_order ulo
  ON u.user_id = ulo.user_id
ORDER BY days_since_last_purchase DESC;


-- ------------------------------------------------------------
-- Finally, inspect the execution time of all statements just run.
-- The Duration column is in seconds and can be used to check the 2-second threshold.
-- ------------------------------------------------------------
SHOW PROFILES;

-- If you want to inspect a specific query in more detail, you can use:
-- SHOW PROFILE FOR QUERY <Query_ID>;
-- For example:
-- SHOW PROFILE FOR QUERY 1;
