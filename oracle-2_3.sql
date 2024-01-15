# Minus is like multiset except distinct
SELECT
    product_id as p_id, product_name
FROM customer_order_products
WHERE customer_id = 50741
MINUS
SELECT
    product_id as p_id, product_name
FROM customer_order_products
WHERE customer_id = 50042
ORDER BY product_id;
#  minus also removes duplicates of the input sets first before doing the subtraction   

#  Emulating minus all using multiset except all
SELECT
    minus_all.product_id as p_id, 
    minus_all.product_name as p_name
FROM TABLE(
    multiset(
        SELECT
            product_id, product_name
        FROM customer_order_products
        WHERE customer_id = 50741
    ) as id_name_coll_type
) multiset except all
CAST(
    multiset(
        SELECT
            product_id, product_name
        FROM customer_order_products
        WHERE customer_id = 50042
    ) as id_name_coll_type
) as minus_all_table
ORDER BY p_id;