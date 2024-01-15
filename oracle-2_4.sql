# Emulating minus all using analytic row_number function
SELECT
    product_id as p_id,
    product_name,
    row_number() OVER (
        PARTITION BY product_id, product_name ORDER BY rownum
    ) as rn
FROM customer_order_products
WHERE customer_id = 50741
MINUS
SELECT
    product_id as p_id,
    product_name,
    row_number() OVER (
        PARTITION BY product_id, product_name ORDER BY rownum
    ) as rn
FROM customer_order_products
WHERE customer_id = 50042
ORDER BY p_id;

"""
add a column that uses row_number to cre_ate a consecutive 
numbering 1, 2, 3 … for each distinct value combination of product_id and product_
name. This way the implicit distinct performed by the minus operator removes no rows, 
since the addition of the consecutive numbers in the rn column makes all rows unique.
"""
