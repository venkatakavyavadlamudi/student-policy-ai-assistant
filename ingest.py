# This File loads the PDF, splits it, embedding and store in vector Database.

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS


# Step 1: Load the PDF
loader=PyPDFLoader("data/student_policy_handbook.pdf")
documents=loader.load()


# Step 2: Split it into Chunks
text_splitter=RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

chunks=text_splitter.split_documents(documents)
print(len(chunks))

# Step 3: Create the Embedding model
embeddings=HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Step 4: Create the FAISS Vector Database
vectorstore=FAISS.from_documents(
chunks,embeddings
)

# Step 5: Save the vector Database
vectorstore.save_local("vectorstore")
print("Vector Database Created Successfully.")
