import googlemaps
import json
from outscraper import ApiClient
import os.path
import pandas as pd
import time
gmaps_key = 'AIzaSyAWzpEoY5iL6RL5Rhg7ANATlT-lUHfhH90'#'AIzaSyB5T9kvIe2hQZ49w7cpC2B638pdnKpaDTY'
outscrape_key = 'NGQxMTM4NzBkZmE0NGU0MThhZmRhZDAxMmU0MGIxN2R8NjQ5YWI1ZWM2MQ'
# Replace 'YOUR_API_KEY' with your actual Google API key
gmaps = googlemaps.Client(key=gmaps_key)
client = ApiClient(api_key=outscrape_key)

json_folder = './data/jsons/'
zip_file = './data/zips/uszips.csv'
# Define a function to fetch reviews for a place
def fetch_reviews(place_id):
    time.sleep(.5)
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
    try:
        results = client.google_maps_reviews_v2(query=place_id, reviews_limit=limit,fields=['name', 'reviews','reviews_data'])
        reviews = results[0]['reviews_data']
        return reviews
    except Exception as e:
        print(f"Error fetching reviews for place {place_id}: {str(e)}")
        return []

# Perform a search for hospitals in the U.S.

def generateHospitals():
    dtypes = {
    'zip': str,  # Read 'zip' column as string
    # Add other columns and their respective data types if needed
    }

    zips_df = pd.read_csv(zip_file, dtype=dtypes)
    zips_df = zips_df.reset_index()
    for index, zip_row in zips_df.iterrows():
        zip = str(zip_row['zip'])
        zip_history_file = './data/zips/hospitals/' + zip + '.json'
        if os.path.isfile(zip_history_file):
            continue
        lat = zip_row['lat']
        long = zip_row['lng']

        search_result = gmaps.places_nearby(
            location=(lat, long),  # Center of the United States
            radius=50000,               # Adjust the radius as needed
            keyword='hospital',
            type='hospital'
        )
        results = search_result.get('results', [])
        with open(zip_history_file,'w') as json_file:
            json.dump(results,json_file,indent=4)
        print('index: ', index)
        print('zip: ',zip)

def generateReviews(hospital):
# for hospital in search_result.get('results', []):
    place_id = hospital['place_id']
    # reviews = fetch_reviews(place_id)
    output_file_path = json_folder + place_id + '.json'
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

def getHospitalsFromZips():
    input_folder = './data/zips/hospitals/'
    output_folder = './data/hospitals/'
    zip_count = 0
    hospital_count = 0
    hospital_file_count = 0
    for filename in os.listdir(input_folder):
        zip_count += 1
        filepath = os.path.join(input_folder, filename)
        with open(filepath,'r') as json_file:
            data = json.load(json_file)
        for hospital in data:
            hospital_count += 1
            place_id = hospital['place_id']
            # print(place_id)
            output_file_path = output_folder + place_id + '.json'
            if not os.path.isfile(output_file_path):
                hospital_file_count += 1
                with open(output_file_path,'w') as json_file:
                    json.dump(hospital,json_file,indent=4)

            print("zip count: ", zip_count, "| hospital count: ", hospital_count, "| hospital file count: ", hospital_file_count)
        # if hospital_file_count > 100:
        #     break
def getReviewsFromHospitals():
    input_folder = './data/hospitals/'
    output_folder = './data/reviews/'
    hospital_count = 0
    review_count = 0
    for filename in os.listdir(input_folder):
        review_method = ''
        filepath = os.path.join(input_folder, filename)
        output_file_path = output_folder + filename
        hospital_count += 1
        if os.path.isfile(output_file_path):
            print('skipped: ', hospital_count, '| file: ', output_file_path)
            continue   
        with open(filepath,'r') as json_file:
            hospital = json.load(json_file)
        review_count = hospital['user_ratings_total']
        location = hospital['geometry']['location']
        place_id = hospital['place_id']
        if review_count == 0:
            continue
        elif review_count >= 1:
            review_method = 'google_maps'
            reviews = fetch_reviews(place_id=place_id)
        elif review_count > 10:
            review_method = 'outscrape'
            limit = round(min(review_count/2, 40),0)
            reviews = fetch_reviews2(place_id=place_id, limit=limit)
        new_hospital = {
            'hospital_name': hospital['name'],
            'place_id':place_id,
            'review_count':review_count,
            'review_fetch_method': review_method,
            'reviews_fetched': len(reviews),
            'reviews':reviews,
            'location':location
        }
        with open(output_file_path,'w') as json_file:
            json.dump(new_hospital,json_file,indent=4)
        review_count += len(reviews)
        
        print('hospital_count: ', hospital_count, ' | total reviews: ',review_count,' | fetch method: ', review_method, ' | number reviews fetched: ', len(reviews), ' | place_id: ', place_id)

def getReviewCount():
    input_folder = './data/reviews/'
    hospital_count = 0
    review_count = 0
    for filename in os.listdir(input_folder):
        filepath = os.path.join(input_folder, filename)
        with open(filepath,'r') as json_file:
            hospital = json.load(json_file)
        hospital_count += 1
        if 'reviews_fetched' in hospital:
            review_count += hospital['reviews_fetched']
    print("hospital count: ", hospital_count, "review count: ", review_count)
# generateHospitals()

getReviewCount()

# getHospitalsFromZips()




# output_file_path = './data/all_reviews.json'

# with open(output_file_path,'w') as json_file:
#     json.dump(new_hospital,json_file,indent=4)
# Print the most recent 100 reviews
# for i, review in enumerate(all_reviews[:1000]):
#     print(f"Review {i + 1}:")
#     print(f"Rating: {review['rating']}")
#     print(f"Text: {review['text']}\n")

# You can now process and analyze the reviews as needed
