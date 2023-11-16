import json
import os
import openai
from azure.cosmos import CosmosClient
cosmos_url = 'https://reviews-cosmosdb.documents.azure.com:443/'
cosmos_key = ''
db_name = 'reviews-db'
container_name = 'reviews-container'

client = CosmosClient(cosmos_url,credential=cosmos_key)
database = client.create_database_if_not_exists(id=db_name)
container = database.create_container_if_not_exists(
    id=container_name,
    partition_key='/place_id',
    offer_throughput=1000
)

def queryReviews(query='SELECT * FROM c OFFSET 0 LIMIT 10000'):
    results = list(container.query_items(
        query,
        enable_cross_partition_query=True
    ))
    return results

def addCluster(reviews, cluster_label = 1):
    for review in reviews:
        review['cluster'] = cluster_label
        container.upsert_item(body=review)

reviews = queryReviews(query='SELECT * FROM c')
addCluster(reviews)
print(queryReviews(query='SELECT * FROM c WHERE IS_DEFINED(c.cluster) OFFSET 0 LIMIT 100'))