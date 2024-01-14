from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
import sqlite3
from datetime import datetime

URL = 'https://web.archive.org/web/20230902185326/https://en.wikipedia.org/wiki/List_of_countries_by_GDP_%28nominal%29'
table_attribs = ["Country", "GDP_USD_millions"]
# target
csv_path = "./Countries_by_GDP.csv"
database = "World_Economies.db" # attr: Country / GDP_USD_billion
log_file = "etl_project_log.txt"


def extract(url, table_attribs):
    ''' This function extracts the required
    information from the website and saves it to a dataframe. The
    function returns the dataframe for further processing. '''
    page = requests.get(url).text
    data = BeautifulSoup(page, 'html.parser')
    df = pd.DataFrame(columns=table_attribs)
    tables = data.find_all('tbody')
    rows = tables[2].find_all('tr')
    for row in rows:
        col = row.find_all('td')
        if len(col) != 0:
            if col[0].find('a') is not None and '-' not in col[2]:
                data_dict = {"Country": col[0].a.contents[0],
                            "GDP_USD_millions": col[2].contents[0]}
                df1 = pd.DataFrame(data_dict, index=[0])
                df = pd.concat([df, df1], ignore_index=True)
    return df

def transform(df):
    ''' This function converts the GDP information from Currency
 a   format to float value, transforms the information of GDP from
    USD (Millions) to USD (Billions) rounding to 2 decimal places.
    The function returns the transformed dataframe.'''
    GDP_list = df["GDP_USD_millions"].tolist()
    GDP_list = [float("".join(x.split(','))) for x in GDP_list]
    GDP_list = [np.round(x/1000,2) for x in GDP_list]
    df["GDP_USD_millions"] = GDP_list
    df=df.rename(columns = {"GDP_USD_millions":"GDP_USD_billions"})
    return df

def load_to_csv(df, csv_path):
    ''' This function saves the final dataframe as a `CSV` file 
    in the provided path. Function returns nothing.'''
    df.to_csv(csv_path)

def load_to_db(df, sql_connection, table_name):
    ''' This function saves the final dataframe as a database table
    with the provided name. Function returns nothing.'''
    df.to_sql(table_name, sql_connection, if_exists='replace', index=False)

def run_query(query_statement, sql_connection):
    ''' This function runs the stated query on the database table and
    prints the output on the terminal. Function returns nothing. '''
    print(query_statement)
    query_output = pd.read_sql(query_statement, sql_connection)
    print(query_output)

def log(message):
    """ Register on logfile """
    timestamp_format = '%Y-%h-%d-%H:%M:%S'
    now = datetime.now()
    timestamp = now.strftime(timestamp_format)
    with open(log_file, 'a') as f:
        f.write(timestamp + ',' + message + '\n')

log('Preliminaries complete. Initiating ETL process')

df = extract(URL, table_attribs)

log('Data extraction complete. Initiating Transformation process')

df = transform(df)

log('Data transformation complete. Initiating loading process')

load_to_csv(df, csv_path)

log('Data saved to CSV file')

sql_connection = sqlite3.connect('World_Economies.db')

log('SQL Connection initiated.')

load_to_db(df, sql_connection, database)

log('Data loaded to Database as table. Running the query')

query_statement = f"SELECT * from {database} WHERE GDP_USD_billions >= 100"
run_query(query_statement, sql_connection)

log('Process Complete.')

sql_connection.close()
