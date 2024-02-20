-- Deterministic Functions
/* return the same result for any given input parameter */
CREATE OR REPLACE PACKAGE BODY pkg_util AS
FUNCTION translate_date(dt IN DATE) RETURN NUMBER DETERMINISTIC;
FUNCTION translate_date(dt IN NUMBER) RETURN DATE DETERMINISTIC;
END pkg_util;

/* Marking your functions as DETERMINISTIC allows the Oracle server to perform
certain optimizations, such as storing a function’s parameters and results in memory
so that subsequent calls to the same function can be handled without the need to call
the function again. */
