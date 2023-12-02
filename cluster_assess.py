import numpy as np
import openai
import json
from collections import defaultdict
from dotenv import load_dotenv
import os
from azure.cosmos import CosmosClient
import random
from matplotlib import pyplot as plt

# from langchain import LLMChain
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

# https://medium.com/@kbdhunga/text-clustering-and-labeling-utilizing-openai-api-677271e0763c
# https://pypi.org/project/keybert/

load_dotenv()
print('key', os.getenv('OPENAI_API_KEY'))
print('COSMO key', os.getenv('COSMO_API_KEY'))
openai.api_key = os.getenv('OPENAI_API_KEY')
cosmo_key = os.getenv('COSMO_API_KEY')
input_datapath = 'data/all_reviews_with_embeddings.json'


def getContainer():
    cosmos_url = 'https://reviews-cosmosdb.documents.azure.com:443/'
    cosmos_key = cosmo_key
    db_name = 'reviews-db'
    container_name = 'reviews-container'

    client = CosmosClient(cosmos_url,credential=cosmos_key)
    database = client.create_database_if_not_exists(id=db_name)
    container = database.create_container_if_not_exists(
        id=container_name,
        partition_key='/place_id',
        offer_throughput=1000
    )
    return container

def queryReviews(query='SELECT * FROM c OFFSET 0 LIMIT 100'):
    container = getContainer()
    results = list(container.query_items(
        query,
        enable_cross_partition_query=True
    ))
    return results


def generate_bins(k='9'):
    cluster_reviews = defaultdict(list)
    offset = 0
    container = getContainer()

    reviews = queryReviews(query='SELECT c.id, c.cluster, c.rating FROM c WHERE IS_DEFINED(c.cluster)')

    for review in reviews:
        try:
            review_rating = review['rating']
            cluster_id = review['cluster'][k]['cluster']
            cluster_reviews[cluster_id].append(review_rating)
        except:
            continue
    return cluster_reviews

# print(queryReviews(query='SELECT * FROM c WHERE IS_DEFINED(c.cluster) OFFSET 0 LIMIT 100'))

clusters = generate_bins('5')
fig, ax = plt.subplots(5, 1)
for id, cluster in clusters.items():
    arr = np.array(cluster)
    print(id, len(arr), arr.mean(), arr.std())
    ax[id].set_title('clusterid:{0}, mean:{1:.3f}, std:{2:.3f}'.format(id, arr.mean(), arr.std()))
    ax[id].hist(arr, bins=5)
plt.tight_layout()
plt.show()
