CREATE OR REPLACE PACKAGE dimension_pkg AS
  PROCEDURE update_dim (
    p_dim_table_name IN VARCHAR2, -- name of dimension table
    p_data DIM_CONTRATOS -- type that will be used to update the dimension
  );
END dimension_pkg;

CREATE OR REPLACE PACKAGE BODY dimension_pkg AS
  PROCEDURE update_dim (
    p_dim_contratos IN VARCHAR2,
    p_data DIM_CONTRATOS
  ) IS
    v_sql VARCHAR2(32767);
  BEGIN
    v_sql := 'MERGE INTO ' || p_dim_contratos || ' d
              USING (SELECT :1 AS cod_fornec, :2 AS ds_fornecedor) s
              ON (d.cod_fornec = s.cod_fornec)
              WHEN MATCHED THEN
                UPDATE SET d.ds_fornecedor = s.ds_fornecedor
                WHERE d.ds_fornecedor <> s.ds_fornecedor
              WHEN NOT MATCHED THEN
                INSERT (cod_fornec, ds_fornecedor)
                VALUES (s.cod_fornec, s.ds_fornecedor)';
    EXECUTE IMMEDIATE v_sql USING p_data.cod_fornec, p_data.ds_fornecedor;

    EXCEPTION
      WHEN OTHERS THEN
        DBMS_OUTPUT.PUT_LINE('Error updating dimension: ' || SQLERRM);
  END update_dim;
END dimension_pkg;
```


CREATE OR REPLACE PACKAGE dimension_2_pkg AS
  TYPE t_contratos IS TABLE OF DIM_CONTRATOS%ROWTYPE;
  PROCEDURE update_dim (
    p_dim_table_name IN VARCHAR2, -- name of dimension table
    p_data t_contratos -- type that will be used to update the dimension
  );
END dimension_2_pkg;

CREATE OR REPLACE PACKAGE BODY dimension_2_pkg AS
  PROCEDURE update_dim (
    p_dim_table_name IN VARCHAR2,
    p_data t_contratos
  ) IS
    v_sql VARCHAR2(32767);
  BEGIN
    FORALL i IN 1..p_data.COUNT SAVE EXCEPTIONS
      MERGE INTO p_dim_table_name d
      USING (SELECT p_data(i).cod_fornec AS cod_fornec, p_data(i).ds_fornecedor AS ds_fornecedor FROM DUAL) s
      ON (d.cod_fornec = s.cod_fornec)
      WHEN MATCHED THEN
        UPDATE SET d.ds_fornecedor = s.ds_fornecedor
        WHERE d.ds_fornecedor <> s.ds_fornecedor
      WHEN NOT MATCHED THEN
        INSERT (cod_fornec, ds_fornecedor)
        VALUES (s.cod_fornec, s.ds_fornecedor);
  EXCEPTION
    WHEN OTHERS THEN
      FOR i IN 1..SQL%BULK_EXCEPTIONS.COUNT LOOP
        DBMS_OUTPUT.PUT_LINE('Error ' || SQL%BULK_EXCEPTIONS(i).ERROR_CODE || ' at ' || SQL%BULK_EXCEPTIONS(i).ERROR_INDEX);
      END LOOP;
  END update_dim;
END dimension_2_pkg;
```

-- update factual
CREATE OR REPLACE PACKAGE fact_pkg AS
  TYPE t_sales IS TABLE OF FACT_SALES%ROWTYPE;
  
  PROCEDURE update_sales(p_data t_sales);
END fact_pkg;

CREATE OR REPLACE PACKAGE BODY fact_pkg AS
  PROCEDURE update_sales(p_data t_sales) IS
  BEGIN
    FORALL i IN 1..p_data.COUNT SAVE EXCEPTIONS
      MERGE INTO FACT_SALES f
      USING (SELECT p_data(i).product_id AS product_id, p_data(i).sale_date AS sale_date, p_data(i).quantity AS quantity FROM DUAL) s
      ON (f.product_id = s.product_id AND f.sale_date = s.sale_date)
      WHEN MATCHED THEN
        UPDATE SET f.quantity = s.quantity
        WHERE f.quantity <> s.quantity
      WHEN NOT MATCHED THEN
        INSERT (product_id, sale_date, quantity)
        VALUES (s.product_id, s.sale_date, s.quantity);
  EXCEPTION
    WHEN OTHERS THEN
      FOR i IN 1..SQL%BULK_EXCEPTIONS.COUNT LOOP
        DBMS_OUTPUT.PUT_LINE('Error ' || SQL%BULK_EXCEPTIONS(i).ERROR_CODE || ' at ' || SQL%BULK_EXCEPTIONS(i).ERROR_INDEX);
      END LOOP;
  END update_sales;
END fact_pkg;
  DBMS_SCHEDULER.create_job(
    job_name => 'UPDATE_DIM_JOB',
    job_type => 'PLSQL_BLOCK',
    job_action => 'BEGIN dimension_2_pkg.update_dim(''your_dim_table_name'', v_data); END;',
    start_date => SYSTIMESTAMP,
    repeat_interval => 'FREQ=DAILY;BYHOUR=2;', -- This will run the job daily at 2 AM
    enabled => TRUE,
    comments => 'Job to update dimension.'
  );
END;
/
