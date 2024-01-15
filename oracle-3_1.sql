# Best-selling years of the less strong beers
# Dividing the beers into alcohol class 1 and 2
SELECT
    pa.product_id as p_id,
    p.product_name as  p_name,
    pa.abv,
    ntile(2) OVER (
        ORDER BY pa.abv, pa.product_id
    ) as alc_class
FROM product_alcohol pa
JOIN products p
    ON pa.product_id = p.id
ORDER BY pa.abv, pa.product_id;

"""
analytic function ntile in lines 7–9 assigns each row into buckets – the number 
of buckets being the argument. It will be assigned in the order given by the order by
clause and such that the rows are distributed as evenly as possible
"""
