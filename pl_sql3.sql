-- string functions
ASCII(x /*CH CHAR*/);
CHR(x);
CONCAT(x, y);
INITCAP(x);--Converts the initial letter of each word in x to uppercase and returns that string.
INSTR(x, find_string [, start] [, occurrence]); -- Searches for find_string in x and returns the position at which it occurs.
LENGTH(x); -- Returns the length of x.
NANVL(x, value); -- Returns value if x is NaN; otherwise, returns x.
NVL(x, value); -- Returns value if x is null; otherwise, returns x.
REPLACE(P_ /*CHAR*/,
        P_ /*SEARCH_STRING*/,
        P_ /*REPLACEMENT_STRING*/);
TRIM((trim_char FROM) x);--Removes leading and trailing characters from x.

-- varray type
/* A varray type is created with the CREATE TYPE statement.  */
CREATE OR REPLACE TYPE varray_type_ name AS VARRAY(10) OF NUMBER;

-- varray type on pl/sql
DECLARE
  TYPE names_array IS VARRAY(10) OF varchar2(20);
  TYPE grades IS VARRAY(10) OF integer;
  names names_array;
  marks grades;
  total integer;
BEGIN
    names := names_array('John', 'Paul', 'George', 'Ringo');
    marks := grades(90, 80, 85, 75);
    total := names.count;
    dbms_output.put_line('Total number of students: ' || total);
    FOR i in 1 .. total LOOP
        dbms_output.put_line('Student ' || names(i) || ' has scored ' || marks(i));
    END LOOP;
END;

-- use of cursor
DECLARE
    CURSOR c_customer IS
        SELECT name
        FROM customers;
        type c_list is varray(6) of customers.name%type;
        name_list c_list := c_list();
        counter integer := 0;
BEGIN
    FOR n IN c_customer LOOP
        counter := counter + 1;
        name_list.extend;
        name_list(counter) := n.name;
        dbms_output.put_line('Customer ' || counter || ': ' || name_list(counter));
    END LOOP;
END;
/* that will get problem of performance, to fetch row by row, so we can use bulk collect */
-- forall will works by block
CREATE OR REPLACE PROCEDURE upd_for_dept (
    dept_in IN employees.department_id%TYPE
,   newsal_in IN employees.salary%TYPE
,   bulk_limit_in IN PLS_INTEGER DEFAULT 100)
IS
    bulk_errors EXCEPTION;
    FRAGMA EXCEPTION_INIT (bulk_errors, -24381);

    CURSOR employees_cur
    IS
        SELECT employee_id, salary, hire_date
        FROM employees
        WHERE departament_id = dept_in
        FOR UPDATE;
    
    TYPE employee_tt IS TABLE OF employees_cur%ROWTYPE
        INDEX BY PLS_INTEGER;
    
    l_employees employee_tt;

    -- PROCEDURE adj_comp_for_arrays
    -- PROCEDURE insert_history
    PROCEDURE insert_history
    IS
    BEGIN
        FORALL indx IN 1 .. l_employees.COUNT SAVE EXCEPTIONS
            INSERT
                INTO employees_history (employee_id, salary, hire_date)
            VALUES (
                l_employees(indx).employee_id
            ,   l_employees(indx).salary
            ,   l_employees(indx).hire_date);
    EXCEPTION
        WHEN bulk_errors THEN
            FOR indx IN 1 .. SQL%BULK_EXCEPTIONS.COUNT LOOP
                /* Log the error */
                log_error (
                    'unable to insert history row for employee  '
                ||  l_employees(SQL%BULK_EXCEPTIONS(indx).ERROR_INDEX).employee_id
                , SQL%BULK_EXCEPTIONS(indx).ERROR_CODE);
                /* 
                Communicate this failure to the update phase:
                Delete this row so that the update will not take place
                */
                l_employees.delete (
                    SQL%BULK_EXCEPTIONS(indx).ERROR_INDEX);
            END LOOP;
    END insert_history;
    -- PROCEDURE update_employees
    PROCEDURE update_employees
    IS
    BEGIN
        /*
        Use INDEX OF to avoid errors
        from a sparsely-populated employee_ids collection
        */
        FORALL indx IN INDICES OF l_employees
            SAVE EXCEPTIONS
            UPDATE employees
            SET salary = l_employees (indx).salary
            , hire_date = l_employees (indx).hire_date
            WHERE employee_id = l_employees (indx).employee_id;
    EXCEPTION
        WHEN bulk_errors THEN
            FOR indx IN 1 .. SQL%BULK_EXCEPTIONS.COUNT LOOP
                /* Log the error */
                log_error (
                    'unable to update SALARY FOR employee  '
                ||  l_employees(SQL%BULK_EXCEPTIONS(indx).ERROR_INDEX).employee_id
                , SQL%BULK_EXCEPTIONS(indx).ERROR_CODE);
            END LOOP;
    END update_employees;
BEGIN
    OPEN employees_cur;
    LOOP
        FETCH employees_cur 
        BULK COLLECT INTO l_employees 
        LIMIT bulk_limit_in;
        
        EXIT WHEN l_employees.COUNT = 0;

        insert_history;
        adj_comp_for_arrays;
        update_employees;
    END LOOP;
END upd_for_dept;
