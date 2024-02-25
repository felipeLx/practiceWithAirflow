create or replace PACKAGE employee_rp
AS
  TYPE employee_aat IS TABLE OF employees%ROWTYPE INDEX BY PLS_INTEGER;

  c_min_ceo_salary CONST PLS_INTEGER := 10000000;

  SUBTYPE t_performance_type IS INTEGER;
  SUBTYPE fullname_t IS VARCHAR2(100);

  FUNCTION fullname (l employees.last_name%TYPE
  , f employees.first_name%TYPE
  , use_f_l_in IN BOOLEAN:= FALSE) RETURN fullname_t;

  FUNCTION fullname (l employees.last_name%TYPE
  , f employees.first_name%TYPE
  , use_f_l_in IN PLS_INTEGER := 0) RETURN fullname_t;

  /* now the procedure can make reference for the package constant */
  PROCEDURE process_employee (departament_in IN NUMBER)
  IS 
    l_id NUMBER;
    l_salary NUMBER(9,2);
    l_name employees_rp.fullname_t;
    '''