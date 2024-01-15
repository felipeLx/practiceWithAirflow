# Retrieving two columns from the best-selling year per beer
select
    bp.brewery_name, 
    bp.product_id as p_id,
    bp.product_name,
    (select 
        ys.yr
    from yearly_sales ys
    where ys.product_id = bp.product_id
    order by ys.yr_qty desc 
    fetch first row only
    ) as yr, 
    (select 
        ys.yr_qty 
    from yearly_sales ys 
    where ys.product_id = bp.product_id 
    order by ys.yr_qty desc 
    fetch first row only
    ) as yr_qty 
    from brewery_products bp 
where bp.brewery_id = 518 
order by bp.product_id;


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
    year,
    yr_qty
FROM (
    SELECT
        bp.brewery_name,
        bp.product_id,
        bp.product_name,
        ys.year,
        ROW_NUMBER() OVER (PARTITION BY bp.product_id ORDER BY ys.yr_qty DESC) AS row_num
    FROM brewery_products bp
    JOIN yearly_sales ys ON bp.product_id = ys.product_id
    WHERE bp.brewery_id = 518
) AS sub
WHERE row_num = 1
ORDER BY product_id;

# Using the rank analytic function to assign consecutive numbers 1, 2, 3 … in descending order of yr_qty, in effect giving the row w/ the highest yr_qty the value 1 in rn. This happens for each beer because of the partition by, so there will be a row w/ rn=1 for each beer. These rows I keep w/ the where clause in line 35.