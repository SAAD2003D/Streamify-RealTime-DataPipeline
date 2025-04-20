import pandas as pd
import os
print("Current Working Directory:", os.getcwd())
data = pd.read_csv('D:\\myprojects\\Technocolabs\\streamify\\Streamify-RealTime-DataPipeline\\datasets\\cleaned_dataset.csv')
# Display basic information about the dataset
print("Dataset Info:")
print(data.info())

# Analyze and clean each column

# 1. song_id
# checking for duplicate song_id values
print("\nChecking for duplicate song_id values...")
duplicates = data['song_id'].duplicated().sum()
print(f"Duplicate song_id values: {duplicates}")
if duplicates > 0:
    data = data.drop_duplicates(subset='song_id')
    

# check if there are any missing values in the song_id column
print("\nChecking for missing values in song_id...")
missing_song_id = data['song_id'].isnull().sum()
zero_mask = data['song_id'] == 0
zero_count = zero_mask.sum()
print(f"Missing song_id values: {missing_song_id}")
print(f"Zero song_id values: {zero_count}")


if missing_song_id > 0 or zero_count > 0:
    data = data.dropna(subset=['song_id'])
    data = data[~zero_mask]
    print("Missing or zero song_id values have been removed.")
else:
    print("No missing or zero song_id values found.")
    
# 2. song_name
# check for missing and empty values in the title column
print("\nChecking for missing values in title...")
null_title_count = data['title'].isnull().sum()
empty_title_count =(data['title']=='').sum() + (data['title'].str.isspace()).sum()
print(f"Missing title values: {null_title_count}")
print(f"Empty title values: {empty_title_count}")



# 3.artist_name 
# check for missing and empty values in the artist_name column 
print("\nchecking for missing and empty values in artist_name...")
null_artist_name_count =data['artist_name'].isnull().sum()
empty_artist_name_count = (data['artist_name']=='').sum() +(data['artist_name'].str.isspace()).sum()
print(f'missing artist_name values: {null_artist_name_count}')
print(f'empty artist_name values: {empty_artist_name_count}')

# 4. duration 
# checking for missing and zero values in duration column
print("\n checking for missing values in duration...")
missing_duration_count = data['duration'].isnull().sum()
zero_duration_count = (data['duration'] == 0).sum()
print(f'missing duration values : {missing_duration_count}')
print(f'zero duration :  {zero_duration_count}')




# 5.year
# check for missing and zero values in the year column
print("\nChecking for missing and zero values in year...")
missing_year_count = data['year'].isnull().sum()
zero_count = (data['year']==0).sum()
unknown_year_count = (data['year']=='Unknown').sum()
print(f'missing year values : {missing_year_count}')
print(f'zeros in year values :{zero_count}')
print(f'unknown year values : {unknown_year_count}')


# 6. tempo
# checking for missing and zero values in temp column
print("\n checking for missing values in tempo...")
missing_tempo_count = data['tempo'].isnull().sum()
zero_tempo_count = (data['tempo'] == 0).sum()
print(f'missing tempo values : {missing_tempo_count}')
print(f'zero tempo :  {zero_tempo_count}')  


# 7. key
# checking for missing and zero values in key column
print("\n checking for missing values in key...")
missing_key_count = data['key'].isnull().sum()
zero_key_count = (data['key'] == 0).sum()
print(f'missing key values : {missing_key_count}')
print(f'zero key :  {zero_key_count}')  



# final cleaning pn the updated dataset

