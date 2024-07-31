import src.nifiAPI as nif
import src.color as col
import src.monitoring as mon
import json
from importlib import reload
import streamlit as st
from src.app_func import *

nifi = nif.nifiAPI_userAuth(host="https://localhost:8443/", username="drimer", password="passpasspass", client='faf03396-018e-1000-2d05-5282f7c6b7fe')

st.write("# Welcome ! 👋")

Processgroup = st.text_input('Process group id', value = "a7aa3600-0186-1000-12c2-01276dc54af5")

if Processgroup:
    st.write(nifi.getProcessGroupInfosInPG(Processgroup))
    processorInfos = nifi.getProcessorsInfosInPG(Processgroup, recursive=True)
    createHierachicalAgGrid(
        pd.DataFrame(createListForAgGrid(processorInfos))
    )

