import pandas as pd

data_updated = pd.read_csv('datasets\\updated_dataset.csv')
# Convert the 'year' column to integers
def transform_year(year):
    try:
        # If the year is in the format 'xxxx-xx-xx', extract the first 4 characters
        if isinstance(year, str) and '-' in year:
            return int(year[:4])
        # If the year is already an integer-like string, convert it to int
        return int(year)
    except ValueError:
        # Handle invalid values by returning a default value (e.g., 0 or None)
        return None
   
print("\nTransforming 'year' column to integers...")
data_updated['year'] = data_updated['year'].apply(transform_year)
data_updated['year'] = data_updated['year'].fillna(0).astype(int)
if 'category' in data_updated.columns:
    data_updated = data_updated.drop(columns=['category'])
    print("'category' column dropped.")

# Drop rows where 'title', 'song_id', or 'artist_name' are missing or null
print("\nDropping rows with missing 'title', 'song_id', or 'artist_name'...")
data_updated = data_updated.dropna(subset=['title', 'song_id', 'artist_name'])

# Add 'is_valid' column
print("\nAdding 'is_valid' column...")
data_updated['is_valid'] = (
    (data_updated['year'].notnull()) & # Year is not null
    (data_updated['year'] != 0) &  # Year is not zero
    (data_updated['tempo'].notnull()) &  # Tempo is not null
    (data_updated['tempo'] != 0 ) &  # Tempo is not zero
    (data_updated['key'].notnull()) &  # Key is not null
    (data_updated['duration'].notnull()) &  # Duration is not null
    (data_updated['duration'] != 0)  # Duration is not zero
)



# Display the updated dataset info
print("\nUpdated Dataset Info:")
print(data_updated.info())

# Save the cleaned dataset
data_updated.to_csv('datasets/cleaned_dataset.csv', index=False)
print("Cleaned dataset saved as 'cleaned_dataset.csv'.")
