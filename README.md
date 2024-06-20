# HDB BTO Chatbot

The Housing & Development Board (HDB) is the public housing authority in Singapore. As someone who is awaiting the completion of my BTO, I found myself searching for relevant information on the HDB website. This prompted me to create this chatbot, which is designed to address questions related to Build-to-Order (BTO) flats. It is developed using Streamlit, Langchain and Chroma.

![assets/hdb_chatbot_logo.png](https://github.com/Joanna-Khek/hdb-bto-chatbot/blob/423cc17ee003c67292efb531f1b532724bb6aa55/assets/hdb_chatbot_logo.png)

## Demo
Users have to first input their OpenAI API Key. After the initial setup, users can start asking their questions!

![assets/app_demo.gif](https://github.com/Joanna-Khek/hdb-bto-chatbot/blob/c41dd94c8ebddd3216e106dc59ff4b723d047bab/assets/app_demo.gif)

## Scraping Information
Information were first scraped from these links. The script used for scrapping can be found in ``src/llm_model/scraper.py``
  - https://www.hdb.gov.sg/cs/infoweb/residential/buying-a-flat/buying-procedure-for-new-flats/timeline
  - https://www.hdb.gov.sg/cs/infoweb/residential/buying-a-flat/buying-procedure-for-new-flats/timeline/plan-your-finances
  - https://www.hdb.gov.sg/cs/infoweb/residential/buying-a-flat/buying-procedure-for-new-flats/modes-of-sale
  - https://www.hdb.gov.sg/cs/infoweb/residential/buying-a-flat/buying-procedure-for-new-flats/modes-of-sale/faqs-for-sales-launch
  - https://www.hdb.gov.sg/cs/infoweb/residential/buying-a-flat/buying-procedure-for-new-flats/application
  - https://www.hdb.gov.sg/cs/infoweb/residential/buying-a-flat/buying-procedure-for-new-flats/application/priority-schemes
  - https://www.hdb.gov.sg/cs/infoweb/residential/buying-a-flat/buying-procedure-for-new-flats/application/fresh-start-housing-scheme
  - https://www.hdb.gov.sg/cs/infoweb/residential/buying-a-flat/buying-procedure-for-new-flats/booking-of-flat
  - https://www.hdb.gov.sg/cs/infoweb/residential/buying-a-flat/buying-procedure-for-new-flats/sign-agreement-for-lease
  - https://www.hdb.gov.sg/cs/infoweb/residential/buying-a-flat/buying-procedure-for-new-flats/key-collection

## LLM
Due to the limited GPU memory of my local machine, I initially experimented with small open-source models (gemma-2b-it), which did not yield satisfactory results. Eventually, I switched to using OpenAI's gpt3.5-turbo, and as anticipated, the results were significantly better.

## Vector Store
Since the amount of data wasn't large, I used Chroma as it stores the data locally. The retrieval of data was quick, unlike cloud vector stores.

## RAG Chain
A Rag Chain was created using Langchain. The following prompt template was used:
```
You are a helpful assistant for question-answering tasks.
You are given the following context information.
Context: {context}

Answer the following question from a user.
Use only information from the previous context information. Do not invent stuff.
If you don't know the answer, say that you don't know.

In your answer, include the source url from the metadata: {metadata}

Question: {query}

Answer:
```

To make the response generation more 'robot' like, I also streamed the response by adding a delay to every character in the response output.

## App
App was built using Streamlit, which has become one of my favourite Python framework to develop data apps!
