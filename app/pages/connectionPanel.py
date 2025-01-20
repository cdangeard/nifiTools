import nifiTalk.src.nifiAPI as nif
from nifiTalk.src.monitoring import Monitor
import uuid
import streamlit as st
from time import sleep
@st.cache_data
def getRandomClientUUID():
    return uuid.uuid4()

def connectionUserAuth(host : str, username : str,
                       password :str, client : uuid) -> None:
    try:
        my_bar = st.progress(0) 
        nifi = nif.nifiAPI_userAuth(host=host, username=username,
                                    password=password, client=client)
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


def connectionCertAuth(host : str, 
                       pemPath : str, certPath : str, keyPath : str,  
                       client: uuid) -> None:
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
            client = st.text_input('client', value = getRandomClientUUID())
            buttonConnectUserAuth = st.button('Connect')
            if buttonConnectUserAuth:
                connectionUserAuth(host, username, password, client)
        elif connectionType == "Cert Auth":
            pemPath = st.text_input('pemPath', value = '../certNifiDev/ca_SSL_chain_DSICentrale.pem')
            certPath = st.text_input('certPath', value = '../certNifiDev/www.nifi-cluster.vy9.dev.net.intra.laposte.fr_CER.pem')
            keyPath = st.text_input('keyPath', value = '../certNifiDev/www.nifi-cluster.vy9.dev.net.intra.laposte.fr_KEY.pem')
            client = st.text_input('client', value = getRandomClientUUID())
            buttonConnectCertAuth = st.button('Connect')
            if buttonConnectCertAuth:
                connectionCertAuth(host, pemPath, certPath, keyPath, client)

connection()