import glob
import polar as pl

list_csv = glob.glob('*.csv') # * means all if need specific format then *.csv
list_csv: list = [i for i in list_csv if 'clean' not in i]	

list_json = glob.glob('*.json') # * means all if need specific format then *.csv
list_json: list = [i for i in list_json if 'clean' not in i]

def extract_csv(files_to_process):
    df = pl.DataFrame()
    for file in files_to_process:
        temp_df = pl.read_csv(file)
        df = df.vstack(temp_df)
    return df

# function to extract all type of files, like csv, json, etc
def extract_all():
    # empty dataframe
    extract_data = pl.DataFrame(data=None, schema=["name", "heigth", "weigth"], orient="col")
    
    # extract csv
    for csv_file in glob.glob('*.csv'):
        temp_csv_df = extract_data.append(pl.read_csv(csv_file)) 
        df = df.vstack(temp_csv_df)
        print(df)