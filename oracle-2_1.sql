# Creating the types and view for the multiset examples
CREATE or REPLACE TYPE id_name_type AS OBJECT (
    id INTeGER,
    name VARCHAR2(20 char)
);

TYPE ID_NAME_TYPE compiled

CREATE or REPLACE TYPE id_name_coll_type AS TABLE OF id_name_type;

TYPE ID_NAME_COLL_TYPE compiled

CREATE or REPLACE VIEW customer_order_products_obj AS
    SELECT
        customer_id,
        max(customer_name) AS customer_name,
        cast(
            collect(
                id_name_type(product_id, product_name)
                order by product_id
            ) as id_name_coll_type
        ) AS product_coll
    FROM customer_order_products
    GROUP BY customer_id;

VIEW CUSTOMER_ORDER_PRODUCTS_OBJ created.



# Achieving the same w/ a lateral inline view
"""
"""
SELECT
    bp.brewery_name,
    bp.product_id as p_id,
    bp.product_name,
    top_ys.yr,
    top_ys.yr_qty
FROM brewery_products bp
CROSS APPLY (
    SELECT
        ys.yr,
        ys.yr_qty
    FROM yearly_sales ys
    WHERE ys.product_id = bp.product_id
    ORDER BY ys.yr_qty DESC
    FETCH FIRST ROW ONLY
) top_ys
WHERE bp.brewery_id = 518
ORDER BY bp.product_id;

"""
use apply, I am allowed to correlate the inline view w/ the predicate in line 40,  just like using lateral. Behind the scenes, the database does exactly the same as a lateral inline view; it is just a case of which syntax you prefer.
"""