import streamlit as st
from nifiTalk.src.nifiAPI import nifiAPI


def callAPI(nifi : nifiAPI):
    typeRequest = st.radio('Type of Request', options=['GET', 'PUT'])
    endpoint = st.text_input('Endpoint', value='/flow/about')
    content = st.text_area('Content to push')
    submit = st.button('submit')

    if submit:
        res = nifi.callAPI(endpoint=endpoint, type=typeRequest, payload=content)
        st.write(res)

callAPI(st.session_state.nifi)
