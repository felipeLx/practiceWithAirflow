# Tree Calculations w/ Recursion
# Multiplying hierarchical quantities
# To traverse a hierarchy, the traditional method in Oracle is to use the connect by syntax
SELECT
    connect_by_root p.id as p_id,
    connect_by_root p.name as p_name,
    c.id as c_id,
    c.name as c_name,
    ltrim(sys_connect_by_path(pr.qty, ' * '), ' * ') as qty_expr,
    qty * prior qty as qty_mult
FROM packaging_relations pr
JOIN packaging p ON p.id = pr.packaging_id
JOIN packaging c ON c.id = pr.contains_id
WHERE connect_by_isleaf = 1
START WITH pr.packaging_id NOT IN (
    SELECT c.contains_id FROM packaging_relations c
)
connect by pr.packaging_id = prior pr.contains_id
ORDER SIBLINGS BY pr.contains_id;

"""
use the same start w/ and connect by as Listing 4-1, but the filter on connect_
by_isleaf in line 13 makes the output contain only the leaves of each branch.
By using connect_by_root in lines 2 and 3, I get the desired effect in this output that 
p_id is the top-level packaging_id, while c_id is the lowest-level contains_id.
But this is unfortunately not supported w/ the connect by syntax, where prior 
only can be used on the table columns and expressions w/ these, not on column 
aliases of the se_lect list. If I try this modification, I get an error: ORA-00904: "QTY_MULT": 
invalid identifier
"""