# The yearly sales of the three beers from Balthazar Brauerei
SELECT
    bp.brewery_name,
    bp.product_id as p_id,
    bp.product_name,
    ys.year,
    ys.year_quantity
FROM brewery_products bp
JOIN yearly_sales ys ON bp.product_id = ys.product_id
WHERE bp.brewery_id = 518
ORDER BY bp.product_id, ys.year DESC;

# analytic functions
"""
row_number analytic function to assign consecutive
numbers 1, 2, 3 … in descending order of yr_qty, in effect giving the row w/ the highest yr_qty the value 1 in rn.
This happens for each beer because of the partition by, so there will be a row w/ rn=1 for each beer. These rows I keep w/ the where
clause in line 35.
"""
SELECT
    brewery_name,
    product_id as p_id,
    product_name,
    year
FROM (
    SELECT
        bp.brewery_name,
        bp.product_id,
        bp.product_name,
        ys.year,
        ROW_NUMBER() OVER (PARTITION BY bp.product_id ORDER BY ys.year DESC) AS row_num
    FROM brewery_products bp
    JOIN yearly_sales ys ON bp.product_id = ys.product_id
    WHERE bp.brewery_id = 518
) AS sub
WHERE row_num = 1
ORDER BY product_id;