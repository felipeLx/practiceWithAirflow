/* Performance anti patterns: non-query DML inside loops */
CREATE OR REPLACE PROCEDURE upd_for_dept (
    dept_in IN employees.department_id%TYPE
    , newsal_in IN employees.salary%TYPE
)
IS
    CURSOR emp_cur
    IS
        SELECT employee_id, salary, hire_date
        FROM employees
        WHERE department_id = dept_in;
BEGIN
    FOR rec IN emp_cur
    LOOP
        BEGIN
            INSERT INTO employee_history (employee_id, salary, hire_date)
            VALUES (rec.employee_id, rec.salary, rec.hire_date);
        
        rec_salary := newsal_in;

        adjust_compensation(rec.employee_id, rec_salary);

        UPDATE employees
        SET salary = rec.salary
        WHERE employee_id = rec.employee_id;
    EXCEPTION
        WHEN OTHERS 
        THEN
            log_error;
        END;
    END LOOP;
END upd_for_dept;

--loop
DECLARE
    i number(1);
    j number(1);
BEGIN
    <<outer_loop>>
    FOR i IN 1..3 LOOP
    <<inner_loop>>
    FOR j IN 1..3 LOOP
    dbms_output.put_line('i='||i||', j='||j);
    END LOOP inner_loop;
    END LOOP outer_loop;
END;
/* types of loops
PL/SQL Basic LOOP: Loop End LOOP
While Loop
For LOOP
Nested Loops
*/

/*
Exit commands:
end loop, continue, goto
*/