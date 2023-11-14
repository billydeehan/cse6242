import googlemaps
import json
from outscraper import ApiClient
import os.path
gmaps_key = 'AIzaSyB5T9kvIe2hQZ49w7cpC2B638pdnKpaDTY'
outscrape_key = 'NGQxMTM4NzBkZmE0NGU0MThhZmRhZDAxMmU0MGIxN2R8NjQ5YWI1ZWM2MQ'
# Replace 'YOUR_API_KEY' with your actual Google API key
gmaps = googlemaps.Client(key=gmaps_key)
client = ApiClient(api_key=outscrape_key)

folder = './data/jsons/'
# Define a function to fetch reviews for a place
def fetch_reviews(place_id):
    try:
        place = gmaps.place(place_id=place_id, fields=['name', 'reviews'],)
        if 'reviews' in place['result']:
            return place['result']['reviews']
        else:
            return []
    except Exception as e:
        print(f"Error fetching reviews for place {place_id}: {str(e)}")
        return []

def fetch_reviews2(place_id, limit):
    results = client.google_maps_reviews_v2(query=place_id, reviews_limit=limit, fields=['name', 'reviews'])
    return results

# Perform a search for hospitals in the U.S.
search_result = gmaps.places_nearby(
    location=(37.0902, -95.7129),  # Center of the United States
    radius=5000000,               # Adjust the radius as needed
    keyword='hospital',
    type='hospital'
)

# Process each hospital to fetch reviews
all_reviews = {
    'hospitals': []
}
review_count = 0
for hospital in search_result.get('results', []):
    place_id = hospital['place_id']
    # reviews = fetch_reviews(place_id)
    output_file_path = folder + place_id + '.json'
    if not os.path.isfile(output_file_path):
        reviews = fetch_reviews2(place_id, 20)
        review_count = review_count + len(reviews)
        location = hospital['geometry']['location']
        new_hospital = {
            'hospital_name': hospital['name'],
            'place_id':place_id,
            'reviews':reviews,
            'location':location
        }
        
        # all_reviews['hospitals'].append(new_hospital)
        with open(output_file_path,'w') as json_file:
            json.dump(new_hospital,json_file,indent=4)
        if review_count >= 100:
            break

# output_file_path = './data/all_reviews.json'

# with open(output_file_path,'w') as json_file:
#     json.dump(new_hospital,json_file,indent=4)
# Print the most recent 100 reviews
# for i, review in enumerate(all_reviews[:1000]):
#     print(f"Review {i + 1}:")
#     print(f"Rating: {review['rating']}")
#     print(f"Text: {review['text']}\n")

# You can now process and analyze the reviews as needed
