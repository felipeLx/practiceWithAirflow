#  Tree Calculations w/ Recursion
#  The hierarchical relations of the different packaging types can be represented as a tree.
SELECT
    p.id as p_id,
    lpad('', 2 * (level() - 1), '.') || p.name as p_name,
    c.id as c_id,
    c.name as c_name,
    pr.qty
FROM packaging_relations pr
JOIN packaging p ON p.id = pr.packaging_id
JOIN packaging c ON c.id = pr.contains_id
START WITH pr.packaging_id NOT IN(
    SELECT c.contains_id
    FROM packaging_relations c
)
CONNECT BY pr.packaging_id = PRIOR pr.contains_id
ORDER SIBLINGS BY pr.contains_id;
"""
In start w/ in lines 12–14, I start at the top-level pallets, because any packaging 
that exists as contains_id in packaging_relations is by definition not at the top level. 
The hierarchy is then traversed by the connect by in line 15
"""