import streamlit as st


st.write("# Welcome ! 👋")
if 'connected' in st.session_state:
    st.write('You are connected to %snifi' % (st.session_state.host))
    st.write('## Home')
    st.write('## Monitor Execution')
    st.write('## Controlers')
else:
    st.write('Not connected go to Connection panel : ')
    st.page_link("pages/connectionPanel.py", label="Connection", icon="🔗")

