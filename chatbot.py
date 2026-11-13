
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_community.vectorstores import FAISS

# Load environment variables
load_dotenv()


# Step 1: Load RAG components
def load_rag_components():

    # Load embedding model
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    # Load FAISS database
    vectorstore = FAISS.load_local(
        "vectorstore",
        embeddings,
        allow_dangerous_deserialization=True
    )

    # Create retriever
    retriever = vectorstore.as_retriever(
        search_kwargs={"k": 4}
    )

    # Initialize Groq LLM
    llm = ChatGroq(
        model="openai/gpt-oss-20b",
        temperature=0
    )

    return retriever, llm


# Step 2: Generate answer
def get_answer(question, retriever, llm):

    # Retrieve relevant documents
    documents = retriever.invoke(question)

    # Prepare context with page information
    context = "\n\n".join(
        [
            f"Page {doc.metadata.get('page', 0) + 1}:\n{doc.page_content}"
            for doc in documents
        ]
    )

    # Final prompt
    final_prompt = f"""
    You are a helpful student policy assistant.

    Answer the user's question using only the provided context.

    Do not make up information or use outside knowledge.

    If the answer is not available in the context, say:
    "I don't know based on the provided documents."

    Context:
    {context}

    Question:
    {question}

    Answer:
    """

    # Generate answer
    response = llm.invoke(final_prompt)

    return response.content, documents
