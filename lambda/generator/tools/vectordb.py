from pinecone import Pinecone, ServerlessSpec
from agents.state import select_embedding_model
from langchain_pinecone import PineconeVectorStore
from typing import Annotated, List

import settings

def init_vector_db() -> PineconeVectorStore:
    # Initialize Pinecone
    print("Initializing Pinecone...")
    pc = Pinecone(
        api_key=settings.PINECONE_API_KEY,
    )
    index_name = settings.PINECONE_INDEX_NAME
    if not pc.has_index(index_name):
        print(f"Creating Pinecone index: {index_name}")
        pc.create_index(
            name=index_name, 
            metric="cosine",
            dimension=768,
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )
    print(f"Using Pinecone index: {index_name}")
    index = pc.Index(index_name)
    print("Initializing embedding...")
    embeddings = select_embedding_model()
    print("Creating Pinecone vector store...")
    vector_store = PineconeVectorStore(
        index=index,
        embedding=embeddings,
    )
    print("Pinecone vector store initialized.")
    return vector_store


def knowledge_base(
    question: Annotated[str, "The query string to search for in the knowledge base."],
    num_results: Annotated[int, "The number of top results to return. Defaults to 5."] = 5
) -> Annotated[List[str], "A list of page contents from the most relevant documents."]:
    """
    Queries the knowledge base using a vector search and returns the most relevant results.

    Args:
        question (str): The query string to search for in the knowledge base.
        num_results (int, optional): The number of top results to return. Defaults to 5.

    Returns:
        List[str]: A list of page contents from the most relevant documents.
    """
    vectordb = init_vector_db()
    results = vectordb.max_marginal_relevance_search(query=question, 
                                                     k=num_results, lambda_mult=0.25)
    return [doc.page_content for doc in results]

