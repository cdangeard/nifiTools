import streamlit as st
import re
import pandas as pd

from nifiTalk.src.nifiAPI import nifiAPI
from src.aagridHierachical import *
from src.decorators import wideScreen

UUID_PATTERN = re.compile(r'^[\da-f]{8}-([\da-f]{4}-){3}[\da-f]{12}$', re.IGNORECASE)

@wideScreen
def controlers(nifi : nifiAPI):
    st.title('Controlers')
    with st.form("Controlers"):
        Processgroup = st.text_input(label= 'Process group id',
                                        placeholder = 'Enter process group id',
                                        value = st.session_state.root)
        submit = st.form_submit_button(label="Submit")
    
    if submit:
        if re.match(UUID_PATTERN, Processgroup):
            st.spinner("Loading...")
            try:
                dic = nifi.getControlerServices(Processgroup, recursive = True)
                st.success(f' {len(dic.keys())} Controlers loaded')
                pg = nifi.getProcessGroupsInfos(Processgroup, recursive=True)
                dic.update(pg)
                dfControlers = pd.DataFrame(createListForAgGrid(dic))
                createHierachicalAgGrid(dfControlers)
            except Exception as e:
                st.error('Error : %s' % e, icon="🚨")
        else: 
            st.error('Process group uuid is not valid')

controlers(st.session_state.nifi)