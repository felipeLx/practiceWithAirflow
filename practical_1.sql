/*
Practical Oracle SQL Mastering the Full Power of Oracle Database
*/
-- pag - yearly sales of the three beers from shop 1
select
 bp.brewery_name
, bp.product_id as p_id
, bp.product_name
, ys.yr
, ys.yr_qty
from brewery_products bp
join yearly_sales ys
on ys.product_id = bp.product_id
where bp.brewery_id = 518
order by bp.product_id, ys.yr;

-- pag 5 - retrieving two column from the best-selling year per beer
SELECT
 bp.brewery_name
 , bp.product_id as p_id
 , bp.product_name
 , (
    select ys.yr
    from yearly_sales ys
    where ys.product_id = bp.product_id
    order by ys.yr_qty DESC
    fetch first row only
 ) as yr
 , (
    select ys.yr_qty
    from yearly_sales ys
    where ys.product_id = bp.product_id
    order by ys.yr_qty DESC
    fetch first row only
 ) a yr_qty
FROM brewery_products bp
WHERE bp.brewery_id = 518
ORDER BY bp.product_id;
-- Since my order by is not unique, my fetch first row will return a random one

-- pag 6 - Using just a single scalar subquery and value concatenation
SELECT
  brewery_name
 , product_id as p_id
 , product_name
 , to_number(
    SUBSTR(yr_qty_str, 1, INSTR(yr_qty_str, ';') -1)
 ) as yr
    , to_number(
        SUBSTR(yr_qty_str, INSTR(yr_qty_str, ';') + 1)
    ) as yr_qty
FROM (
    SELECT
     bp.brewery_name
     , bp.product_id
     , bp.product_name
     -- scalar subquery below
     , (
        select ys.yr || ';' || ys.yr_qty
        from yearly_sales ys
        where ys.product_id = bp.product_id
        order by ys.yr_qty DESC
        fetch first row only
     ) as yr_qty_str
    FROM brewery_products bp
    WHERE bp.brewery_id = 518
)
order by product_id;
-- query will have problem with LOD columns

-- pag 7 - Using analytic function to be able to retrieve all columns if desired
SELECT
  brewery_name
 , product_id as p_id
 , product_name
 , yr
 , yr_qty
 from (
    select
        bp.brewery_name
        , bp.product_id
        , bp.product_name
        , ys.yr
        , ys.yr_qty
        , row_number() over (partition by bp.product_id order by ys.yr_qty DESC) as rn
-- join the two views instead of querying yearly_sales in a scalar subquery: it impossible to use the fetch first (does not support a partition clause)
    from brewery_products bp
    join yearly_sales ys
    on ys.product_id = bp.product_id
    where bp.brewery_id = 518
 )
    where rn = 1
    order by product_id;

-- pag 9 - Achieving the same with a lateral inline view
SELECT
  bp.brewery_name
 , bp.product_id as p_id
 , bp.product_name
 , top_ys.yr
 , top_ys.yr_qty
FROM brewery_products bp
CROSS JOIN LATERAL (
    SELECT
     ys.yr
     , ys.yr_qty
    FROM yearly_sales ys
    WHERE ys.product_id = bp.product_id
    ORDER BY ys.yr_qty DESC
    FETCH FIRST ROW ONLY
) top_ys
WHERE bp.brewery_id = 518
ORDER BY bp.product_id;

