# Functions Defined Within SQL
#  writing functions that SQL can call
SELECT
    p.id as p_id,
    p.name,
    pa.sales_volume as vol,
    pa.abv
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