import streamlit as st
import time
import json
import pandas as pd
from langchain_openai import OpenAIEmbeddings
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import DataFrameLoader

st.title("HDB :blue[Chatbot] :robot_face:")
with st.expander(':orange[Information]', expanded=True):
    st.write('''
             The Housing & Development Board (HDB) is Singapore's public housing authority.
             This chatbot focuses on answering BTO related questions. Information are scraped from
             https://www.hdb.gov.sg/cs/infoweb/residential/buying-a-flat/buying-procedure-for-new-flats
             '''
    )
with st.sidebar:
  st.image("assets/hdb_chatbot_logo.png", width=200)

@st.cache_resource
def initialise_setup(openai_api_key):
    
    # Test Connection
    embeddings = OpenAIEmbeddings(model='text-embedding-ada-002', openai_api_key=openai_api_key)
    llm = ChatOpenAI(model="gpt-3.5-turbo-0125", openai_api_key=openai_api_key)

    with open('src/llm_model/data/data.json', 'rt') as f_in:
        docs_raw = json.load(f_in)
        
    df_docs = pd.DataFrame(docs_raw)
    df_docs = DataFrameLoader(df_docs, page_content_column="texts")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    docs = df_docs.load_and_split(text_splitter=text_splitter)
    vectorstore = Chroma.from_documents(documents=docs, embedding=embeddings, persist_directory='db')
    
    return vectorstore, llm

def stream_response(response):
    for word in response.split():
        yield word + " "
        time.sleep(0.05)

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def get_metadata_source(docs):
    return [doc.metadata for doc in docs]

def generate_response(query, rag_chain):
    return rag_chain.invoke(query)
       
def get_rag_chain(llm, vectorstore):
    template = """You are a helpful assistant for question-answering tasks. 
    You are given the following context information.
    Context: {context}

    Answer the following question from a user.
    Use only information from the previous context information. Do not invent stuff.
    If you don't know the answer, say that you don't know.

    In your answer, include the source url from the metadata: {metadata}
    
    Question: {query}

    Answer:"""
    
    retriever = vectorstore.as_retriever()
    
    prompt = PromptTemplate(
        input_variables=["context", "metadata", "query"],
        template=template)

    rag_chain = (
        {"context": retriever | format_docs,
        "metadata": retriever | get_metadata_source,
        "query": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return rag_chain
    
def main_conversation_ui(rag_chain):
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant",
                                    "content": "Welcome to HDB Chatbot! What would you like to ask?"}]
    
    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # User's prompt
    if prompt := st.chat_input():
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        
    
        # Bot's response
        response = generate_response(prompt, rag_chain)
        with st.chat_message("assistant"):
            response = st.write_stream(stream_response(response))

        st.session_state.messages.append({"role": "assistant", "content": response})

def run():
    ready = True
    
    with st.sidebar:
        openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")
        
    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
        ready = False
        
    if ready:
        vectorstore, llm = initialise_setup(openai_api_key)
        with st.sidebar:
            st.success("API Authenticated!")
        rag_chain = get_rag_chain(llm=llm, vectorstore=vectorstore)
        main_conversation_ui(rag_chain)
        
    else:
        st.stop()
        
if __name__ == "__main__":
    run()
    