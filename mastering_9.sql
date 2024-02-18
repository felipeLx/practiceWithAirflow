/*
The DECODE, NULLIF, NVL, and NVL2
functions, however, do not solve a specific problem; rather, they are best described
as inline if-then-else statements.
*/

-- DECODE takes three or more expressions as arguments. Each expression can be a column, a literal, a function, or even a subquery.
SELECT lname,
DECODE(manager_emp_id, NULL, 'HEAD HONCHO', 'WORKER BEE') emp_type
FROM employee;
/*
The DECODE function in this example compares each row’s manager_emp_id
column (the first expression) to NULL (the second expression). If the result of the
comparison is true, DECODE returns 'HEAD HONCHO' (the third expression); otherwise,
'WORKER BEE' (the last expression) is returned.

The previous example demonstrates the use of a DECODE function with the mini-
mum number of parameters (four). The next example demonstrates how additional
sets of parameters may be utilized for more complex logic:
*/
SELECT p.part_nbr part_nbr, p.name part_name, s.name supplier,
DECODE(p.status,
'INSTOCK', 'In Stock',
'DISC', 'Discontinued',
'BACKORD', 'Backordered',
'ENROUTE', 'Arriving Shortly',
'UNAVAIL', 'No Shipment Scheduled',
'Unknown') part_status
FROM part p INNER JOIN supplier s
ON p.supplier_id = s.supplier_id;

-- NULLIF is useful if you want to substitute NULL for a column’s value
SELECT fname, lname,
NULLIF(salary, GREATEST(2000, salary)) salary
FROM employee;
/*
GREATEST function returns either the employee’s salary or
2000, whichever is greater. The NULLIF function compares this value to the
employee’s salary and returns NULL if they are the same.
*/

-- NVL2 function is similar to the NVL function, but it takes three arguments
SELECT lname,
NVL2(manager_emp_id, 'WORKER BEE', 'HEAD HONCHO') emp_type
FROM employee;

