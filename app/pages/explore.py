import streamlit as st
from src.app_func import *


if 'connected' not in st.session_state or not st.session_state.connected:
    st.write('Not connected go to Connection panel : ')
    st.page_link("app.py", label="Connection", icon="🔗")
    st.stop()


st.title('Explore')

pgs = st.session_state.nifi.getProcessGroupInfos(st.session_state.root, recursive=True)
#st.write(pgs)
aggrid = createHierachicalAgGrid(pd.DataFrame(createListForAgGrid(pgs)))