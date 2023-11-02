import openai
import tiktoken
import pandas as pd
import json
input_datapath = 'data/all_reviews.json'
max_tokens = 500
embedding_model = ''
embedding_encoding = 'cl100k_base'
encoding = tiktoken.get_encoding(embedding_encoding)

openai.api_key = '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'

def get_embedding(text, model="text-embedding-ada-002"):
   text = text.replace("\n", " ")
   return openai.Embedding.create(input = [text], model=model)['data'][0]['embedding']

with open(input_datapath,'r') as json_file:
    data = json.load(json_file)

for hospital in data['hospitals']:
    for review in hospital['reviews']:
        text = review['text']
        token_count = len(encoding.encode(text))
        # Shorten the text to 100 characters
        if token_count > max_tokens:
            text = text[:1000]
        if text != '':
            review['embedding'] = get_embedding(text)

output_file_path = './data/all_reviews_with_embeddings.json'

with open(output_file_path,'w') as json_file:
    json.dump(data,json_file,indent=4)
