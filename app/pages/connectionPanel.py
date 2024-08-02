import nifiTalk.src.nifiAPI as nif
from nifiTalk.src.monitoring import Monitor
import uuid
import streamlit as st
from time import sleep

def connection():
    st.write('# Connection panel')
    if 'connected' in st.session_state:
        st.write('You are connected to %snifi' % (st.session_state.host))
        buttonDisconnect = st.button('Disconnect')
        if buttonDisconnect:
            del st.session_state.connected
            del st.session_state.nifi
            del st.session_state.monitor
            del st.session_state.host
            if 'username' in st.session_state:
                del st.session_state.username
            st.success('Disconnected!')
            sleep(0.5)
            st.rerun()
    else:
        connectionType = st.radio("Connection type", ["User Auth", "Cert Auth"])
        host = st.text_input('host', value = 'https://localhost:8443/')
        if connectionType == "User Auth":
            username = st.text_input('username', value = 'drimer')
            password = st.text_input('password', value = 'passpasspass', type="password")
            client = st.text_input('client', value = uuid.uuid4())
            buttonConnectUserAuth = st.button('Connect')
            if buttonConnectUserAuth:
                try:
                    my_bar = st.progress(0) 
                    nifi = nif.nifiAPI_userAuth(host=host, username=username, password=password,
                                                client=client)
                    my_bar.progress(80)
                    mon = Monitor(nifi)
                    st.session_state.nifi = nifi
                    st.session_state.monitor = mon
                    st.session_state.connected = True
                    st.session_state.host = host
                    st.session_state.username = username
                    st.session_state.root = nifi.getRootProcessGroup()
                    my_bar.progress(100)
                except Exception as e:
                    st.error('Connection failed with error : %s' % e, icon="🚨")
                    st.stop()
                st.success("Logged in!")
                sleep(1)
                st.switch_page("pages/home.py")
        elif connectionType == "Cert Auth":
            pemPath = st.text_input('pemPath', value = 'pemPath')
            certPath = st.text_input('certPath', value = 'certPath')
            keyPath = st.text_input('keyPath', value = 'keyPath')
            client = st.text_input('client', value = uuid.uuid4())
            buttonConnectCertAuth = st.button('Connect')
            if buttonConnectCertAuth:
                try:
                    my_bar = st.progress(0) 
                    nifi = nif.nifiAPI_certAuth(host=host, pemPath=pemPath, certPath=certPath,
                                                keyPath=keyPath, client=client)
                    my_bar.progress(80)
                    mon = Monitor(nifi)
                    st.session_state.nifi = nifi
                    st.session_state.monitor = mon
                    st.session_state.connected = True
                    st.session_state.host = host
                    st.session_state.root = nifi.getRootProcessGroup()
                    my_bar.progress(100)
                except Exception as e:
                    st.error('Connection failed with error : %s' % e, icon="🚨")
                    st.stop()
                st.success("Logged in!")
                sleep(0.5)
                st.switch_page("pages/home.py")

connection()