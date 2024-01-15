# Tree Calculations w/ Recursion
# Recursive subquery factoring is a powerful tool for traversing hierarchies
# Multiplication of quantities w/ recursive subquery factoring
WITH recursive_pr (
    packaging_id, contains_id, qty_mult, level
) AS (
    SELECT
        pr.packaging_id,
        pr.contains_id,
        pr.qty_mult,
        1 AS level
    FROM
        packaging_relations pr
    WHERE
        pr.packaging_id NOT IN (
            SELECT
                c.contains_id
            FROM
                packaging_relations c
        )
    UNION ALL
    SELECT
        pr.packaging_id,
        pr.contains_id,
        rpr.qty * pr.qty_mult as qty,
        rpr.level + 1 as level
    FROM
        recursive_pr rpr
    JOIN packaging_relations pr ON pr.packaging_id = rpr.contains_id
)
    SEARCH DEPTH FIRST BY contains_id SET rpr_order
SELECT
    p.id as p_id,
    lpad(' ', 2 * (rpr.level - 1)) || p.name as p_name,
    c.id as c_id,
    c.name as c_name,
    rpr.qty
FROM recursive_pr rpr
JOIN packaging p ON p.id = rpr.packaging_id
JOIN packaging c
    ON p.id = rpr.contains_id
ORDER BY rpr.rpr_order;
"""
When it is a recursive w/ instead of just a normal w/, it is mandatory to include 
the list of column names, as I do in line 2.
Inside the w/ clause, I need two se_lect statements separated by the union all in 
line 13.
The first se_lect (lines 4–12) finds the top-level nodes of the hierarchy. This is 
equivalent to selecting the rows in the start w/ clause, but can be more complex 
w/, for example, joins.
Recursive subquery factoring does not have a built-in pseudocolumn level, so instead 
I have my own lvl column, which is initialized to 1 for the top-level nodes in line 8.
The second se_lect (lines 14–21) is the recursive part. It must query itself (line 19) 
and join to one or more other tables to find child rows.
In the first iteration, the recursive_pr will contain the level 1 nodes found in the 
preceding text, and the join to packaging_relations in lines 20–21 is equivalent to the 
connect by and finds the level 2 nodes in the tree. In line 18, I add 1 to the lvl value to 
indicate this.
In the second iteration, the recursive_pr will give me the level 2 nodes found in the 
first iteration, and the join finds the level 3 nodes. And so it will be executed repeatedly 
until no more child rows are found
"""