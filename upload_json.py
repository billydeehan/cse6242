import json
import os
import openai
from azure.cosmos import CosmosClient
cosmos_url = 'https://reviews-cosmosdb.documents.azure.com:443/'
cosmos_key = 'MYKzQ3mpIwwOg9ZenEG4MFslPM0a181ImCWjmUiJ0zU51LKsUkUN3v04Rf0ydfJQsbWJS1oDZ1vIACDbcfgTFg=='
db_name = 'reviews-db'
container_name = 'reviews-container'

client = CosmosClient(cosmos_url,credential=cosmos_key)
database = client.create_database_if_not_exists(id=db_name)
container = database.create_container_if_not_exists(
    id=container_name,
    partition_key='/place_id',
    offer_throughput=1000
)

def uploadReviews():
    input_folder = './data/embeddings/'
    upload_count = 0
    for filename in os.listdir(input_folder):
        filepath = os.path.join(input_folder, filename)
        with open(filepath,'r') as json_file:
            hospital = json.load(json_file)
        if 'reviews_fetched' not in hospital:
            continue
        hospital_name = hospital['hospital_name']
        place_id = hospital['place_id']
        location = hospital['location']
        review_fetch_method = hospital['review_fetch_method']
        review_fetch_count = hospital['reviews_fetched']
        for review in hospital['reviews']:
            time = str(review['time'])
            id = place_id + '|' + time
            rating = review['rating']
            text = review['text']
            if 'embedding' not in review:
                continue
            embedding = review['embedding']
            new_review = {
                'id': id,
                'place_id': place_id,
                'hospital_name': hospital_name,
                'location': location,
                'review_fetch_method': review_fetch_method,
                'reviews_fetched': review_fetch_method,
                'time': time,
                'rating': rating,
                'text': text,
                'embedding': embedding
            }
            container.upsert_item(body=new_review)
            upload_count += 1
            if upload_count % 10 == 0:
                print(upload_count)
    print(upload_count)

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

uploadReviews()