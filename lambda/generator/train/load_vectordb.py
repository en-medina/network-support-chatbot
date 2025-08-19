from pathlib import Path
from typing import List

from langchain_community.document_loaders import PyMuPDFLoader, TextLoader
from langchain_core.documents import Document  # or langchain.schema.Document depending on your version
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_ollama.embeddings import OllamaEmbeddings
from langchain_pinecone import PineconeVectorStore

from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv
from os import getenv

load_dotenv(Path(__file__).parent.parent / ".env")

def pdf_loader(pdf_dir: Path) -> List[Document]:
    """
    Load a PDF file and return its content as a list of documents.
    
    Args:
        pdf_path (pathlib.Path): Path to the PDF file.
        
    Returns:
        list: A list of documents loaded from the PDF.
    """
    docs = list()

    # Load the PDF document
    for pdf_path in pdf_dir.glob("*.pdf"):
        loader = PyMuPDFLoader(pdf_path)
        docs.extend(loader.load())

    return docs

def md_loader(md_dir: Path) -> List[Document]:
    """
    Load Markdown files and return their content as a list of documents.
    
    Args:
        md_dir (pathlib.Path): Directory containing Markdown files.
        
    Returns:
        list: A list of documents loaded from the Markdown files.
    """
    docs = list()

    # Load the Markdown documents
    for md_path in md_dir.glob("*.md"):
        loader = TextLoader(md_path, encoding="utf-8")
        docs.extend(loader.load())

    return docs

def initialize_pinecone():
    # Initialize Pinecone
    print("Initializing Pinecone...")
    pc = Pinecone(
        api_key=getenv("PINECONE_API_KEY"),
    )
    index_name = getenv("PINECONE_INDEX_NAME", "network-support-chatbot")
    if not pc.has_index(index_name):
        print(f"Creating Pinecone index: {index_name}")
        pc.create_index(
            name=index_name, 
            metric="cosine",
            dimension=768,
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )
    index = pc.Index(index_name)
    return index

def main():
    # Define the path to the directory containing PDF and Markdown files
    print("Loading documents...") 
    data_dir = Path(__file__).parent / "data"

    docs = list()
    docs.extend(pdf_loader(data_dir / "pdf"))
    docs.extend(md_loader(data_dir / "md"))

    # Keep only the name of the file as metadata
    for i in range(len(docs)):
        docs[i].metadata["source"] = Path(docs[i].metadata["source"]).name

    # Remove entries that contain less than 10 words
    docs = [doc for doc in docs if len(doc.page_content.split()) >= 10]

    # Print the number of documents loaded
    print(f"Number of documents loaded: {len(docs)}")
    embeddings = OllamaEmbeddings(model="qllama/multilingual-e5-base:q4_k_m")
    index = initialize_pinecone()
    vector_store = PineconeVectorStore(
        index=index,
        embedding=embeddings,
    )
    print("Adding documents to Pinecone index...")
    vector_store.add_documents(docs)
    print("Documents added to Pinecone index.")

if __name__ == "__main__":
    main()
    # embeddings = OllamaEmbeddings(model="qllama/multilingual-e5-large")
    # text = "Hello, how are you?"
    # embedding = embeddings.embed_query(text)
    # print(embedding[:5])

    # embeddings = HuggingFaceEmbeddings(model="intfloat/multilingual-e5-large")
    # text = "Hello, how are you?"
    # embedding = embeddings.embed_query(text)
    # print(embedding[:5])
    #main()