/* avoid hard code split functions into package */
-- package to open or close a Procedure

Create or replace package app_config_pkg is
    FUNCTION open_status RETURN VARCHAR2 DETERMINISTIC;
    FUNCTION close_status RETURN VARCHAR2 DETERMINISTIC;
end;
/
create or replace PACKAGE body app_config_pkg is
    /* constant is really fast to be access */
    c_private_open CONSTANT VARCHAR2 (4) := 'open';
    c_private_close CONSTANT VARCHAR2 (5) := 'closed';
    FUNCTION open_status RETURN VARCHAR2 DETERMINISTIC
    IS
    BEGIN
        RETURN c_private_open;
    END open_status;
    FUNCTION close_status RETURN VARCHAR2 DETERMINISTIC
    IS
    BEGIN
        RETURN c_private_close;
    END close_status;
end;


/* create table for magic values */
-- package to retrieve magic values by name
create or replace PACKAGE magic_value_for (NAME_IN IN VARCHAR2)
    RETURN VARCHAR2 DETERMINISTIC RESULT_CACHE
IS
    l_return magic_values.magic_value%TYPE;
BEGIN
    SELECT magic_value
    INTO l_return
    FROM magic_values mv
    WHERE mv.name = NAME_IN;
    RETURN l_return;
EXCEPTION
    WHEN NO_DATA_FOUND THEN
        RETURN NULL;
end magic_value_for;

CREATE TABLE magic_values
(
    name        VARCHAR2(100) NOT NULL,
    identifier VARCHAR2(30),
    magic_value VARCHAR2(100) NOT NULL,
    datatype    VARCHAR2(30) NOT NULL,
)
/
-- generate code based on contents of table
BEGIN
    INSERT INTO magic_values
        VALUES ('maximum Salary', 'max_salary', 10000, 'number');
    INSERT INTO magic_values
        VALUES ('Company Name', 'company_name', 'NTL Corporate', 'varchar2');
    INSERT INTO magic_values
        VALUES ('Earliest Date', 'earliest_date', '01-JAN-2000', 'date');
    COMMIT;
END;

CREATE OR REPLACE PACKAGE magic_value_mgr
IS
    FUNCTION company_name RETURN VARCHAR2 DETERMINISTIC RESULT_CACHE;
    FUNCTION earliest_date RETURN DATE DETERMINISTIC RESULT_CACHE;
    FUNCTION max_salary RETURN NUMBER DETERMINISTIC RESULT_CACHE;
END magic_value_mgr;
/
CREATE OR REPLACE PACKAGE BODY magic_value_mgr
IS
    FUNCTION company_name RETURN VARCHAR2 DETERMINISTIC RESULT_CACHE
    IS
    BEGIN
        RETURN 'NTL Corporate';
    END company_name;
    FUNCTION earliest_date RETURN DATE DETERMINISTIC RESULT_CACHE
    IS
    BEGIN
        RETURN TO_DATE(magic_value_for('Earliest Date'), 'DD-MON-YYYY');
    END earliest_date;
    FUNCTION max_salary RETURN NUMBER DETERMINISTIC RESULT_CACHE
    IS
    BEGIN
        RETURN TO_NUMBER(magic_value_for('maximum Salary'));
    END max_salary;
END magic_value_mgr;