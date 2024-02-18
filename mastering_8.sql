/*
To represent hierarchical data, you need to
make use of a relationship such as when one column of a table references another
column of the same table. When such a relationship is implemented using a data-
base constraint, it is known as self-referential integrity constraint.
*/
-- from Oracle mastering- hierarchical
-- finding a node in a tree
SELECT e.lname "Employee", m.laname `Manager`
  FROM employees e LEFT OUTER JOIN employees m
  ON e.mgr_employee_id = m.empid;

-- finding leaf nodes in a tree
SELECT emp_id, lname, dept_id, manager_id, salary, hire_date
  FROM employee e
  WHERE emp_id NOT IN 
  (SELECT mgr_employee_id FROM employees
  WHERE mgr_employee_id IS NOT NULL);

/*
  you can extract information in hierarchical form from a table containing hierarchi-
cal data by using the SELECT statement’s START WITH...CONNECT BY clause.
START WITH condition1
Specifies the root row(s) of the hierarchy. All rows that satisfy condition1 are
considered root rows. If you don’t specify the START WITH clause, all rows are
considered root rows, which is usually not desirable. You can include a sub-
query in condition1 .
CONNECT BY condition2
Specifies the relationship between parent rows and child rows in the hierarchy.
The relationship is expressed as a comparison expression, where columns from
the current row are compared to corresponding parent columns. condition2
must contain the PRIOR operator, which is used to identify columns from the
parent row. condition2 cannot contain a subquery.
*/
SELECT lname,  empid, mgr_employee_id
  FROM employees
  START WITH mgr_employee_id IS NULL
  CONNECT BY PRIOR empid = mgr_employee_id;
/*
use a sub-
query to generate the information needed to evaluate the condition and pass that
information to the main query, as in the following example:
*/
SELECT lname, emp_id, manager_emp_id
FROM employee
START WITH hire_date = (SELECT MIN(hire_date) FROM employee)
CONNECT BY manager_emp_id = PRIOR emp_id;

-- pseudocolumn LEVEL to return the level number for each row returned by the query.
SELECT level, lname, emp_id, manager_emp_id
FROM employee
START WITH manager_emp_id IS NULL
CONNECT BY manager_emp_id = PRIOR emp_id;

-- finding number of levels
SELECT MAX(level) FROM employee
START WITH manager_emp_id IS NULL
CONNECT BY PRIOR manager_emp_id = emp_id;

SELECT level, COUNT(emp_id) FROM employee
START WITH manager_emp_id IS NULL
CONNECT BY PRIOR manager_emp_id = emp_id
GROUP BY level;

/*
to find the uppermost employee in each department, you need to search
the tree for those employees whose managers belong to a different department than
their own.
*/
SELECT emp_id, lname, dept_id, manager_emp_id, salary, hire_date
FROM employee
START WITH manager_emp_id IS NULL
CONNECT BY manager_emp_id = PRIOR emp_id
AND dept_id != PRIOR dept_id;

-- consider each employee as a root, and for each employee you want to sum the salaries of all employees in its subtree
