import openai
from sklearn.cluster import KMeans
import json


openai.api_key = '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'
input_datapath = 'data/all_reviews_with_embeddings.json'
sample_size = 5
clusters = 5
review_n = 0
with open(input_datapath,'r') as json_file:
    data = json.load(json_file)

filtered_data = {'hospitals': []}

for hospital in data['hospitals']:
    filtered_reviews = [review for review in hospital['reviews'] if 'embedding' in review]
    if filtered_reviews:
        hospital['reviews'] = filtered_reviews
        filtered_data['hospitals'].append(hospital)

embeddings = []
review_texts = []

data = filtered_data

for hospital in data['hospitals']:
    for review in hospital['reviews']:
        embedding = review['embedding']
        embeddings.append(embedding)
        review_texts.append(review['text'])

kmeans = KMeans(n_clusters=clusters, n_init='auto')
kmeans.fit(embeddings)
labels = kmeans.fit_predict(embeddings)

# Create a dictionary to store review texts for each label
label_to_reviews = {i: [] for i in range(clusters)}

# Assign labels to the reviews and store them in the dictionary
for i, label in enumerate(labels):
    review_text = review_texts[i]
    label_to_reviews[label].append(review_text)

# Add the K-means label as a property to each review
for hospital in data['hospitals']:
    for review in hospital['reviews']:
        embedding = review['embedding']
        label = kmeans.predict([embedding])[0]
        review['kmeans_label'] = label

# Print the labels and the review texts associated with each label
for label, label_reviews in label_to_reviews.items():
    print(f"Label {label}:")
    for review_text in label_reviews:
        print(review_text)
