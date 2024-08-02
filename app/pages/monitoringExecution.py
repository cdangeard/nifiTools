import streamlit as st
import plotly.express as px
import re
import pandas as pd
import numpy as np

from nifiTalk.src.nifiAPI import nifiAPI
from src.aagridHierachical import *
from src.decorators import wideScreen

UUID_PATTERN = re.compile(r'^[\da-f]{8}-([\da-f]{4}-){3}[\da-f]{12}$', re.IGNORECASE)

@wideScreen
def monitoring(nifi : nifiAPI):
    st.sidebar.header("Monitoring : ")
    st.title('Monitoring Nifi')
    #Input process group
    Processgroup = st.text_input('Process group id', value = st.session_state.root)
    st.sidebar.text(
        f'{Processgroup[:5]}..{Processgroup[-5:]}' if Processgroup is not None else '', )
    #Input rate
    Rate = st.number_input('Rate', value = 1, step = 1, max_value = 10, format= '%d')
    #Input max duration
    MaxDuration = st.number_input('Max duration', 
                                  value = 5, step = 1, min_value = 1, 
                                  format='%d')
    StarterProcessGroup = st.text_input('Starter process group (optional)', value = '', )
    #Button
    if st.button('Start'):
        #Verify inputs
        if Processgroup == '':
            st.error('Process group id cannot be empty')
        elif Rate == '':
            st.error('Rate cannot be empty')
        elif MaxDuration == '':
            st.error('Max duration cannot be empty')
        # test if Pg id is valid uuid
        elif not UUID_PATTERN.match(Processgroup):
            st.error('Process group uuid is not valid')
        elif StarterProcessGroup != '' and not UUID_PATTERN.match(StarterProcessGroup):
            st.error('Starter process group uuid is not valid')
        else:
            starter = StarterProcessGroup if StarterProcessGroup else 'auto'
            my_bar = st.progress(0)
            if starter == 'auto':
                starter = st.session_state.nifi.findSourceProcessor(processGroupId=Processgroup)
                if len(starter) == 1:
                    starter = starter[0]
                    st.success(f'Starter Processor found : {starter}')
                    my_bar.progress(20)
                else:
                    st.error('No starter processor found')
                    my_bar.progress(100)
                    st.stop()
            processorInfos = st.session_state.nifi.getProcessorsInfos(Processgroup, recursive=True)
            createHierachicalAgGrid(
                pd.DataFrame(createListForAgGrid(processorInfos))
            )
            #Loading bar
            pgInside = st.session_state.nifi.getProcessGroupList(processGroupId=Processgroup, 
                                                                   recursive=True)
            pgInside.append(Processgroup)
            dataDict = st.session_state.monitor.monitor_PG(Processgroup,
                                                           rate = float(Rate), 
                                                           maxDuration = int(MaxDuration),
                                                           start = starter)
            my_bar.progress(80)
            #Convert dict to dataframe
            df = pd.DataFrame.from_dict(dataDict, orient='index')

            df_active = df[df[Processgroup] > 0]

            my_bar.progress(100)
            
            #Display execution time
            startTime = df_active['timestamp'].min()
            maxTime = df_active['timestamp'].max()
            executionTime = maxTime - startTime

            st.title('Raw Results')
            st.write(f"<h3>execution time :<b> {(executionTime):.2f}</b> seconds</h3>",
                      unsafe_allow_html=True)
            #Display raw results
            st.dataframe(df)
            #Graph timeseries
            pgList = list(df.columns)
            pgList.remove('timestamp')
            df_active['timeSinceStart'] = df_active['timestamp'] - df_active['timestamp'].iloc[0]
            fig = px.line(df_active, x="timeSinceStart", 
                          y=pgList, 
                          title='Queue Count by connections',
                          labels={'timeSinceStart':'time (s)', 
                                  'variable':'component', 
                                  'value':'queue count'}, 
                          markers=True)
            st.plotly_chart(fig)
            
            #Evaluate mean loaded rate for each queue
            s = (df_active[pgList].astype(int) > 0).mean(axis=0)
            df_mean = pd.DataFrame(
                {
                    'component_Id' : s.index,
                    'loaded_prop' : s.values*100,
                    'isPG' : [True if pg in pgInside else False for pg in s.index],
                    'serie' : [np.array(df_active[pg]) for pg in pgList],
                }
            )
            st.dataframe(
                df_mean,#.style.highlight_max(axis=0, subset = ['loaded_prop']),#interaction problem with column_config
                column_config={
                    'component_Id' : st.column_config.TextColumn('component_Id'),
                    'loaded_prop' : st.column_config.NumberColumn(
                        'Mean loaded Time', 
                        format="%.0f %%", 
                        help="Proportion of time where the queue is not empty"),
                    'isPG' : st.column_config.TextColumn('isPG'),
                    'serie' : st.column_config.LineChartColumn('serie'),
                },
                hide_index=True
            )

monitoring(st.session_state.nifi)