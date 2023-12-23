# PEP008
"""
Standard library imports.
Related third party imports.
Local application/library specific imports.
You should put a blank line between each group of imports.
"""
import pandas as pd
import requests
import sqlite3

# table column
"""
ID	Employee ID
FNAME	First Name
LNAME	Last Name
CITY	City of residence
CCODE	Country code (2 letters)
"""

# sql connection
conn = sqlite3.connect('STAFF.db')

# misc
table_name = 'INSTRUCTOR'
attribute_list = ['ID', 'FNAME', 'LNAME', 'CITY', 'CCODE']

# read csv file
file_path = '/home/project/INSTRUCTOR.csv'
df = pd.read_csv(file_path, names = attribute_list)

df_sql = df.to_sql(table_name, conn, if_exists = 'replace')
print('Table is ready')

query_statement = f"SELECT * FROM {table_name}"
query_output = pd.read_sql(query_statement, conn)
print('query: ', query_statement)
print('output: ', query_output)

query_statement_ocol = f"SELECT FNAME FROM {table_name}"
query_output_ocol = pd.read_sql(query_statement_ocol, conn)
print(query_statement_ocol)
print(query_output_ocol)

query_statement_count = f"SELECT COUNT(*) FROM {table_name}"
query_output_count = pd.read_sql(query_statement_count, conn)
print(query_statement_count)
print(query_output_count)

data_dict = {'ID' : [100],
            'FNAME' : ['John'],
            'LNAME' : ['Doe'],
            'CITY' : ['Paris'],
            'CCODE' : ['FR']}
data_append = pd.DataFrame(data_dict)
data_append.to_sql(table_name, conn, if_exists='append', index=False)
print('Data appended successfully')

conn.close()