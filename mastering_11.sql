 -- selective aggregation
 /* Europe Buckets */
 UPDATE mt_orders mtdo
 SET (mtdo.europe_tot_orders, mtdo.europe_tot_sale_price, mtdo.europe_max_sale_price) = 
        (SELECT mtdo.europe_tot_orders + eur_day_tot.tot_sale_price, mtdo.europe_tot_sale_price + nvl(eur_day_tot.tot_sale_price, 0), 
        CASE WHEN eur_day_tot.tot_sale_price > mtdo.europe_max_sale_price 
        THEN eur_day_tot.max_sale_price
        ELSE mtdo.europe_max_sale_price END
    FROM
        (SELECT COUNT(*) tot_orders, SUM(co.sale_price) tot_sale_price, MAX(co.sale_price) max_sale_price
        FROM cust_order co INNER JOIN customer c
        ON co.cust_nbr = c.cust_nbr
        WHERE co.cancelled_dt IS NULL
        AND co.order_dt >= TRUNC(SYSDATE)
        AND c.region_id IN 
        (SELECT region_id FROM region
        START WITH name = 'Europe'
        CONNECT BY PRIOR region_id = super_region_id)) eur_day_tot);

-- checking for existence
/*
When evaluating optional one-to-many relationships, there are certain cases where
you want to know whether the relationship is zero or greater than zero without
regard for the actual data.
*/
SELECT c.cust_nbr cust_nbr, c.name name,
    DECODE(o, (SELECT COUNT(*) FROM cust_order co 
    WHERE co.cust_nbr = c.cust_nbr
    AND co.cancelled_dt IS NULL
    AND co.order_dt > TRUNCATE(SYSDATE) - (5*365)), 'N', 'Y') has_recent_orders
    FROM customer c;

SELECT c.cust_nbr cust_nbr, c.name name,
    CASE WHEN EXISTS (SELECT 1 FROM cust_order co
    WHERE co.cust_nbr = c.cust_nbr AND co.cancelled_dt IS NULL
    AND co.order_dt > TRUNC(SYSDATE) – (5 * 365))
    THEN 'Y' ELSE 'N' END has_recent_orders
FROM customer c;


FUNCTION get_next_order_state(ord_nbr in NUMBER,
trans_type in VARCHAR2 DEFAULT 'POS')
RETURN VARCHAR2 is
next_state VARCHAR2(20) := 'UNKNOWN';
BEGIN
    SELECT CASE
        WHEN status = 'REJECTED' THEN status
        WHEN status = 'CANCELLED' THEN status
        WHEN status = 'SHIPPED' THEN status
        WHEN status = 'NEW' AND trans_type = 'NEG' THEN 'AWAIT_PAYMENT'
        WHEN status = 'NEW' AND trans_type = 'POS' THEN 'PROCESSING'
        WHEN status = 'AWAIT_PAYMENT' AND trans_type = 'NEG' THEN 'REJECTED'
        WHEN status = 'AWAIT_PAYMENT' AND trans_type = 'POS' THEN 'PROCESSING'
        WHEN status = 'PROCESSING' AND trans_type = 'NEG' THEN 'DELAYED'
        WHEN status = 'PROCESSING' AND trans_type = 'POS' THEN 'FILLED'
        WHEN status = 'DELAYED' AND trans_type = 'NEG' THEN 'CANCELLED'
        WHEN status = 'DELAYED' AND trans_type = 'POS' THEN 'PROCESSING'
        WHEN status = 'FILLED' AND trans_type = 'POS' THEN 'SHIPPED'
        ELSE 'UNKNOWN'
        END
    INTO next_state
    FROM cust_order
    WHERE order_nbr = ord_nbr;
    RETURN next_state;
    EXCEPTION
    WHEN NO_DATA_FOUND THEN
    RETURN next_state;
    END get_next_order_state;