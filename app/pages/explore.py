import streamlit as st
from src.aagridHierachical import *
from src.decorators import wideScreen
from nifiTalk.src.nifiAPI import nifiAPI
from src.cacheData import getProcessGroupsInfos

@wideScreen
def explore(nifi : nifiAPI):
    st.title('Explore')
    pgs = nifi.getProcessGroupsInfos(st.session_state.root, recursive=True)
    #st.write(pgs)
    createHierachicalAgGrid(pd.DataFrame(createListForAgGrid(pgs)))


explore(st.session_state.nifi)