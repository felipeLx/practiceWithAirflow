# Data for two customers and their orders
SELECT
    customer_id as c_id, customer_name, ordered,
    product_id as p_id, product_name, quantity
FROM customer_order_products
WHERE customer_id IN (50042, 50741)
ORDER BY customer_id, product_id;

# Data for two breweries and the products bought from them
SELECT
    brewery_id as b_id, brewery_name,
    product_id as p_id, product_name
FROM brewery_products
WHERE brewery_id IN (518, 523)
ORDER BY brewery_id, product_id;