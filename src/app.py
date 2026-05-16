import streamlit as st
from rag import ask


# config
st.set_page_config(
    page_title="Wuduh — UAE Labor Law Assistant",
    page_icon="⚖️",
    layout="centered"
)

# Header
st.title("⚖️ Wuduh | وضوح")
st.caption("Your UAE Labor Law Assistant — Ask questions about UAE labor law in plain English.")

# Disclaimer
st.warning("""**Legal Disclaimer:** This tool provides information based on UAE labor law texts 
and is not a substitute for professional legal advice. 
Always consult a qualified legal professional for your specific situation.""")

# Initialize histories 
if "messages" not in st.session_state:
    st.session_state.messages = []       # for UI display

if "rag_history" not in st.session_state:
    st.session_state.rag_history = []    # for GPT-4o memory

# Display chat history 
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
        if message["role"] == "assistant" and "sources" in message:
            with st.expander("📄 Sources"):
                for source in message["sources"]:
                    meta = source["metadata"]
                    st.write(f"Article {meta['article_number']} — {meta['law_name']}")


# Chat input 
query = st.chat_input("Ask a question about UAE labor law...")

if query:
    # Display and save user message
    with st.chat_message("user"):
        st.write(query)
    st.session_state.messages.append({"role": "user", "content": query})

    # Call RAG pipeline
    with st.chat_message("assistant"):
        with st.spinner("Looking up UAE labor law..."):
            result = ask(query, st.session_state.rag_history)
        
        st.write(result["answer"])
        
        # Add this block
        with st.expander("📄 Sources"):
            for source in result["sources"]:
                meta = source["metadata"]
                st.write(f"Article {meta['article_number']} — {meta['law_name']}")
        
        st.session_state.rag_history = result["history"]
    
    # Save assistant answer to display history
    st.session_state.messages.append({
    "role": "assistant", 
    "content": result["answer"],
    "sources": result["sources"]
    })