import streamlit as st

def connected(f):
    if 'connected' not in st.session_state or not st.session_state.connected:
        st.write('Not connected go to Connection panel : ')
        st.page_link("app.py", label="Connection", icon="🔗")
        st.stop()
    else:
        return f
    

def wideScreen(f):
    st.set_page_config(layout="wide")
    return f