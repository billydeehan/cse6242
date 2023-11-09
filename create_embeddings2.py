import openai
import tiktoken
import pandas as pd
import json
import os

max_tokens = 500
embedding_model = ''
embedding_encoding = 'cl100k_base'
encoding = tiktoken.get_encoding(embedding_encoding)

openai.api_key = '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'

def get_embedding(text, model="text-embedding-ada-002"):
   text = text.replace("\n", " ")
   return openai.Embedding.create(input = [text], model=model)['data'][0]['embedding']

folder = './data/jsons'
output_folder = './data/json_embeddings'

for filename in os.listdir(folder):
    filepath = os.path.join(folder, filename)
    output_filepath = os.path.join(output_folder, filename)
    if not os.path.isfile(output_filepath):
        print(filepath)
        with open(filepath,'r') as json_file:
            data = json.load(json_file)
            for review in data['reviews'][0]['reviews_data']:
                text = review['review_text']
                if text is not None:
                    token_count = len(encoding.encode(text))
                    if token_count > max_tokens:
                        text = text[:1000]
                    review['embedding'] = get_embedding(text)
        with open(output_filepath,'w') as json_file:
            json.dump(data,json_file,indent=4)

