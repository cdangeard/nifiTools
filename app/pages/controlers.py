import streamlit as st
import re
import pandas as pd
from src.app_func import *

UUID_PATTERN = re.compile(r'^[\da-f]{8}-([\da-f]{4}-){3}[\da-f]{12}$', re.IGNORECASE)

st.set_page_config(page_title="Controlers", layout="wide")

st.title('Controlers')

if 'connected' not in st.session_state or not st.session_state.connected:
    st.write('Not connected go to Connection panel : ')
    st.page_link("app.py", label="Connection", icon="🔗")
else:
    with st.form("Controlers"):
        Processgroup = st.text_input(label= 'Process group id',
                                        placeholder = 'Enter process group id',
                                        value = st.session_state.root)
        submit = st.form_submit_button(label="Submit")
    
    if submit:
        if re.match(UUID_PATTERN, Processgroup):
            st.spinner("Loading...")
            try:
                dic = st.session_state.nifi.getControlerServices(Processgroup, recursive = True)
                st.success(f' {len(dic.keys())} Controlers loaded')
                pg = st.session_state.nifi.getProcessGroupInfos(Processgroup, recursive=True)
                dic.update(pg)
                dfControlers = pd.DataFrame(createListForAgGrid(dic))
                createHierachicalAgGrid(dfControlers)
            except Exception as e:
                st.error('Error : %s' % e, icon="🚨")
        else: 
            st.error('Process group uuid is not valid')