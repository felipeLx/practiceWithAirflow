import glob
import pandas as pd
from loggin_entries import log

list_csv = glob.glob('*.csv') # * means all if need specific format then *.csv
list_csv: list = [i for i in list_csv if 'clean' not in i]	

list_json = glob.glob('*.json') # * means all if need specific format then *.csv
list_json: list = [i for i in list_json if 'clean' not in i]

def extract_csv(files_to_process):
    df = pd.DataFrame(data=None, columns=['name', 'heigth', 'weigth'], index=None)
    for file in files_to_process:
        temp_df = pd.read_csv(file)
        df = df.vstack(temp_df)
    return df

# function to extract all type of files, like csv, json, etc
def extract_all():
    # empty dataframe
    extracted_data = pd.DataFrame(data=None, columns=['name', 'heigth', 'weigth'], index=None)
    
    # extract csv
    for csv_file in glob.glob('*.csv'):
        extracted_data = extracted_data.append(pd.read_csv(csv_file), ignore_index=True) 
        
    # extract json
    for json_file in glob.glob('*.json'):
        extracted_data = extracted_data.append(pd.read_json(json_file), ignore_index=True)
    
    return extracted_data

def transform_data(data):
    data['name'] = data['name'].str.upper()
    # convert heigth from inches to cm
    data['heigth'] = round(data.heigth * 2.54, 2)
    # convert weigth from pounds to kg
    data['weigth'] = round(data.weigth * 0.453592, 2)
    return data

def load_data(target_file, data_to_load):
    data_to_load.to_csv(target_file, index=False)
    
target_file = 'transformed_data.csv'

log("ETL job started")

log("Extract phase started")
extracted_data = extract_all()
log("Extract phase ended")


log("Transformed phase started")
transformed_data = transform_data(extracted_data)
log("Transformed phase ended")

log("Load phase started")
load_data(target_file, transformed_data)
log("Load phase ended")

log("ETL job ended")