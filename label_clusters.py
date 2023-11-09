import numpy as np
import openai
import json
from collections import defaultdict

from langchain import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

# https://medium.com/@kbdhunga/text-clustering-and-labeling-utilizing-openai-api-677271e0763c
# https://pypi.org/project/keybert/

openai.api_key = ''
input_datapath = 'data/all_reviews_with_embeddings.json'

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
    system_template = "You are a market analyst and know all reviews from Amazon. You're helping me write a concise topic from many reviews."
    human_template = "Using the following reviews, write a topic title that summarizes them.\n\nREVIEWS:{reviews}\n\nTOPIC TITLE:"

    return ChatPromptTemplate(
        messages=[
            SystemMessagePromptTemplate.from_template(system_template),
            HumanMessagePromptTemplate.from_template(human_template),
        ],
        input_variables=["reviews"],
    )


with open(input_datapath,'r') as json_file:
    data = json.load(json_file)

cluster_reviews = defaultdict(list)

for hospital in data['hospitals']:
    for review in hospital['reviews']:
        review_txt = review['text']
        cluster_id = review.get('cluster_id', 0)
        cluster_reviews[cluster_id].append(review_txt)


for cluster_id, reviews in cluster_reviews.items():
    chain = LLMChain(
        llm=ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo-16k"), prompt=get_prompt(), verbose=False
    )
    review_str = '\n'.join(reviews)
    result = chain.run({"reviews": review_str})
    print(result)
