# AzureGPTwithBingSeach
In this repo I will be using Azure OpenAI and Bing Search to somehow let Azure GPT get their information from the internet. 

* [Bing Web Search API](https://learn.microsoft.com/en-us/bing/search-apis/bing-web-search/overview) used to return webpages related to the query. 
* [Azure OpenAI](https://learn.microsoft.com/en-us/azure/ai-services/openai/overview) used with the page content to provide an answer to the questio. 

# Table of contents:

# Step 1 - Getting a URL from the Bing Web Search API
Before starting anything we would need to install the required python packages.  
You can do that by using the following command: 
```
pip install -r requirements.txt
```
We would need to import the following libraries: 
``` Python
import openai
import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
```
I have created .env file that will contain the keys and endpoints for the Bing and Azure OpenAI resource.  
We will need to get the Bing Web Search key and store the value in the .env file as shown: 
![Bing Key](images/BingKey.png) 

To configure the Bing resource, we would use load_dotenv and os to load the key from .env file as follows: 
``` Python
load_dotenv()
# Load your Bing Search V7 subscription key from your environment variable.
subscription_key = os.getenv("Bing_key") # Bing_key is the name of the variable containing the Bing resource key in .env file. 
endpoint = "https://api.bing.microsoft.com" + "/v7.0/search"
```

# Step 2 - Getting the contents of the webpage

# Step 3 - Using Azure Open AI model to answer the question
