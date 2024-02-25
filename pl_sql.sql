/*
https://www.tutorialspoint.com/plsql/plsql_basic_syntax.htm

Basic Syntax of PL/SQL which is a block-structured language
Each block consists of three sub-parts: a declarative part (DECLARE), an executable part (BEGIN...END), and an exception-building part (exception).
*/

-- hello world
DECLARE
    message VARCHAR2(20) := 'Hello, World!';
BEGIN
/*
* dbms executable statement(s)
*/
    dbms_output.put_line(message);
END;
/

/*
PL/SQL program units:
- PL/SQL BLOCK
- FUNCTION
- PROCEDURE
- PACKAGE
- PACKAGE BODY
- TRIGGER
- TYPE
- TYPE BODY
*/
DECLARE 
   SUBTYPE name IS char(20); 
   SUBTYPE message IS varchar2(100); 
   salutation name; 
   greetings message; 
BEGIN 
   salutation := 'Reader '; 
   greetings := 'Welcome to the World of PL/SQL'; 
   dbms_output.put_line('Hello ' || salutation || greetings); 
END; 
/ 

-- variables
-- not case-sensitive
/*
PL/SQL variables must be declared in the declaration section or in a package as a global variable. When you declare a variable, PL/SQL allocates memory for the variable's value and the storage location is identified by the variable name.
variable_name [CONSTANT] datatype [NOT NULL] [:= | DEFAULT initial_value] 
*/
sales NUMBER(10,2);
pi CONSTANT DOUBLE PRECISION := 3.14;
address VARCHAR2(100);

DECLARE 
   a integer := 10; 
   b integer := 20; 
   c integer; 
   f real; 
BEGIN 
   c := a + b; 
   dbms_output.put_line('Value of c: ' || c); 
   f := 70.0/3.0; 
   dbms_output.put_line('Value of f: ' || f); 
END; 
/  

/* Variable scope in PL/SQL 
Local variables − Variables declared in an inner block and not accessible to outer blocks.
Global variables − Variables declared in the outermost block or a package.
*/
DECLARE 
   -- Global variables  
   num1 number := 95;  
   num2 number := 85;  
BEGIN  
   dbms_output.put_line('Outer Variable num1: ' || num1); 
   dbms_output.put_line('Outer Variable num2: ' || num2); 
   DECLARE  
      -- Local variables 
      num1 number := 195;  
      num2 number := 185;  
   BEGIN  
      dbms_output.put_line('Inner Variable num1: ' || num1); 
      dbms_output.put_line('Inner Variable num2: ' || num2); 
   END;  
END; 
/ 
