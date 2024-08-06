import streamlit as st
import os
from src.decorators import connected
from nifiTalk.src.nifiAPI import nifiAPI
from nifiTalk.src.color import *
import json
import pandas as pd
import re
UUID_PATTERN = re.compile(r'^[\da-f]{8}-([\da-f]{4}-){3}[\da-f]{12}$', re.IGNORECASE)

@st.cache_data
def verifyCSV(file):
    return True

@st.cache_data
def verifyJSON(file):
    return True

@connected
def coloring(nifi : nifiAPI, defaultColorPath = 'app/data/colorPatern.json'):
    st.write('# Painting your Nifi')
    
    with open(defaultColorPath) as f:
        colorPatern = json.load(f)
    
    colorUpload = st.file_uploader(
        label = f'Color Patern (par default : {os.getcwd()}{defaultColorPath.replace('/','\\')})',
        type = ['.json', '.csv']
        )
    
    if colorUpload:
        if colorUpload.name[-4:] == '.csv':
            try:
                colorPatern = pd.read_csv(colorUpload).to_dict('records')
                keys = [k for k in colorPatern[0].keys()]
                if len(keys) != 2:
                    raise Exception(ValueError, 'ncol != 2')
                colorPatern = {r[keys[0]] : r[keys[1]]  for r in colorPatern}
            except ValueError as e:
                st.error(f'erreur de lecture {e}')
                st.stop()
            st.success(f'read csv File : {colorUpload.name}')
        if colorUpload.name[-5:] == '.json':
            try:
                colorPatern = json.load(f)
            except ValueError as e:
                st.error(f'erreur de lecture {e}')
                st.stop()
            st.success(f'read json File : {colorUpload.name}')

    with st.form('coloring'):
        Processgroup = st.text_input(
            label= 'Process group id',
            placeholder = 'Process group à peindre',
            value = st.session_state.root)
        recursive = st.checkbox('Recursive', value = False)
        jsonPaternTable = st.data_editor(
            colorPatern,
            num_rows="dynamic",
            column_config={
                "index" : st.column_config.TextColumn(
                    "Processor Identifier"
                ),
                "value" : st.column_config.TextColumn(
                    "Color",
                    help="Hexadecimal color",
                    validate="^#[0-9a-fA-F]{6}$"
                ),
            }
        )
        submit = st.form_submit_button(label="Submit")
    
    if submit:
        if not re.match(UUID_PATTERN, Processgroup):
            st.error('Process group uuid is not valid')
            st.stop()
        try:
            c = APIcolorProcessGroup(nifiAPI = nifi,
                                processGroupId = Processgroup,
                                colorPatern = jsonPaternTable,
                                recursive = recursive,
                                results=True)
        except:
            st.error(f'Error while painting process group : {Processgroup}', icon="🚨")
            st.stop()
        st.success(f'Painting process group : {Processgroup}', icon="✅")
        st.dataframe(pd.DataFrame.from_dict(c, columns=['Processor Identifier','Colored?', 'Reason'], orient='index'), hide_index=True)

coloring(st.session_state.nifi)
