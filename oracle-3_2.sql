# Viewing yearly sales of the beers in alcohol class 1
SELECT
    pac.product_id as p_id,
    EXTRACT(year from ms.mth) as yr,
    SUM(ms.qty) as yr_qty
FROM (
    SELECT
        pa.product_id,
        ntile(2) over (order by pa.abv, pa.product_id) as alc_class
    FROM product_attributes pa
    ) pac
JOIN monthly_sales ms
ON pac.product_id = ms.product_id
WHERE pac.alc_class = 1
GROUP BY pac.product_id,
    EXTRACT(year from ms.mth)
ORDER BY p.id, yr;

"""
As analytic functions cannot be used in a where clause, I need to put the ntile
calculation in an inline view in lines 7–10. In line 14, I keep only those w/ alc_class = 1.
"""
