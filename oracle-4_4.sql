# Tree Calculations w/ Recursion
#  Alternative method using dynamic evaluation function
WITH function evaluate_expr (
    p_expr varchar2
    ) 
        return number
    is
        l_retval number;
    begin
        execute immediate 'select ' || p_expr || ' from dual' into l_retval;
        return l_retval;
    end;
SELECT
    connect_by_root p.id as p_id,
    connect by_root p.name as p_name,
    c.id as c_id,
    c.name as c_name,
    ltrim(sys_connect_by_path(pr.qty, '*'), '*') as qty_expr,
    evaluate_expr(ltrim(sys_connect_by_path(pr.qty, '*'), '*')) as qty_mult
FROM packaging_relations pr
    JOIN packaging p
        ON p.id = pr.packaging_id
    JOIN packaging c
        ON c.id = pr.contains_id
WHERE
    connect_by_isleaf = 1
START WITH pr.packaging_id not in (
    SELECT c.contains_id
    FROM packaging_relations c
)
connect by pr.packaging_id = prior pr.contains_id
order siblings by pr.contains_id;
"""

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