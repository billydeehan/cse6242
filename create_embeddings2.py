import openai
import tiktoken
import pandas as pd
import json
import os
import re
max_tokens = 500
embedding_model = ''
embedding_encoding = 'cl100k_base'
encoding = tiktoken.get_encoding(embedding_encoding)

openai.api_key = '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'

def get_embedding(text, model="text-embedding-ada-002"):
   text = text.replace("\n", " ")
   try:
        return openai.Embedding.create(input = [text], model=model)['data'][0]['embedding']
   except Exception as e:
        print(f"Error creating embedding for {text}: {str(e)}")
        return []
   
folder = './data/reviews'
output_folder = './data/embeddings'
   
for filename in os.listdir(folder):
    filepath = os.path.join(folder, filename)
    output_filepath = os.path.join(output_folder, filename)
    if not os.path.isfile(output_filepath):
        print(filepath)
        with open(filepath,'r') as json_file:
            data = json.load(json_file)
            if 'reviews' in data:
                for review in data['reviews']:
                    text = review['text']
                    if text is not None and text!='':
                        text = re.sub(r'[^a-zA-Z\s]', '', text)
                        token_count = len(encoding.encode(text))
                        if token_count > max_tokens:
                            text = text[:1000]
                        review['embedding'] = get_embedding(text)
        with open(output_filepath,'w') as json_file:
            json.dump(data,json_file,indent=4)

