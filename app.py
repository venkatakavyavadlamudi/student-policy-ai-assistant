

import streamlit as st
from chatbot import load_rag_components, get_answer

# Page configuration
st.set_page_config(
    page_title="Student Policy Assistant",
    page_icon="🎓",
    layout="wide"
)

# Custom styling
st.markdown("""
<style>
    .main {
        background-color: #F7F9FC;
    }

    .block-container {
        padding-top: 2rem;
    }

    .title {
        color: #17365D;
        font-size: 32px;
        font-weight: bold;
    }

    .subtitle {
        color: #64748B;
        font-size: 15px;
    }

    [data-testid="stSidebar"] {
        background-color: #EEF4FC;
    }

    .stChatMessage {
        border-radius: 12px;
    }
</style>
""", unsafe_allow_html=True)


# Load RAG components only once
@st.cache_resource
def initialize_chatbot():
    return load_rag_components()


# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []


# Load backend
try:
    retriever, llm = initialize_chatbot()
    backend_ready = True

except Exception as e:
    backend_ready = False
    st.error(f"Unable to load chatbot: {e}")


# Sidebar
with st.sidebar:

    st.title("🎓 Student Help Center")

    st.markdown("---")

    st.subheader("📚 Policy Categories")

    categories = [
        "Attendance Policy",
        "Leave Policy",
        "Examination Policy",
        "Assignment Policy",
        "Fee Payment Policy",
        "Scholarships",
        "Library Rules",
        "Placement Policy"
    ]

    for category in categories:
        st.markdown(f"📌 {category}")

    st.markdown("---")

    st.subheader("💡 Suggested Questions")

    suggestions = [
        "What is the minimum attendance requirement?",
        "How can I apply for leave?",
        "What are the examination rules?",
        "What is the fee refund policy?",
        "How can I apply for scholarships?"
    ]

    for question in suggestions:
        if st.button(question, use_container_width=True):
            st.session_state.selected_question = question

    st.markdown("---")

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.selected_question = ""
        st.rerun()

    st.caption("Student Policy AI Assistant | Version 1.0")


# Main interface
st.markdown(
    '<p class="title">🎓 Student Policy AI Assistant</p>',
    unsafe_allow_html=True
)

st.markdown(
    '<p class="subtitle">Your AI assistant for understanding academic rules, '
    'student policies and institutional guidelines.</p>',
    unsafe_allow_html=True
)

st.markdown("---")


# Welcome message
if len(st.session_state.messages) == 0:

    st.info(
        "👋 Welcome! Ask me anything about student policies. "
        "I will find the relevant information from the Student Policy Handbook."
    )


# Display previous chat messages
for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

        # Display retrieved sources
        if message["role"] == "assistant" and message.get("sources"):

            with st.expander("📄 View Retrieved Sources"):

                for i, doc in enumerate(message["sources"]):

                    page = doc.metadata.get("page", 0) + 1

                    st.markdown(f"**Source {i+1} – Page {page}**")

                    st.write(doc.page_content)

                    st.markdown("---")


# Chat input
user_question = st.chat_input(
    "Ask your student policy question..."
)


# Handle suggested questions
if st.session_state.get("selected_question"):

    user_question = st.session_state.selected_question

    st.session_state.selected_question = ""


# Generate response
if user_question and backend_ready:

    # Store user question
    st.session_state.messages.append({
        "role": "user",
        "content": user_question
    })

    # Display user message
    with st.chat_message("user"):
        st.markdown(user_question)

    # Generate AI response
    with st.chat_message("assistant"):

        with st.spinner("Searching student policy documents..."):

            try:

                response, documents = get_answer(
                    user_question,
                    retriever,
                    llm
                )

                st.markdown(response)

                # Show sources
                with st.expander("📄 View Retrieved Sources"):

                    for i, doc in enumerate(documents):

                        page = doc.metadata.get("page", 0) + 1

                        st.markdown(
                            f"**Source {i+1} – Page {page}**"
                        )

                        st.write(doc.page_content)

                        st.markdown("---")

                # Save assistant response
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response,
                    "sources": documents
                })

            except Exception as e:

                error_message = f"Sorry, something went wrong: {e}"

                st.error(error_message)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_message
                })

elif user_question and not backend_ready:

    st.error("Chatbot backend is not available. Check your configuration.")
