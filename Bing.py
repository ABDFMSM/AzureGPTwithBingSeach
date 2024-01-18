import openai
from pprint import pprint
import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

load_dotenv()

# Configure Azure OpenAI Completion Resource: 
openai.api_type = "azure"
openai.api_version = '2023-05-15'
openai.api_base = os.getenv("OpenAISweden_endpoint")
openai.api_key = os.getenv("OpenAISweden_key")
engine_name = os.getenv("OpenAISweden_engine")

# Add your Bing Search V7 subscription key and endpoint to your environment variables.
subscription_key = os.getenv("Bing_key")
print(subscription_key)
endpoint = "https://api.bing.microsoft.com" + "/v7.0/search"

# Query term(s) to search for. 
query = "What is the latest GPT released by Microsoft?"

# Construct a request
def search(query):
    mkt = 'en-US'
    params = { 'q': query, 'mkt': mkt, 'count':5, 'responseFilter': ['Webpages']}
    headers = { 'Ocp-Apim-Subscription-Key': subscription_key }

    # Call the API
    try:
        response = requests.get(endpoint, headers=headers, params=params)
        response.raise_for_status()
        return response.json()['webPages']['value'][0]

    except Exception as ex:
        raise ex
    
question = input("What is your question?")

results = search(question)

result = requests.get(results['url'])
soup = BeautifulSoup(result.content, 'html.parser')
text = soup.find('body').get_text().strip()
cleaned_text = ' '.join(text.split('\n'))
cleaned_text = ' '.join(text.split())
#print(cleaned_text)

#print(results_list)

prompt = f"Use the following information: {cleaned_text} to get the answer to the following question {question}."
content = "You are an AI assistant that will get information from the first URL in the Bing search so you are somehow getting information from the internet, and you have to use that information to provide an answer to the question"

if results: 
    response = openai.ChatCompletion.create(engine= engine_name, messages=[
        {'role': 'system', 'content': content},
        {'role': 'user', 'content': prompt}])
    text = response['choices'][0]['message']['content']
    print(f'Answer: {text}')
else:
    print("Error: No resutls found for the given question.")