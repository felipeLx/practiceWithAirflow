/*
PL/SQL is a procedural programming language from Oracle that combines the fol-
lowing elements:
• Logical constructs such as IF-THEN-ELSE and WHILE
• SQL DML statements, built-in functions, and operators
• Transaction control statements such as COMMIT and ROLLBACK
• Cursor control statements
• Object and collection manipulation statements
PL/SQL routines stored in the database may be one of two types: stored procedures
or stored functions. * Stored functions and procedures are essentially identical except
for the following:
• Stored functions have a return type, whereas procedures do not.
• Because stored functions return a value, they can be used in expressions,
whereas procedures cannot.

Placing functions and procedures inside packages eliminates the need to recompile
all functions and procedures that reference a newly recompiled function/procedure.

Packages consist of two distinct parts: a package specification, which defines the sig-
natures of the package’s public procedures and functions, and a package body, which
contains the code for the public procedures and functions and may also contain code
for any private functions and procedures not included in the package specification.
*/

CREATE OR REPLACE PACKAGE process_mgmt AS
  PROCEDURE raise_salary (emp_id IN NUMBER, amount IN NUMBER);
  FUNCTION get_salary (emp_id IN NUMBER) RETURN NUMBER;
END emp_mgmt;

CREATE OR REPLACE PACKAGE BODY process_mgmt AS
  PROCEDURE raise_salary (emp_id IN NUMBER, amount IN NUMBER) IS
  BEGIN
    UPDATE employees
    SET salary = salary + amount
    WHERE employee_id = emp_id;
  END raise_salary;
  FUNCTION get_salary (emp_id IN NUMBER) RETURN NUMBER IS
    sal NUMBER;
  BEGIN
    SELECT salary INTO sal
    FROM employees
    WHERE employee_id = emp_id;
    RETURN sal;
  END get_salary;
END emp_mgmt;

-- other example
CREATE OR REPLACE PACKAGE my_pkg AS
    PROCEDURE my_proc (arg1 IN VARCHAR2);
    FUNCTION my_func (arg1 IN NUMBER) RETURN VARCHAR2;
END my_pkg;

CREATE OR REPLACE PACKAGE BODY my_pkg AS
    FUNCTION my_private_func (arg1 IN NUMBER) RETURN VARCHAR2 IS
        return_val VARCHAR2(100);
    BEGIN
        SELECT col1 INTO return_val
        FROM tab2
        WHERE col2 = arg1;

        RETURN return_val;
    EXCEPTION
        WHEN NO_DATA_FOUND THEN
            RETURN 'NOT DATA';
    END my_private_func;

    PROCEDURE my_proc (arg1 IN VARCHAR2) IS
    BEGIN
        UPDATE tab1 SET col1 = col1 + 1
        WHERE col2 = arg1;
    END my_proc;

    FUNCTION my_func (arg1 IN NUMBER) RETURN VARCHAR2 IS
    BEGIN
        RETURN my_private_func(arg1);
    END my_func;
END my_pkg;

-- One of the most common uses of stored functions is to isolate commonly-used functionality to facilitate code reuse and simplify maintenance.
/* build a utility package that includes
functions for translating between Oracle’s internal date format and the desired format */
CREATE OR REPLACE PACKAGE BODY pkg_util AS
    FUNCTION translate_date(dt IN DATE) RETURN NUMBER IS
    BEGIN
    RETURN ROUND((dt - TO_DATE('01011970','MMDDYYYY')) * 86400 * 1000);
    END translate_date;
    
    FUNCTION translate_date(dt IN NUMBER) RETURN DATE IS
    BEGIN
    RETURN TO_DATE('01011970','MMDDYYYY') + (dt / (86400 * 1000));
    END translate_date;
END pkg_util;

SELECT co.order_nbr, co.cust_nbr, co.sale_price,
    pkg_util.translate_date(co.order_dt) utc_order_dt
FROM cust_order co
WHERE co.ship_dt = TRUNC(SYSDATE);

-- to simplify and hide complex IF-THEN-ELSE logic from your SQL statements
/* generate a report detail-
ing all customer orders for the past month */
-- You could utilize a CASE statement in the ORDER BY clause
SELECT co.order_nbr, co.cust_nbr, co.sale_price
FROM cust_order co
WHERE co.order_dt > TRUNC(SYSDATE, 'MONTH')
    AND co.cancelled_dt IS NULL
ORDER BY
    CASE
        WHEN co.ship_dt IS NOT NULL THEN co.ship_dt
        WHEN co.expected_ship_dt IS NOT NULL
        AND co.expected_ship_dt > SYSDATE
            THEN co.expected_ship_dt
        WHEN co.expected_ship_dt IS NOT NULL
        THEN GREATEST(SYSDATE, co.expected_ship_dt)
        ELSE co.order_dt
    END;

-- better aproach: add a stored function to the pkg_util package that returns the appropriate date for a given order
FUNCTION get_best_order_date(order_dt IN DATE, exp_ship_dt IN DATE, ship_dt IN DATE) RETURN DATE IS
BEGIN
    IF ship_dt IS NOT NULL THEN
        RETURN ship_dt;
    ELSIF exp_ship_dt IS NOT NULL AND exp_ship_dt > SYSDATE THEN
        RETURN exp_ship_dt;
    ELSIF exp_ship_dt IS NOT NULL THEN
        RETURN SYSDATE;
    ELSE
        RETURN order_dt;
    END IF;
END get_best_order_date;

SELECT co.order_nbr, co.cust_nbr, co.sale_price,
    pkg_util.get_best_order_date(co.order_dt, co.expected_ship_dt, co.ship_dt) best_date
FROM cust_order co
WHERE co.order_dt > TRUNC(SYSDATE, 'MONTH')
    AND co.cancelled_dt IS NULL
ORDER BY pkg_util.get_best_order_date(co.order_dt, co.expected_ship_dt, co.ship_dt);

SELECT orders.order_nbr, orders.cust_nbr,
orders.sale_price, orders.best_date
FROM
(SELECT co.order_nbr order_nbr, co.cust_nbr cust_nbr,
co.sale_price sale_price,
pkg_util.get_best_order_date(co.order_dt, co.expected_ship_dt,
co.ship_dt) best_date
FROM cust_order co
WHERE co.order_dt > TRUNC(SYSDATE, 'MONTH')
AND co.cancelled_dt IS NULL) orders
ORDER BY orders.best_date;

-- can be called from the SELECT clause of a query
CREATE OR REPLACE VIEW vw_example
(col1, col2, col3, col4, col5, col6, col7, col8)
AS SELECT t1.col1,
t1.col2,
t2.col3,
t2.col4,
pkg_example.func1(t1.col1, t2.col3),
pkg_example.func2(t1.col2, t2.col4),
pkg_example.func3(t1.col1, t2.col3),
pkg_example.func4(t1.col2, t2.col4)
FROM tab1 t1 INNER JOIN tab2 t2
ON t1.col1 = t2.col3;

