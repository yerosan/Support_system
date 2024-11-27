import requests
import json


from langchain.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain_core.prompts import MessagesPlaceholder
from langchain_core.messages import HumanMessage,AIMessage

from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import SystemMessage, trim_messages



def query_ollama_model(prompt):
    url = "http://localhost:11434/api/generate"
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": "llama3.2",
        "prompt": prompt,
        "max_tokens": 100
    }

    try:
        response = requests.post(url, json=payload, headers=headers, stream=True)
        response.raise_for_status()  # Will raise an error for 4xx/5xx status codes

        full_response = ""  # Initialize to store the full response
        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line.decode("utf-8"))  # Decode and parse the JSON
                    if "response" in data:
                        full_response += data["response"]  # Accumulate the response parts

                    if data.get("done", False):  # Stop processing if "done" is True
                        break
                except json.JSONDecodeError:
                    continue  # Skip invalid lines in the response stream
        
        return full_response  # Return the accumulated response
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Error interacting with Ollama: {e}")
    

# def query_ollama_stream(prompt):
#     url = "http://localhost:11434/api/generate"
#     headers = {"Content-Type": "application/json"}
#     payload = {
#         "model": "llama3.2",
#         "prompt": prompt,
#         "max_tokens": 100
#     }

#     response = requests.post(url, json=payload, headers=headers, stream=True)
#     response.raise_for_status()
#     for line in response.iter_lines():
#         if line:
#             print("The line____------", line)
#             try:
#                 data = json.loads(line.decode("utf-8"))
#                 if "response" in data:
#                     yield data["response"].replace("\n", " ")
#             except json.JSONDecodeError:
#                 continue


# def query_ollama_stream(retriever,fileName,query):
#     global store
#     session_Id = f'{fileName}'

#     model = "llama3.2"

#     # Initialize the trimmer
#     trimmer = trim_messages(
#         max_tokens=2000,
#         strategy="last",
#         token_counter=model,
#         include_system=True,
#         allow_partial=False,
#         start_on="human"
#     )

#     # System prompts
#     contextualize_q_system_prompt = (
#         "Given a chat history and the latest user question, "
#         "which might reference context in the chat history, "
#         "formulate a standalone question. Do NOT answer the question, "
#         "just reformulate it if needed and otherwise return it as is."
#     )

#     system_prompt = (
#         """
#         You are an expert research assistant tasked with answering questions solely based on the provided documents. 
#         Your role is to ensure that all responses are grounded in the context of these documents.
#         Only provide answers derived directly from the content of the provided documents.
#         Ensure that each response is detailed, elaborated, comprehensive, and addresses the query.
#         Do not speculate, assume, or guess. Stick strictly to the facts as presented in the document.
#         """
#         "{context}"
#     )

#     # Define history-aware retriever and prompts
#     contexualize_chatHistory = ChatPromptTemplate.from_messages(
#         [
#             ("system", contextualize_q_system_prompt),
#             MessagesPlaceholder("chat_history"),
#             ("human", "{input}"),
#         ]
#     )

#     history_aware_retriever = create_history_aware_retriever(
#         model, retriever, contexualize_chatHistory
#     )

#     qa_prompt = ChatPromptTemplate.from_messages(
#         [
#             ("system", system_prompt),
#             MessagesPlaceholder("chat_history"),
#             ("human", "{input}"),
#         ]
#     )

#     question_answer_chain = create_stuff_documents_chain(model, qa_prompt)
#     rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

#     print("The Retrierver______-----", rag_chain)

#     # Session-based chat history
#     def get_session_history(session_id: str) -> BaseChatMessageHistory:
#         if session_id not in store:
#             store[session_id] = ChatMessageHistory()

#         if store[session_id].messages:
#             trimmed_messages = trimmer.invoke(store[session_id].messages)
#             store[session_id].messages = trimmed_messages

#         return store[session_id]

#     conversational_rag_chain = RunnableWithMessageHistory(
#         rag_chain,
#         get_session_history,
#         input_messages_key="input",
#         history_messages_key="chat_history",
#         output_messages_key="answer",
#     )

#     # Invoke the chain
#     try:
#         chain_response = conversational_rag_chain.invoke(
#             {"input": query},
#             config={"configurable": {"session_id": session_Id}},
#         )
#     except Exception as e:
#         raise RuntimeError(f"Error during chain invocation: {e}")

#     # Prepare prompt for external API
#     full_prompt = f"{system_prompt.format(context=chain_response['answer'])}"
#     url = "http://localhost:11434/api/generate"
#     headers = {"Content-Type": "application/json"}
#     payload = {
#         "model": "llama3.2",
#         "prompt": full_prompt,
#         "max_tokens": 100
#     }

#     # Fetch response from external API
#     try:
#         response = requests.post(url, json=payload, headers=headers, stream=True)
#         response.raise_for_status()
#         for line in response.iter_lines():
#             if line:
#                 try:
#                     data = json.loads(line.decode("utf-8"))
#                     if "response" in data:
#                         yield data["response"].replace("\n", " ")
#                 except json.JSONDecodeError:
#                     continue
#     except requests.RequestException as e:
#         raise RuntimeError(f"API call failed: {e}")








import httpx
from typing import Generator

def call_llama_api(prompt: str, model: str = "llama3.2", max_tokens: int = 100) -> str:
    """
    Call the locally hosted Llama API to generate a response based on the provided prompt.
    """
    url = "http://localhost:11434/api/generate"
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": model,
        "prompt": prompt,
        "max_tokens": max_tokens,
    }

    try:
        response = httpx.post(url, json=payload, timeout=10)
        response.raise_for_status()  # Raise an error for HTTP codes >= 400
        result = response.json()
        return result.get("output", "")
    except Exception as e:
        print(f"Error calling Llama API: {e}")
        return "Error: Could not retrieve response from the model."

# def call_llama_stream(prompt: str, model: str = "llama3.2", max_tokens: int = 100) -> Generator[str, None, None]:
#     """
#     Call the locally hosted Llama API and stream the response in chunks.
#     """
#     url = "http://localhost:11434/api/generate"
#     headers = {"Content-Type": "application/json"}
#     payload = {
#         "model": model,
#         "prompt": prompt,
#         "max_tokens": max_tokens,
#     }

#     #     # Fetch response from external API
# #     try:
# #         response = requests.post(url, json=payload, headers=headers, stream=True)
# #         response.raise_for_status()
# #         for line in response.iter_lines():
# #             if line:
# #                 try:
# #                     data = json.loads(line.decode("utf-8"))
# #                     if "response" in data:
# #                         yield data["response"].replace("\n", " ")
# #                 except json.JSONDecodeError:
# #                     continue
# #     except requests.RequestException as e:
# #         raise RuntimeError(f"API call failed: {e}")

#     try:
#         with httpx.stream("POST", url, json=payload, headers=headers, timeout=30) as response:
#             response.raise_for_status()
#             for line in response.iter_lines():
#                 if line:
#                     print("The lines ___---_", line)
#                     try:
#                         data=json.loads(line.decode("utf-8"))
#                         if "response" in data:
#                             yield data["response"].replace("\n","")
#                     except json.JSONDecodeError:
#                         continue
                

#                 # yield chunk
#     except Exception as e:
#         print(f"Error calling Llama Stream API: {e}")
#         yield "Error: Could not retrieve response from the Llama model."



def call_llama_stream(prompt: str, model: str = "llama3.2", max_tokens: int = 100) -> Generator[str, None, None]:
    """
    Call the Llama API, collect the full response, and yield it as a single chunk.
    """
    url = "http://localhost:11434/api/generate"
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": model,
        "prompt": prompt,
        "max_tokens": max_tokens,
    }

    try:
        # Use httpx to stream the response
        with httpx.stream("POST", url, json=payload, headers=headers, timeout=30) as response:
            response.raise_for_status()

            full_response = []
            for line in response.iter_lines():
                if line:
                    try:
                        # Parse the JSON response line
                        data = json.loads(line)
                        if "response" in data:
                            yield data["response"]
                            # full_response.append(data["response"])
                        # if data.get("done", False):
                        #     break  # Stop when "done" is True
                    except json.JSONDecodeError:
                        continue
            
            # Combine the full response and yield it
            # yield "".join(full_response)
    except Exception as e:
        print(f"Error calling Llama Stream API: {e}")
        yield "My apologies; at the moment, I am struggling to manage things on my own."


from langchain.prompts.chat import ChatPromptTemplate
# from langchain.schema.messages import MessagesPlaceholder
from langchain_core.prompts import MessagesPlaceholder
# from langchain.schema.document import Document
# from langchain.retrievers import VectorStoreRetriever



#   You are an expert research assistant tasked with answering questions solely based on the provided documents.
#         Your role is to ensure that all responses are grounded in the context of these documents.
#         Only provide answers derived directly from the content of the provided documents.
#         Ensure that each response is detailed, elaborated, comprehensive, and addresses the query.
#         Do not speculate, assume, or guess. Stick strictly to the facts as presented in the document.

def query_ollama_stream(retriever, fileName, query):
    global store
    session_id = f"{fileName}"

    contextualize_q_system_prompt = (
        "Given a chat history and the latest user question "
        "which might reference context in the chat history, "
        "formulate a standalone question which can be understood "
        "without the chat history. Do NOT answer the question, "
        "just reformulate it if needed and otherwise return it as is."
    )

    system_prompt = (
        """
        You are a professional research assistant responding exclusively based on the provided documents.
        Respond thoughtfully to client greetings or emotional queries with appropriate and valuable replies.
        Ensure all answers are factual, detailed, and comprehensive, strictly derived from the documents.
        Avoid speculation or assumptions; adhere closely to the document's content.
        """
        "{context}"
    )

    # Generate the prompt with document context
    docs = retriever.get_relevant_documents(query)
    context = "\n".join([doc.page_content for doc in docs])
    full_prompt = system_prompt.format(context=context) + f"\nUser Query: {query}"

    # Stream the response from the Llama API
    return call_llama_stream(full_prompt)
