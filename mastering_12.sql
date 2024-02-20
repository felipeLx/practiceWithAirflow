-- Partition
/*
breaking a table into multi-
ple pieces while preserving the look and feel of a single table. Each piece is called a
partition, and, although every partition must share the same columns, constraints,
indexes, and triggers, each partition can have its own unique storage parameters.

You can also take advantage of
Oracle’s segmented buffer cache to keep the most active partitions in the keep buffer
so they are always in memory, while the rest of the partitions can be targeted for the
recycle or default buffers. Additionally, individual partitions may be taken offline
without affecting the availability of the rest of the partitions, giving administrators a
great deal of flexibility.
Depending on the partitioning scheme employed, you must choose one or more col-
umns of a table to be the partition key. The values of the columns in the partition key
determine the partition that hosts a particular row. Oracle also uses the partition key
information in concert with your WHERE clauses to determine which partitions to
search during SELECT, UPDATE, and DELETE operations
*/

-- Range Partitioning
CREATE TABLE cust_order (
    order_nbr NUMBER(7) NOT NULL,
    cust_nbr NUMBER(5) NOT NULL,
    order_dt DATE NOT NULL,
    sales_emp_id NUMBER(5) NOT NULL,
    sale_price NUMBER(9,2),
    expected_ship_dt DATE,
    cancelled_dt DATE,
    ship_dt DATE,
    status VARCHAR2(20)
)
PARTITION BY RANGE (order_dt)
(PARTITION orders_2000
VALUES LESS THAN (TO_DATE('01-JAN-2001','DD-MON-YYYY'))
TABLESPACE ord1,
PARTITION orders_2001
VALUES LESS THAN (TO_DATE('01-JAN-2002','DD-MON-YYYY'))
TABLESPACE ord2,
PARTITION orders_2002
VALUES LESS THAN (TO_DATE('01-JAN-2003','DD-MON-YYYY'))
TABLESPACE ord3);

-- Partition by HASH
PARTITION BY HASH (part_nbr)
(PARTITION part1 TABLESPACE p1,
PARTITION part2 TABLESPACE p2,
PARTITION part3 TABLESPACE p3,
PARTITION part4 TABLESPACE p4);

-- Composite Range-Hash Partitioning
PARTITION BY RANGE (order_dt)
SUBPARTITION BY HASH (cust_nbr) SUBPARTITIONS 4
STORE IN (order_sub1, order_sub2, order_sub3, order_sub4)
(PARTITION orders_2000
VALUES LESS THAN (TO_DATE('01-JAN-2000','DD-MON-YYYY'))
(SUBPARTITION orders_2000_s1 TABLESPACE order_sub1,
SUBPARTITION orders_2000_s2 TABLESPACE order_sub2,
SUBPARTITION orders_2000_s3 TABLESPACE order_sub3,
SUBPARTITION orders_2000_s4 TABLESPACE order_sub4),
PARTITION orders_2001
VALUES LESS THAN (TO_DATE('01-JAN-2001','DD-MON-YYYY'))
(SUBPARTITION orders_2001_s1 TABLESPACE order_sub1,
SUBPARTITION orders_2001_s2 TABLESPACE order_sub2,
SUBPARTITION orders_2001_s3 TABLESPACE order_sub3,
SUBPARTITION orders_2001_s4 TABLESPACE order_sub4);
/* Interestingly, when composite partitioning is used, all of the data is physically stored
in the subpartitions, while the partitions, just like the table, become virtual. */

-- List Partitioning
/* warehouse table contain-
ing sales summary data by product, state, and month/year could be partitioned into
geographic regions */
CREATE TABLE sales_fact (
state_cd VARCHAR2(3) NOT NULL,
month_cd NUMBER(2) NOT NULL,
year_cd NUMBER(4) NOT NULL,
product_cd VARCHAR2(10) NOT NULL,
tot_sales NUMBER(9,2) NOT NULL
)
PARTITION BY LIST (state_cd)
(PARTITION sales_newengland VALUES ('CT','RI','MA','NH','ME','VT')
TABLESPACE s1,
PARTITION sales_northwest VALUES ('OR','WA','MT','ID','WY','AK')
TABLESPACE s2,
PARTITION sales_southwest VALUES ('NV','UT','AZ','NM','CO','HI')
TABLESPACE s3,
PARTITION sales_southeast VALUES ('FL','GA','AL','SC','NC','TN','WV')
TABLESPACE s4,
PARTITION sales_east VALUES ('PA','NY','NJ','MD','DE','VA','KY','OH')
TABLESPACE s5,
PARTITION sales_california VALUES ('CA')
TABLESPACE s6,
PARTITION sales_south VALUES ('TX','OK','LA','AR','MS')
TABLESPACE s7,
PARTITION sales_midwest VALUES ('ND','SD','NE','KS','MN','WI','IA',
'IL','IN','MI','MO')
TABLESPACE s8);
-- appropriate for low cardinality data in which the number of distinct values of a column is small relative to the number of rows

-- Composite List-Range Partitioning
/* range-list composite partitioning allows
you to partition your data by range, and then subpartition via a list.
excellent strategy for partitioning data in a sales warehouse so that you could parti-
tion your data both on sales periods (i.e., years, quarters, months) and on sales
regions (i.e., states, countries, districts).
*/
CREATE TABLE sales_fact (
    state_cd VARCHAR2(3) NOT NULL,
    month_cd NUMBER(2) NOT NULL,
    year_cd NUMBER(4) NOT NULL,
    product_cd VARCHAR2(10) NOT NULL,
    tot_sales NUMBER(9,2) NOT NULL
)
    PARTITION BY RANGE (year_cd)
        SUBPARTITION BY LIST (state_cd)
        (PARTITION sales_2000
        VALUES LESS THAN (2001)
        (SUBPARTITION sales_2000_newengland
        VALUES ('CT','RI','MA','NH','ME','VT') TABLESPACE s1,
        SUBPARTITION sales_2000_northwest
        VALUES ('OR','WA','MT','ID','WY','AK') TABLESPACE s2,
        SUBPARTITION sales_2000_southwest
        VALUES ('NV','UT','AZ','NM','CO','HI') TABLESPACE s3,
        SUBPARTITION sales_2000_southeast
        VALUES ('FL','GA','AL','SC','NC','TN','WV') TABLESPACE s4,
        SUBPARTITION sales_2000_east
        VALUES ('PA','NY','NJ','MD','DE','VA','KY','OH') TABLESPACE s5,
        SUBPARTITION sales_2000_california
        VALUES ('CA') TABLESPACE s6
        ),
        PARTITION sales_2001
        VALUES LESS THAN (2002)
        (SUBPARTITION sales_2001_newengland
        VALUES ('CT','RI','MA','NH','ME','VT') TABLESPACE s1,
        SUBPARTITION sales_2001_northwest
        VALUES ('OR','WA','MT','ID','WY','AK') TABLESPACE s2,
        SUBPARTITION sales_2001_southwest
        VALUES ('NV','UT','AZ','NM','CO','HI') TABLESPACE s3,
        SUBPARTITION sales_2001_southeast
        VALUES ('FL','GA','AL','SC','NC','TN','WV') TABLESPACE s4,
        SUBPARTITION sales_2001_east
        VALUES ('PA','NY','NJ','MD','DE','VA','KY','OH') TABLESPACE s5,
        SUBPARTITION sales_2001_california
        VALUES ('CA') TABLESPACE s6
    ));
    
CREATE TABLE sales_fact (
state_cd VARCHAR2(3) NOT NULL,
month_cd NUMBER(2) NOT NULL,
year_cd NUMBER(4) NOT NULL,
product_cd VARCHAR2(10) NOT NULL,
tot_sales NUMBER(9,2) NOT NULL
)
PARTITION BY RANGE (year_cd)
SUBPARTITION BY LIST (state_cd)
SUBPARTITION TEMPLATE (
SUBPARTITION newengland
VALUES ('CT','RI','MA','NH','ME','VT') TABLESPACE s1,
SUBPARTITION northwest
VALUES ('OR','WA','MT','ID','WY','AK') TABLESPACE s2,
SUBPARTITION southwest
VALUES ('NV','UT','AZ','NM','CO','HI') TABLESPACE s3,
SUBPARTITION southeast
VALUES ('FL','GA','AL','SC','NC','TN','WV') TABLESPACE s4,
SUBPARTITION east
VALUES ('PA','NY','NJ','MD','DE','VA','KY','OH') TABLESPACE s5,
SUBPARTITION california
VALUES ('CA') TABLESPACE s6,
SUBPARTITION south
VALUES ('TX','OK','LA','AR','MS') TABLESPACE s7,
SUBPARTITION midwest
VALUES ('ND','SD','NE','KS','MN','WI','IA', 'IL','IN','MI','MO')
TABLESPACE s8
)
(PARTITION sales_2000
VALUES LESS THAN (2001),
PARTITION sales_2001
VALUES LESS THAN (2002),
PARTITION sales_2002
VALUES LESS THAN (2003)
);