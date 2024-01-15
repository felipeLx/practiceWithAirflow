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

