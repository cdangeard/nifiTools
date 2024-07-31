import streamlit as st
from src.app_func import *


if 'connected' not in st.session_state or not st.session_state.connected:
    st.write('Not connected go to Connection panel : ')
    st.page_link("app.py", label="Connection", icon="🔗")
    st.stop()


st.title('Explore')

pgs = st.session_state.nifi.getProcessGroupInfos(st.session_state.root, recursive=False)
st.write(pgs)
df = pd.DataFrame(createListForAgGrid(pgs))

gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_column(
    "name", "Name",
    cellRenderer=JsCode("""
        class UrlCellRenderer {
          init(params) {
            this.eGui = document.createElement('a');
            this.eGui.innerText = params.value;
            this.eGui.setAttribute('href', 'https://localhost:8443/nifi/?processGroupId=' + params.data.id);
            this.eGui.setAttribute('style', "text-decoration:none");
            this.eGui.setAttribute('target', "_blank");
          }
          getGui() {
            return this.eGui;
          }
        }
    """)
)
gridOptions = gb.build()
st.write(gridOptions)
AgGrid( df,
        gridOptions=gridOptions,
        height=500,
        allow_unsafe_jscode=True,
        enable_enterprise_modules=True,
        filter=True,
        update_mode=GridUpdateMode.SELECTION_CHANGED | GridUpdateMode.VALUE_CHANGED,
        theme="material",
        tree_data=True
        )
