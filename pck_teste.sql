CREATE OR REPLACE PACKAGE BODY update_dim_pck AS

  PROCEDURE update_dim (
    p_dim_name IN VARCHAR2,
    p_source_data IN update_dim_pck.source_data_t
  ) IS
    l_dim_record dim_table%ROWTYPE;
    l_update_count INTEGER := 0;
    l_insert_count INTEGER := 0;

  BEGIN
    -- Loop through source data
    FOR rec IN p_source_data LOOP
      -- Check if record exists in dimension table
      SELECT * 
      INTO l_dim_record
      FROM user_tables  -- Replace with your actual schema
      WHERE table_name = p_dim_name
        AND id = rec.id;

      -- Update existing record
      IF FOUND THEN
        IF l_dim_record.column_to_update != rec.column_to_update THEN
          l_dim_record.column_to_update := rec.column_to_update;
          l_update_count := l_update_count + 1;
        END IF;
      -- Insert new record
      ELSE
        l_dim_record := rec;
        l_insert_count := l_insert_count + 1;
      END IF;
    END LOOP;

    -- Bulk UPDATE and INSERT
    IF l_update_count > 0 THEN
      FOR rec IN p_source_data LOOP
        UPDATE user_tables  -- Replace with your actual schema
        SET column_to_update = rec.column_to_update
        WHERE table_name = p_dim_name
          AND id = rec.id;
      END LOOP;
    END IF;

    IF l_insert_count > 0 THEN
      FOR rec IN p_source_data LOOP
        INSERT INTO user_tables  -- Replace with your actual schema
        (id, column_to_update)
        VALUES (rec.id, rec.column_to_update);
      END LOOP;
    END IF;

    DBMS_OUTPUT.PUT_LINE('Updated records: ' || l_update_count);
    DBMS_OUTPUT.PUT_LINE('Inserted records: ' || l_insert_count);
  END;
END update_dim_pck;

/

CREATE OR REPLACE PACKAGE BODY update_dim_pck AS
-- aproch with source_data from cursor
  PROCEDURE update_dim (
    p_dim_name IN VARCHAR2,

    p_source_cursor IN SYS_REFCURSOR

  ) IS

    l_dim_record dim_table%ROWTYPE;

    l_update_count INTEGER := 0;

    l_insert_count INTEGER := 0;

    l_source_record source_record_t;

 

  BEGIN

    -- Loop through each record in the source cursor

    OPEN p_source_cursor;

    LOOP

      FETCH p_source_cursor INTO l_source_record;

      EXIT WHEN p_source_cursor%NOTFOUND;



      -- Check if record exists in dimension table

      SELECT * 

      INTO l_dim_record

      FROM user_tables  -- Replace with your actual schema

      WHERE table_name = p_dim_name

        AND id = l_source_record.id;



      -- Update existing record

      IF FOUND THEN

        IF l_dim_record.column_to_update != l_source_record.column_to_update THEN

          l_dim_record.column_to_update := l_source_record.column_to_update;

          l_update_count := l_update_count + 1;

          UPDATE user_tables  -- Replace with your actual schema

          SET column_to_update = l_dim_record.column_to_update

          WHERE table_name = p_dim_name

            AND id = l_source_cursor.id%ROWTYPE.id;

        END IF;

      -- Insert new record

      ELSE

        l_dim_record := l_source_record;

        l_insert_count := l_insert_count + 1;

        INSERT INTO user_tables  -- Replace with your actual schema

        (id, column_to_update)

        VALUES (l_source_record.id, l_source_record.column_to_update);

      END IF;

    END LOOP;

    CLOSE p_source_cursor;



    DBMS_OUTPUT.PUT_LINE('Updated records: ' || l_update_count);

    DBMS_OUTPUT.PUT_LINE('Inserted records: ' || l_insert_count);

  END;

END update_dim_pck;

-- aproch with cursor and multiple dimensions

CREATE OR REPLACE PACKAGE BODY update_dim_pck AS
    cursor p_source_cursor IS
    select * from p_source_table;
    l_source_record source_record;

  PROCEDURE update_dim_one (
    p_dim_name IN VARCHAR2
  ) IS
    l_dim_record dim_table%ROWTYPE;

    l_update_count INTEGER := 0;

    l_insert_count INTEGER := 0;
 
  BEGIN
    -- Loop through each record in the source cursor
    OPEN p_source_cursor;
    LOOP

      FETCH p_source_cursor INTO l_source_record;

      EXIT WHEN p_source_cursor%NOTFOUND;
-- aproch with source_data from cursor
    PROCEDURE update_dim_one (
    p_dim_name IN VARCHAR2
  ) IS

    l_dim_record dim_table%ROWTYPE;

    l_update_count INTEGER := 0;

    l_insert_count INTEGER := 0;

  BEGIN
    -- Loop through each record in the source cursor

    OPEN p_source_cursor;

    LOOP

      FETCH p_source_cursor INTO l_source_record;

      EXIT WHEN p_source_cursor%NOTFOUND;
-- aproch with source_data from cursor
  PROCEDURE update_dim_two (
    p_dim_name IN VARCHAR2
  ) IS
    l_dim_record dim_table%ROWTYPE;

    l_update_count INTEGER := 0;
    l_insert_count INTEGER := 0;

  BEGIN

    -- Loop through each record in the source cursor

    OPEN p_source_cursor;

    LOOP

      FETCH p_source_cursor INTO l_source_record;

      EXIT WHEN p_source_cursor%NOTFOUND;



      -- Check if record exists in dimension table

      SELECT * 

      INTO l_dim_record

      FROM user_tables  -- Replace with your actual schema

      WHERE table_name = p_dim_name

        AND id = l_source_record.id;



      -- Update existing record

      IF FOUND THEN

        IF l_dim_record.column_to_update != l_source_record.column_to_update THEN

          l_dim_record.column_to_update := l_source_record.column_to_update;

          l_update_count := l_update_count + 1;

          UPDATE user_tables  -- Replace with your actual schema

          SET column_to_update = l_dim_record.column_to_update

          WHERE table_name = p_dim_name

            AND id = l_source_cursor.id%ROWTYPE.id;

        END IF;

      -- Insert new record

      ELSE

        l_dim_record := l_source_record;

        l_insert_count := l_insert_count + 1;

        INSERT INTO user_tables  -- Replace with your actual schema

        (id, column_to_update)

        VALUES (l_source_record.id, l_source_record.column_to_update);

      END IF;

    END LOOP;

    CLOSE p_source_cursor;



    DBMS_OUTPUT.PUT_LINE('Updated records: ' || l_update_count);

    DBMS_OUTPUT.PUT_LINE('Inserted records: ' || l_insert_count);

  END;
END update_dim_pck;

BEGIN
  DBMS_SCHEDULER.CREATE_JOB (
    job_name        => 'UPDATE_DIM_ONE_JOB',
    job_type        => 'PLSQL_BLOCK',
    job_action      => 'BEGIN update_dim_pck.update_dim_one(''your_dim_name''); END;',
    start_date      => SYSTIMESTAMP,
    repeat_interval => 'FREQ=DAILY;BYHOUR=0;BYMINUTE=0;BYSECOND=0', -- This will run the job daily at midnight
    enabled         => TRUE,
    comments        => 'Job to run update_dim_pck.update_dim_one procedure daily at midnight'
  );
END;
/

CREATE OR REPLACE PACKAGE BODY update_dim_pck AS

  PROCEDURE update_dim (
    p_dim_name IN VARCHAR2,
    p_source_data IN update_dim_pck.source_data_t
    -- p_source_cursor IN SYS_REFCURSOR
  ) IS
    l_dim_record dim_table%ROWTYPE;
    l_update_count INTEGER := 0;
    l_insert_count INTEGER := 0;

  BEGIN
    -- Loop through source data
    FOR rec IN p_source_data LOOP
      -- Check if record exists in dimension table
      SELECT * 
      INTO l_dim_record
      FROM user_tables  -- Replace with your actual schema
      WHERE table_name = p_dim_name
        AND id = rec.id;

      -- Update existing record
      IF FOUND THEN
        IF l_dim_record.column_to_update != rec.column_to_update THEN
          l_dim_record.column_to_update := rec.column_to_update;
          l_update_count := l_update_count + 1;
        END IF;
      -- Insert new record
      ELSE
        l_dim_record := rec;
        l_insert_count := l_insert_count + 1;
      END IF;
    END LOOP;

    -- Bulk UPDATE and INSERT
    IF l_update_count > 0 THEN
      FOR rec IN p_source_data LOOP
        UPDATE user_tables  -- Replace with your actual schema
        SET column_to_update = rec.column_to_update
        WHERE table_name = p_dim_name
          AND id = rec.id;
      END LOOP;
    END IF;

    IF l_insert_count > 0 THEN
      FOR rec IN p_source_data LOOP
        INSERT INTO user_tables  -- Replace with your actual schema
        (id, column_to_update)
        VALUES (rec.id, rec.column_to_update);
      END LOOP;
    END IF;

    DBMS_OUTPUT.PUT_LINE('Updated records: ' || l_update_count);
    DBMS_OUTPUT.PUT_LINE('Inserted records: ' || l_insert_count);
  END;
END update_dim_pck;
