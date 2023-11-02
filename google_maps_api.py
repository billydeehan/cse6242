import googlemaps
import json

# Replace 'YOUR_API_KEY' with your actual Google API key
gmaps = googlemaps.Client(key='AIzaSyB5T9kvIe2hQZ49w7cpC2B638pdnKpaDTY')

# Define a function to fetch reviews for a place
def fetch_reviews(place_id):
    try:
        place = gmaps.place(place_id=place_id, fields=['name', 'reviews'])
        if 'reviews' in place['result']:
            return place['result']['reviews']
        else:
            return []
    except Exception as e:
        print(f"Error fetching reviews for place {place_id}: {str(e)}")
        return []

# Perform a search for hospitals in the U.S.
search_result = gmaps.places_nearby(
    location=(37.0902, -95.7129),  # Center of the United States
    radius=500000,               # Adjust the radius as needed
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
    reviews = fetch_reviews(place_id)
    review_count = review_count + len(reviews)
    location = hospital['geometry']['location']
    new_hospital = {
        'hospital_name': hospital['name'],
        'place_id':place_id,
        'reviews':reviews,
        'location':location
    }
    all_reviews['hospitals'].append(new_hospital)
    if review_count >= 1000:
        break

output_file_path = './data/all_reviews.json'

with open(output_file_path,'w') as json_file:
    json.dump(all_reviews,json_file,indent=4)
# Print the most recent 100 reviews
# for i, review in enumerate(all_reviews[:1000]):
#     print(f"Review {i + 1}:")
#     print(f"Rating: {review['rating']}")
#     print(f"Text: {review['text']}\n")

# You can now process and analyze the reviews as needed
