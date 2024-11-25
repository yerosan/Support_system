def query_rag_system(query_model,retriever, query):
    # Retrieve relevant documents based on the query
    docs = retriever.get_relevant_documents(query)
    context = "\n".join([doc.page_content for doc in docs])
    
    # Prepare the prompt with context for the Ollama model
    prompt = f"Given the following context, answer the question: {context}\n\nQuestion: {query}\nAnswer:"
    
    # Send the prompt to the Ollama model
    response = query_model(prompt)
    return response