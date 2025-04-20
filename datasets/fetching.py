import requests
import pandas as pd
import time
from urllib.parse import quote




# Load the dataset
data = pd.read_csv('datasets/dataset.csv')

# Function to get an access token using OAuth2
CLIENT_ID = "5GUMVcQOLobJFKgU2X7tJKOpOprQxtN4"
CLIENT_SECRET = "vTvCJKf7oKolOkgdiRfymnVOavGovW80"
REDIRECT_URI = "urn:ietf:wg:oauth:2.0:oob"  # Replace with your redirect URI
AUTHORIZATION_CODE = "mroEd3Hr_ig4GD3wCyZR0bGFnVA2txS6"  # Replace with the actual authorization code

# Function to get an access token using Authorization Code Flow
def get_access_token(client_id, client_secret, authorization_code, redirect_uri):
    url = "https://musicbrainz.org/oauth2/token"
    data = {
        'grant_type': 'authorization_code',
        'code': authorization_code,
        'redirect_uri': redirect_uri,
        'client_id': client_id,
        'client_secret': client_secret
    }
    response = requests.post(url, data=data)
    if response.status_code == 200:
        print("Access token retrieved successfully.")
        return response.json().get('access_token')
    else:
        print(f"Failed to get access token: {response.status_code}, {response.text}")
        return None

# Function to fetch data from MusicBrainz
def fetch_musicbrainz_data(title, artist, access_token):
    try:
        encoded_title = quote(title)
        encoded_artist = quote(artist)
        url = f"https://musicbrainz.org/ws/2/recording/?query=recording:\"{encoded_title}\" AND artist:\"{encoded_artist}\"&fmt=json"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'User-Agent': 'kafkaapp (fsaad1929@gmail.com)'
        }
        response = requests.get(url, headers=headers)
        
        # Debugging logs
        print(f"Request URL: {response.url}")
        print(f"Response Status Code: {response.status_code}")
        print(f"Response Headers: {response.headers}")
        print(f"Response Text: {response.text}")
        
        if response.status_code == 200:
            results = response.json()
            if results['recordings']:
                recording = results['recordings'][0]
                return {
                    'year': recording.get('first-release-date', 'Unknown'),
                    'category': []  # Tags are not present in the response
                }
            else:
                print(f"No results found for {title} by {artist}")
                return None
        elif response.status_code == 403:
            print(f"MusicBrainz API error for {title} by {artist}: HTTP 403 (Rate limit or authentication issue)")
            return None
        else:
            print(f"MusicBrainz API error for {title} by {artist}: HTTP {response.status_code}")
            return None
    except Exception as e:
        print(f"Error fetching data for {title} by {artist}: {e}")
        return None
# Get the access token
access_token = get_access_token(CLIENT_ID, CLIENT_SECRET, AUTHORIZATION_CODE, REDIRECT_URI)
if not access_token:
    print("Failed to retrieve access token. Exiting...")
    exit()

# Iterate over all rows to fetch year and category
for index, row in data.iterrows():
    if pd.notnull(row['title']) and pd.notnull(row['artist_name']):
        song_data = fetch_musicbrainz_data(row['title'], row['artist_name'], access_token)
        if song_data:
            # Update only the year and category fields
            data.at[index, 'year'] = song_data['year']
            data.at[index, 'category'] = ', '.join(song_data['category']) if song_data['category'] else 'Unknown'
        else:
            data.at[index, 'category'] = 'Unknown'
        time.sleep(0.2)  # Add delay to avoid rate limiting

# Save the updated dataset
data.to_csv('datasets/updated_dataset.csv', index=False)
print("Updated dataset saved with fetched year and categories.")

# Test the API with a single query
test_title = "Merry-Go-Round"
test_artist = "Bob Hope"
song_data = fetch_musicbrainz_data(test_title, test_artist, access_token)
print(song_data)