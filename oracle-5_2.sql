# Functions Defined Within SQL
#  Calculating blood alcohol concentration for male and female
SELECT
    p.id as p_id,
    p.name,
    pa.sales_volume as vol,
    pa.abv,
    round(
        100 * (pa.sales_colume * pa.abv /100 * 0.789) ,
FROM products p
JOIN product_alcohol pa
    ON pa.product_id = p.id
WHERE p.group_id = 142
ORDER BY p.id;

"""
This data can be used to find out how much pure alcohol one bottle of beer contains, 
which is needed to find out how much the blood alcohol concentration (BAC) will be 
increased by drinking one such bottle
"""