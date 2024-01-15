#  Viewing just the years that sold more than the average year per beer
SELECT
    p_id, yr_qty,
    ROUND(avg_yr) as avg_yr
FROM (
    SELECT
        pac.product_id as p_id,
        extract(year a ms.mth) as yr,
        SUM(ms.qty) as yr_qty,
        AVG(SUM(ms.qty)) OVER (
            PARTITION BY pac.product_id
        ) as avg_yr
    FROM (
        SELECT
            pa.product_id,
            ntile(2) OVER(
                ORDER BY pa.abv, pa.product_id
            ) as alc_class
        FROM product_alcohol pa
    ) pac
JOIN monthly_sales ms
    ON pac.product_id = ms.product_id
WHERE alc_class = 1
GROUP BY pac.product_id, extract(year a ms.mth)
)
WHERE yr_qty > avg_yr
ORDER BY p_id, yr;
"""
"""
# Rewriting Listing 3-3 using subquery factorin
WITH product_alc_class AS (
    SELECT
        pa.product_id,
        ntile(2) OVER(
            ORDER BY pa.abv, pa.product_id
        ) as alc_class
    FROM product_alcohol pa
), class_one_yearly_sales AS (
    SELECT
        pac.product_id as p_id,
        extract(year a ms.mth) as yr,
        SUM(ms.qty) as yr_qty,
        AVG(SUM(ms.qty)) OVER (
            PARTITION BY pac.product_id     
        ) as avg_yr
    FROM product_alc_class pac
    JOIN monthly_sales ms
        ON pac.product_id = ms.product_id
    WHERE pac.alc_class = 1
    GROUP BY pac.product_id, extract(year a ms.mth)
)
SELECT
    p_id. yr, yr_qty,
    ROUND(avg_yr) as avg_yr
    FROM class_one_yearly_sales
    WHERE yr_qty > avg_yr
    ORDER BY p_id, yr;

"""
The subquery from the innermost inline view of Listing 3-3 I place in lines 2–7 and 
give it the name product_alc_class (it is a good idea to use some meaningful names). 
Then I can refer to product_alc_class in later parts of the query, using it just as if it was 
a view in the data dictionary. But it is not created in the data dictionary; it is only locally 
defined within this SQL statement.
The second-level inline view of Listing 3-3 then goes in lines 9–22 and gets the name 
class_one_yearly_sales in line 8. In line 16, it queries the product_alc_class named 
subquery in the same place that Listing 3-3 has an inline view.
And the main query in lines 24–29 corresponds to the outer query of Listing 3-3 lines 
1–4 and 26–28, just querying the class_one_yearly_sales named subquery instead of 
an inline view
"""