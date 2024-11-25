# Function to generate embeddings using Sentence-Transformer
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema import Document  # Import Document class
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain_community.document_loaders import TextLoader


import os
import logging

store={}
def generate_embeddings(text, persist_directory):
    os.makedirs(persist_directory, exist_ok=True)
    text_file_path = os.path.join(persist_directory, "temp_text.txt")
    
    try:
        # Split the text into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200, add_start_index=True
        )
        document = Document(page_content=text)
        all_splits = text_splitter.split_documents([document])

        # Initialize embeddings and vectorstore
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        vectorstore = Chroma.from_documents(
            documents=all_splits, embedding=embeddings, persist_directory=persist_directory
        )
        vectorstore.persist()  # Ensure data is saved to disk
        
        print("Number of documents stored in Chroma vectorstore>>>>>>>>>>>>>:", len(all_splits))
        return persist_directory  # Return the directory for retrieval
    except Exception as e:
        logging.error(f"Failed to initialize vector store: {e}")
        raise




def create_retrieval_chain(fileName):
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    vectorstore = Chroma(
            persist_directory=fileName,
            embedding_function=embeddings
        )
    
    retriever = vectorstore.as_retriever()

    # DOCES=retriever.invoke("hOW IS YEROSAN")
    # print("tHE DOCS------_",DOCES)
    # More debugging outputs to confirm
    # print("Embeddings initialized with model:", embeddings.model_name)
    # print("Retriever created:", retriever)
    
    return retriever


# from langchain.embeddings import HuggingFaceEmbeddings
# from langchain.vectorstores import Chroma

# def create_retrieval_chain(fileName):
#     # Print the file name for debugging
#     print("The file name provided:--------_____", fileName)
    
#     # Initialize embeddings
#     embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
#     print("Embeddings initialized with model:", embeddings.model_name)
    
#     # Initialize Chroma vector store
#     vectorstore = Chroma(
#         persist_directory=fileName,
#         embedding_function=embeddings
#     )
#     print("Vectorstore initialized with persist directory:", fileName)
    
#     # Create the retriever
#     retriever = vectorstore.as_retriever()
#     print("Retriever created successfully:", retriever)
    
#     # Use the retriever to get relevant documents
#     query = "How is Yerosan?"
#     docs = retriever.get_relevant_documents(query)
#     print("Retrieved documents:", docs)
    
#     return retriever
        


# from langchain.chains import create_stuff_documents_chain
# from langchain.vectorstores import Chroma
# from langchain.embeddings import HuggingFaceEmbeddings
# # from langchain.llms import OpenAI

# def create_retrieval_chain(fileName, query, model_name="all-MiniLM-L6-v2", llm_model="gpt-4"):
#     """
#     Creates a high-performing retrieval chain that retrieves and processes documents based on a query.
    
#     Args:
#         fileName (str): The directory where vectorstore data is persisted.
#         query (str): The query for retrieving documents.
#         model_name (str): Embedding model name. Default is "all-MiniLM-L6-v2".
#         llm_model (str): The language model to use for document processing. Default is "gpt-4".
    
#     Returns:
#         str: A natural language response to the query.
#     """
#     try:
#         print(f"The file name provided: {fileName}")
        
#         # Initialize embeddings
#         embeddings = HuggingFaceEmbeddings(model_name=model_name)
#         print(f"Embeddings initialized with model: {embeddings.model_name}")
        
#         # Initialize Chroma vector store
#         vectorstore = Chroma(
#             persist_directory=fileName,
#             embedding_function=embeddings
#         )
#         print(f"Vectorstore initialized with persist directory: {fileName}")
        
#         # Create the retriever
#         retriever = vectorstore.as_retriever()
#         print("Retriever created successfully.")
        
#         # Retrieve documents based on the query
#         docs = retriever.get_relevant_documents(query)
#         print(f"Retrieved {len(docs)} documents.")
        
#         if not docs:
#             print("No documents found for the query.")
#             return "No relevant documents were found for the query."
        
#         # Initialize the LLM
#         llm = OpenAI(model=llm_model)
        
#         # Use create_stuff_documents_chain to process the documents
#         chain = create_stuff_documents_chain(llm)
#         response = chain.run(input_documents=docs, question=query)
        
#         print("Generated response:", response)
#         return response

#     except Exception as e:
#         print(f"Error in retrieval chain: {e}")
#         return f"An error occurred: {str(e)}"