-- why you should prefer SWITCH
/*
• CASE expressions can be used everywhere that DECODE functions are permitted.
• CASE expressions are more readable than DECODE expressions.
• CASE expressions execute faster than DECODE expressions. 
• CASE expressions handle complex logic more gracefully than DECODE
expressions.
• CASE is ANSI-compliant, whereas DECODE is proprietary.
*/

SELECT co.order_nbr, co.cust_nbr,
CASE WHEN co.expected_ship_dt IS NULL THEN 'NOT YET SCHEDULED'
WHEN co.expected_ship_dt <= SYSDATE THEN 'SHIPPING DELAYED'
WHEN co.expected_ship_dt <= SYSDATE + 2 THEN 'SHIPPING SOON'
ELSE 'BACKORDERED'
END ship_status
-- all results in a CASE expression must have comparable types; otherwise, ORA-00932 will be thrown.

-- simple CASE expression
SELECT p.part_nbr part_nbr, p.name part_name, s.name supplier,
CASE p.status
WHEN 'INSTOCK' THEN 'In Stock'
WHEN 'DISC' THEN 'Discontinued'
WHEN 'BACKORD' THEN 'Backordered'
WHEN 'ENROUTE' THEN 'Arriving Shortly'
WHEN 'UNAVAIL' THEN 'No Shipment Scheduled'
ELSE 'Unknown'
END part_status
FROM part p INNER JOIN supplier s
ON p.supplier_id = s.supplier_id;

-- PL/SQL
DECLARE
    tot_ord NUMBER;
    tot_price NUMBER;
    max_price NUMBER;
    prev_max_price NUMBER;
BEGIN
    SELECT COUNT(*), SUM(sale_price), MAX(sale_price)
    INTO tot_ord, tot_price, max_price
    FROM cust_order
    WHERE cancelled_dt IS NULL
        AND order_dt >= TRUNC(SYSDATE);
    
    UPDATE mtd_orders
    SET tot_orders = tot_orders + tot_ord,
        tot_sale_price = tot_sale_price + tot_price
    RETURNING max_sale_price INTO prev_max_price;

    IF max_price > prev_max_price THEN
        UPDATE mtd_orders
        SET max_sale_price = max_price;
    END IF;
END;

/*
Using DECODE or CASE, however, you can update the tot_orders and tot_sale_price
columns and optionally update the max_sale_price column in the same UPDATE state-
ment.
*/
UPDATE mtd_orders mtdo
SET (mtdo.tot_orders, mtdo.tot_sale_price, mtdo.max_sale_price) =
    (SELECT mtdo.tot_orders + day_tot.tot_orders,
mtdo.tot_sale_price + NVL(day_tot.tot_sale_price, 0),
DECODE(GREATEST(mtdo.max_sale_price,
NVL(day_tot.max_sale_price, 0)), mtdo.max_sale_price,
mtdo.max_sale_price, day_tot.max_sale_price)
FROM
    (SELECT COUNT(*) tot_orders, SUM(sale_price) tot_sale_price,
    MAX(sale_price) max_sale_price
    FROM cust_order
    WHERE cancelled_dt IS NULL
    AND order_dt >= TRUNC(SYSDATE)) day_tot);

-- case statement
UPDATE mtd_orders mtdo
SET (mtdo.tot_orders, mtdo.tot_sale_price, mtdo.max_sale_price) =
    (SELECT mtdo.tot_orders + day_tot.tot_orders,
    mtdo.tot_sale_price + day_tot.tot_sale_price,
    CASE WHEN day_tot.max_sale_price > mtdo.max_sale_price
    THEN day_tot.max_sale_prices
    ELSE mtdo.max_sale_price END
    FROM
        (SELECT COUNT(*) tot_orders, SUM(sale_price) tot_sale_price,
        MAX(sale_price) max_sale_price
        FROM cust_order
        WHERE cancelled_dt IS NULL
        AND order_dt >= TRUNC(SYSDATE)) day_tot);