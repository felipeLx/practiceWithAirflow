/* PROCEDure */

CREATE [OR REPLACE] PROCEDURE procedure_name 
[(parameter_name [IN | OUT | IN OUT] type [, ...])] 
{IS | AS} 
BEGIN 
  < procedure_body > 
END procedure_name; 
-- The AS keyword is used instead of the IS keyword for creating a standalone procedure.
CREATE OR REPLACE PROCEDURE greetings 
AS 
BEGIN 
   dbms_output.put_line('Hello World!'); 
END; 
/

EXECUTE greetings;

DECLARE 
   a number; 
PROCEDURE squareNum(x IN OUT number) IS 
BEGIN 
  x := x * x; 
END;  
BEGIN 
   a:= 23; 
   squareNum(a); 
   dbms_output.put_line(' Square of (23): ' || a); 
END; 
/