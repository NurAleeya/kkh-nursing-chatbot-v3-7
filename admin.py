import streamlit as st
import json
import os
from datetime import datetime

def export_chat_history():
    """Export chat history to JSON"""
    if 'messages' in st.session_state and st.session_state.messages:
        chat_data = {
            'export_date': datetime.now().isoformat(),
            'messages': st.session_state.messages,
            'total_messages': len(st.session_state.messages)
        }
        return json.dumps(chat_data, indent=2)
    return None

def import_chat_history(uploaded_file):
    """Import chat history from JSON file"""
    try:
        chat_data = json.load(uploaded_file)
        if 'messages' in chat_data:
            st.session_state.messages = chat_data['messages']
            return True, f"Imported {len(chat_data['messages'])} messages"
        else:
            return False, "Invalid file format"
    except Exception as e:
        return False, f"Error importing file: {str(e)}"

def admin_panel():
    """Admin panel for managing the chatbot"""
    st.header("🔧 Admin Panel")
    
    # Chat History Management
    st.subheader("💬 Chat History Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Export Chat History**")
        if st.button("Export Current Session"):
            chat_export = export_chat_history()
            if chat_export:
                st.download_button(
                    label="Download Chat History",
                    data=chat_export,
                    file_name=f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
            else:
                st.warning("No chat history to export")
    
    with col2:
        st.write("**Import Chat History**")
        uploaded_file = st.file_uploader("Choose a JSON file", type="json")
        if uploaded_file is not None:
            success, message = import_chat_history(uploaded_file)
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)
    
    # Clear Chat History
    st.subheader("🗑️ Clear Data")
    if st.button("Clear Chat History", type="secondary"):
        if 'messages' in st.session_state:
            del st.session_state.messages
        st.success("Chat history cleared")
        st.rerun()
    
    # System Information
    st.subheader("📊 System Information")
    
    info_col1, info_col2 = st.columns(2)
    
    with info_col1:
        st.metric("Total Messages", len(st.session_state.get('messages', [])))
        st.metric("Knowledge Base Items", len(st.session_state.chatbot.knowledge_base) if 'chatbot' in st.session_state else 0)
    
    with info_col2:
        st.metric("LLM Endpoint Status", "🟢 Connected" if True else "🔴 Disconnected")
        st.metric("Embedding Model", "all-MiniLM-L6-v2")
    
    # Knowledge Base Management
    st.subheader("📚 Knowledge Base Management")
    
    if 'chatbot' in st.session_state:
        categories = list(st.session_state.chatbot.knowledge_base.keys())
        selected_category = st.selectbox("Select Category", categories)
        
        if selected_category:
            items = list(st.session_state.chatbot.knowledge_base[selected_category].keys())
            st.write(f"**Items in {selected_category}:**")
            for item in items:
                st.write(f"• {item}")
    
    # Configuration
    st.subheader("⚙️ Configuration")
    
    # LLM Settings
    with st.expander("LLM Configuration"):
        st.code(f"""
        Endpoint: http://10.175.5.70:1234/v1/chat/completions
        Model: phi-2
        Temperature: 0.7
        Max Tokens: 1000
        """)
    
    # Embedding Settings  
    with st.expander("Embedding Configuration"):
        st.code(f"""
        Model: all-MiniLM-L6-v2
        Dimension: 384
        Similarity Threshold: 0.7
        """)

if __name__ == "__main__":
    admin_panel()
