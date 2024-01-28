from openai import AzureOpenAI
import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

load_dotenv()

# Configure Azure OpenAI Completion Resource: 
#openai.api_type = "azure"
client = AzureOpenAI(
    api_version = "2023-12-01-preview",
    azure_endpoint = os.getenv("AOAI_endpoint"),
    api_key = os.getenv("AOAI_key")
)

completion_deployment_name = os.getenv("AOAI_completion_engine")
chat_deployment_name = os.getenv("AOAI_chat_engine")

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
    
def WebContent(question):
    query = f"Extract the keywords from the text between triple backticks ```{question}``` in order to formulate a bing search query"
    #print(query)
    bing_query = client.completions.create(model=completion_deployment_name, prompt=query)
    #print(bing_query.choices[0].text)
    results = search(bing_query.choices[0].text)
    result = requests.get(results['url'])
    soup = BeautifulSoup(result.content, 'html.parser')
    text = soup.find('body').get_text().strip()
    cleaned_text = ' '.join(text.split('\n'))
    cleaned_text = ' '.join(text.split())
    text_to_summarize = f"Provide one paragraph that answer the question between double back ticks ``{question}`` using information between triple backticks ```{cleaned_text}```"
    returned_text = client.completions.create(model=completion_deployment_name, prompt=text_to_summarize, max_tokens=1024)
    print(f"Based on the following URL: {results['url']}")
    return returned_text.choices[0].text, question


def GPTResponse(Text, question, msg_include=2, messages=[], num=0):
    num += 2
    prompt = f"To answer the following question between double back ticks ``{question}``, use the following information between the triple backticks ```{Text}``` ."
    if messages == []:
        sys_msg = "You are an AI assistant that will get information from the first URL in the Bing search so you are somehow getting information from the internet, and you have to use that information to provide an answer to the question"
        messages = [{"role": "system", "content": sys_msg}, {"role": "user", "content": prompt}]
    else:
        messages.append({"role": "user", "content": prompt})
    if num > msg_include: 
        del messages[1:3]
        num -= 2
    response = client.chat.completions.create(model= chat_deployment_name, messages=messages)
    text = response.choices[0].message.content
    print(f'{text}')    
    question = input("Do you still have other questions? Otherwise type 'exit' to exit:\n")
    if question != "exit":
        messages.append({"role": "assistant", "content": text})
        WebText, question = WebContent(question)
        GPTResponse(WebText, question, msg_include, messages, num)
    return         


question = input("What is your question?\n")
WebText, question = WebContent(question)
GPTResponse(WebText, question, 6)
