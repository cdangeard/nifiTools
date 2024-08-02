import pandas as pd
import pandas as pd
from st_aggrid import JsCode, AgGrid, GridOptionsBuilder, GridUpdateMode

def createHierachicalDf(dictIn : dict,  parentCol : str = 'parentGroupId',
                        linkChar : bool = True, racine = None, depth : int = 0):
    """
    Create a hierachical dataframe from processgroup info

    Parameters
    ----------
    dictIn : dict
        dict of process group info
    parentCol : str, optional
        column name of parent process group, by default 'parentGroupId'
    linkChar : bool, optional
        if True, add a character to the dataframe, by default True
    racine : str, optional
        root process group, by default None
    depth : int, optional
        depth of the process group, by default 0
    """
    if racine is not None:
        roots = list([k for k, v in dictIn.items() if parentCol in v.keys() and 
                     v[parentCol] == racine])
    else:
        roots = list([k for k, v in dictIn.items() if parentCol not in v.keys() or
                      v[parentCol] not in dictIn.keys()])
    dfOut = pd.DataFrame()
    for root in roots:
        dfRoot = dictIn[root]
        dfRoot['depth'], dfRoot['id'] = depth, root
        #a fini
        if linkChar:
            if root == roots[-1]:
                dfRoot = {f' {depth}' : '└─'} | dfRoot
            else:
                dfRoot = {f' {depth}' : '├─'} | dfRoot
        dfOut = pd.concat([
            dfOut,
            pd.DataFrame([dfRoot]),
            createHierachicalDf(dictIn, parentCol = parentCol, linkChar= linkChar,
                                racine = root,depth = depth + 1)
        ])
    return dfOut.sort_index(axis=1).fillna('')

def createListForAgGrid(dictIn : dict, parentField : str = 'parentGroupId',
                       root = None, orgHierarchy = '') -> list:
    """
    Create a dictionary for aggrid

    Parameters
    ----------
    dictIn : dict
        dict of process group info
    parentField : str, optional
        column name of parent process group, by default 'parentGroupId'
    """
    listOut = []
    if root is None:
        leafs = list([k for k, v in dictIn.items() 
                    if "parentGroupId" not in v.keys() or
                    v['parentGroupId'] not in dictIn.keys()])
    else:
        leafs = list([k for k, v in dictIn.items() 
                      if "parentGroupId" in v.keys() 
                      and v['parentGroupId'] == root])
    for leaf in leafs:
        dicOut = dictIn[leaf]
        dicOut['id'] = leaf
        if orgHierarchy == '':
            dicOut['orgHierarchy'] = leaf
        else:
            dicOut['orgHierarchy'] = orgHierarchy + '/' + leaf
        listOut.append(dicOut)
        listOut.extend(createListForAgGrid(dictIn = dictIn, 
                                          parentField = parentField, 
                                          root = leaf,
                                          orgHierarchy = dicOut['orgHierarchy']))
    return listOut      
    
def createHierachicalAgGrid(df):
    """
    from : https://discuss.streamlit.io/t/ag-grid-on-tree-structured-data/26808/5
    """
    gb = GridOptionsBuilder.from_dataframe(df)
    urlRenderer = JsCode("""
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
    gridOptions = gb.build()
    #hide columns that are not needed
    gridOptions["columnDefs"]= [{"field" : col} for col in df.columns]
    for col in gridOptions["columnDefs"]:
        if col["field"] in ["id", "orgHierarchy", "parentGroupId"]:
            col["hide"] = True
        if col["field"] == "name":
            col["cellRenderer"] = urlRenderer
    gridOptions["defaultColDef"]={
      "flex": 1,
    },
    gridOptions["autoGroupColumnDef"]= {
        "headerName": 'Organisation Hierarchy',
        "minWidth": 300,
        "cellRendererParams": {
        "suppressCount": True,
        },
    },
    gridOptions["treeData"]=True
    gridOptions["animateRows"]=True
    gridOptions["groupDefaultExpanded"]= -1
    gridOptions["getDataPath"]=JsCode(""" function(data){
        return data.orgHierarchy.split("/");
    }""").js_code

    return AgGrid(df,
                  gridOptions=gridOptions,
                  height=500,
                  allow_unsafe_jscode=True,
                  enable_enterprise_modules=True,
                  filter=True,
                  update_mode=GridUpdateMode.SELECTION_CHANGED,
                  theme="material",
                  tree_data=True
                  )