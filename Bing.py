import openai
import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

load_dotenv()

# Configure Azure OpenAI Completion Resource: 
openai.api_type = "azure"
openai.api_version = '2023-05-15'
openai.api_base = os.getenv("OpenAI_endpoint")
openai.api_key = os.getenv("OpenAI_key")
engine_name = os.getenv("OpenAI_engine")

# Add your Bing Search V7 subscription key and endpoint to your environment variables.
subscription_key = os.getenv("Bing_key")
endpoint = "https://api.bing.microsoft.com/v7.0/search"

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
    
def WebContent():
    question = input("What is your question?")

    results = search(question)

    result = requests.get(results['url'])
    soup = BeautifulSoup(result.content, 'html.parser')
    text = soup.find('body').get_text().strip()
    cleaned_text = ' '.join(text.split('\n'))
    cleaned_text = ' '.join(text.split())
    return cleaned_text, question


def GPTResponse(Text, question):

    prompt = f"Use the following information: {Text} to get the answer to the following question {question}."
    sys_msg = "You are an AI assistant that will get information from the first URL in the Bing search so you are somehow getting information from the internet, and you have to use that information to provide an answer to the question"
    response = openai.ChatCompletion.create(engine= engine_name, messages=[
        {'role': 'system', 'content': sys_msg},
        {'role': 'user', 'content': prompt}])
    text = response['choices'][0]['message']['content']
    print(f'Answer: {text}')

WebText, question = WebContent()
GPTResponse(WebText, question)
