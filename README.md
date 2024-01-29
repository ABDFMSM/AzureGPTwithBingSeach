# AzureGPTwithBingSeach

**This updated repo now uses an AOAI completion model as well to extract keywords from the query for the bing search and to summarize the webpage content.** 

In this repo I will be using Azure OpenAI and Bing Search to somehow let Azure GPT get their information from the internet. 

* [Bing Web Search API](https://learn.microsoft.com/en-us/bing/search-apis/bing-web-search/overview) used to return webpages related to the query. 
* [Azure OpenAI](https://learn.microsoft.com/en-us/azure/ai-services/openai/overview) used with the page content to provide an answer to the question. 

# Table of contents:
- [Step 1 - Getting Things Ready](https://github.com/ABDFMSM/AzureGPTwithBingSeach?tab=readme-ov-file#step-1---getting-things-ready)  
- [Step 2 - Getting a URL from the Bing Web Search API](https://github.com/ABDFMSM/AzureGPTwithBingSeach?tab=readme-ov-file#step-2---getting-a-url-from-the-bing-web-search-api)  
- [Step 3 - Getting the Contents of the Webpage](https://github.com/ABDFMSM/AzureGPTwithBingSeach?tab=readme-ov-file#step-3---getting-the-contents-of-the-webpage)  
- [Step 4 - Using Azure Open AI model to answer the question](https://github.com/ABDFMSM/AzureGPTwithBingSeach?tab=readme-ov-file#step-4---using-azure-open-ai-model-to-answer-the-question)  
- [Output Example](https://github.com/ABDFMSM/AzureGPTwithBingSeach?tab=readme-ov-file#output-example)

# Step 1 - Getting Things Ready
Before starting anything we would need to install the required python packages.  
You can do that by using the following command: 
```
pip install -r requirements.txt
```
We would need to import the following libraries: 
``` Python
from openai import AzureOpenAI
import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
```
I have created .env file that will contain the keys and endpoints for the Bing and Azure OpenAI resource.  
On VScode you can create an empty file and you name it .env which should contain the following: 
  ![EnvFile](Images/EnvFile.png)

## Configuring Bing Web Seach Resrouce
We will need to get the Bing Web Search key and store the value in the .env file as shown: 
![Bing Key](Images/BingKey.png) 

To configure the Bing resource, we would use load_dotenv and os to load the key from .env file as follows: 
``` Python
load_dotenv()
# Load your Bing Search V7 subscription key from your environment variable.
subscription_key = os.getenv("Bing_key") # Bing_key is the name of the variable containing the Bing resource key in .env file. 
endpoint = "https://api.bing.microsoft.com" + "/v7.0/search"
```

## Configuring Azure OpenAI Resource: 
Afterwards, we need to do the same to configure the Azure OpenAI resource. 
We would get the Azure OpenAI resource key and endpoint from Azure portal as shown: 
  ![AOAIKey&Endpoint](Images/AOAIKey&Endpoint.png) 

Now we would configure AOAI resource as follows: 
``` Python
# Configure Azure OpenAI Resource: 
#openai.api_type = "azure"
client = AzureOpenAI(
    api_version = "2023-12-01-preview",
    azure_endpoint = os.getenv("AOAI_endpoint"),
    api_key = os.getenv("AOAI_key")
)
completion_deployment_name = os.getenv("AOAI_completion_engine")
chat_deployment_name = os.getenv("AOAI_chat_engine")
```

# Step 2 - Getting a URL from the Bing Web Search API
I have created a function that will return the first URL the Bing search API find. 
``` Python
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
```

# Step 3 - Getting the Contents of the Webpage
After getting the user question, the AOAI completion model would extract the keywords and feed it to the Bing resource. The first URL content is extracted throught requests library and then fed again to completion model to summarize it.
``` Python
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
```

# Step 4 - Using Azure Open AI model to answer the question
Feeding the summarized paragraph and the question to the AOAI chat completion model. In this updated model I have added the ability to provide previous messages and include certain number of past messages for context. 
Since AOAI model is not connected to the internet, the AOAI will use the webpage contents as a way to get real-time information to answer the user's question. 
``` Python
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

```

# Output Example
Finally we can run the following code to start the conversation with the chatCompletion model, it will always provide the URL that it used to answer user's questions: 
``` Python
question = input("What is your question?\n")
WebText, question = WebContent(question)
GPTResponse(WebText, question, 6)
```
Here is the question and the response you can get: 
  ![Example](Images/Example.png)




