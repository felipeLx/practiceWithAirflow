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


# Achieving the same w/ a lateral inline view
"""
"""
SELECT
    bp.brewery_name,
    bp.product_id as p_id,
    bp.product_name,
    top_ys.yr,
    top_ys.yr_qty
FROM brewery_products bp
CROSS APPLY (
    SELECT
        ys.yr,
        ys.yr_qty
    FROM yearly_sales ys
    WHERE ys.product_id = bp.product_id
    ORDER BY ys.yr_qty DESC
    FETCH FIRST ROW ONLY
) top_ys
WHERE bp.brewery_id = 518
ORDER BY bp.product_id;

"""
use apply, I am allowed to correlate the inline view w/ the predicate in line 40,  just like using lateral. Behind the scenes, the database does exactly the same as a lateral inline view; it is just a case of which syntax you prefer.
"""