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
CROSS JOIN LATERAL (
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

# lines 36–42 queries yearly_sales and uses the fetch first row to find the row of the year w/ the highest sales. But it is not executed for all beers finding a single row w/ the best-selling year across all beers, for line 13 correlates the yearly_sales to the brewery_products on product_id.
"""
Placed the keyword lateral in front of the inline view in line 35, which tells the database that I want a correlation here, so it should execute the inline view once for each row of the correlated outer row source – in this case brewery_products. That means that for each beer, there will be executed an individual fetch first row query, almost as if it were a scalar subquery.•I then use cross join in line 35 to do the actual joining, which simply is because I need no on clause in this case. I have all the correlation I need in line 40, so I need not use an inner or outer join.
"""