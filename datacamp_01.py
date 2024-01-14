from module_name import FileSystemDataLink

# Dictionary
catalog = {
    'diaper_reviews': FileSystemDataLink('s3://datacamp/s3_data/diaper_reviews.csv'),
}

catalog['diaper_reviews'].read()
# DataFrame[brand: string, model: string, absorption_rate: tinyint, comfort: tinyint]

print(type(catalog['diaper_reviews']))
# <class '__main__.FileSystemDataLink'>

print(type(catalog['diaper_reviews'].read()))
# <class 'pyspark.sql.dataframe.DataFrame'>

