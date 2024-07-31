import streamlit as st

if st.session_state.get('connected', False):
    pages = [
        st.Page("pages/home.py", title="Home", icon="🏠"),
        st.Page("pages/explore.py", title="Explore", icon="🕵️‍♀️"),
        st.Page("pages/monitoringExecution.py", title="Monitor Execution", icon="📈"),
        st.Page("pages/controlers.py", title="Controlers Services", icon="🛠️"),   
        st.Page("pages/connectionPanel.py", title="Déconnection", icon="🔗"),
    ]
else:
    pages = [
        st.Page("pages/home.py", title="Home", icon="🏠"),
        st.Page("pages/connectionPanel.py", title="Connection", icon="🔗"),
    ]
page = st.navigation(pages)

page.run()
