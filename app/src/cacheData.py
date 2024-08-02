import streamlit as st
from nifiTalk.src.nifiAPI import nifiAPI

@st.cache_data
def getProcessGroupsInfos(nifi : nifiAPI, pg : str, recursive : bool):
    return nifi.getProcessGroupsInfos(processGroupId=pg, recursive=recursive)


