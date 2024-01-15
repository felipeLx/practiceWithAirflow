#  Specifying column names list instead of column aliases
WITH product_alc_class (
    product_id, alc_class
) AS (
    SELECT
        pa.product_id,
        ntile(2) OVER(
            ORDER BY pa.abv, pa.product_id
        ) as alc_class
    FROM product_alcohol pa
), yearly_sales (
        product_id, yr, yr_qty, avg_yr
    ) as (
        SELECT
            ms.product_id,
            extract(year from ms.mth),
            sum(ms.qty),
            avg(sum(ms.qty)) over (
                partition by ms.product_id
            )
        FROM monthly_sales ms
        WHERE ms.product_id IN (
            SELECT pac.product_id
            FROM product_alc_class pac
            WHERE pac.alc_class = 1
        )   
        GROUP BY ms.product_id, extract(year from ms.mth)
    ) 
SELECT
    pac.product_id as p.id,
    ys.yr, ys.yr_qty, ROUND(ys.avg_yr) as avg_yr
FROM product_alc_class pac
JOIN yearly_sales ys
    ON pac.product_id = ys.product_id
WHERE ys.yr_qty > ys.avg_yr
ORDER BY p_id, yr;

"""
For each of my named subqueries in the w/ clause, I in_sert between the query 
name and the as keyword a set of parentheses w/ a list of column names (lines 1–3 
and lines 10–12). This overrules whatever column names and/or aliases returned by the 
subqueries themselves – I do not even have to provide column aliases, as you can see in 
line 8 and lines 15–19
"""