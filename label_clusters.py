import numpy as np
import openai
import json
from collections import defaultdict
from dotenv import load_dotenv
import os
from azure.cosmos import CosmosClient
import random

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
openai.api_key = os.getenv('OPENAI_API_KEY')
input_datapath = 'data/all_reviews_with_embeddings.json'


def getContainer():
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
    return container

def queryReviews(query='SELECT * FROM c OFFSET 0 LIMIT 10000'):
    container = getContainer()
    results = list(container.query_items(
        query,
        enable_cross_partition_query=True
    ))
    return results

def call_openai_api(messages):
    return openai.ChatCompletion.create(
        model='gpt-3.5-turbo-16k',
        messages=messages,
        max_tokens=4096,
        temperature=1
    )

def summarize_text(transcript):
    system_prompt = "I would like for you to assume the role of a Life Coach"
    user_prompt = f"""Generate ten words summary of the text below.
    Text: {transcript}
    """

    messages = [
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': user_prompt}
    ]

    response = call_openai_api(messages)
    summary = response['choices'][0]['message']['content']
    return summary

def get_prompt():
    sys_template1 = 'You are a healthcare expert and have in-depth knowledge of hospital administration. You are helping me write a concise topic from many reviews.'

    system_template = "You are a market analyst and know all reviews from Amazon. You're helping me write a concise topic from many reviews."
    human_template = "Using the following reviews, write a topic title that summarizes them.\n\nREVIEWS:{reviews}\n\nTOPIC TITLE:"

    return ChatPromptTemplate(
        messages=[
            SystemMessagePromptTemplate.from_template(sys_template1),
            HumanMessagePromptTemplate.from_template(human_template),
        ],
        input_variables=["reviews"],
    )

def generate_bins(k='9'):
    cluster_reviews = defaultdict(list)
    offset = 0
    container = getContainer()

    reviews = queryReviews(query='SELECT c.id, c.cluster, c.text FROM c WHERE IS_DEFINED(c.cluster)')
        # if len(reviews) <= 0 or offset > 10000:
        #     break
        # offset += 100
    for review in reviews:
        try:
            review_txt = review['text']
            cluster_id = review['cluster'][k]['cluster']
            cluster_reviews[cluster_id].append(review_txt)
        except:
            continue
    for key in cluster_reviews.keys():
        cluster_reviews[key] = random.sample(cluster_reviews[key], 1000)
    return cluster_reviews



# with open(input_datapath,'r') as json_file:
#     data = json.load(json_file)
#
# cluster_reviews = defaultdict(list)
#
# for hospital in data['hospitals']:
#     for review in hospital['reviews']:
#         review_txt = review['text']
#         cluster_id = review.get('cluster_id', 0)
#         cluster_reviews[cluster_id].append(review_txt)

cluster_reviews = generate_bins('5')

for cluster_id, reviews in cluster_reviews.items():
    chain = LLMChain(
        llm=ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo-16k"), prompt=get_prompt(), verbose=False
    )
    review_str = '\n'.join(reviews[:10])
    result = chain.run({"reviews": review_str})
    print(cluster_id, result)
