import streamlit as st
import openai
import pyodbc
import os
import pandas as pd
from myfunctions import *
import time



if 'status' not in st.session_state:
    st.session_state['status']={
        'db':False,
        'ai':False
    }

if "messages" not in st.session_state:
     st.session_state['messages'] = []

if "tableNames" not in st.session_state:
    st.session_state['tableNames']=[]


if "tables" not in st.session_state:
    st.session_state['tables']=[]

for message in st.session_state.messages:
    x=user_chat (message['content']) if message['role']=='user' else assistant_chat (message['content'])


with st.sidebar:

    if x:=st.multiselect('Select tables',options=st.session_state['tables']):
        st.session_state['tableNames']=x

    with st.form('config'):

        DRIVER=st.selectbox('Server Type',['MYSQL'])
        SERVER=st.text_input('Server')
        DATABASE=st.text_input('DataBase')
        UID=st.text_input('User Name')
        PASSWORD=st.text_input('Password',type='password')
        key=st.text_input('API key',type='password')
        if DRIVER=='MYSQL':
            DRIVER='MySQL ODBC 8.0 ANSI Driver'
        if submit:=st.form_submit_button('submit'):
            st.session_state['setup']={
            'DRIVER':DRIVER,
            'SERVER':SERVER,
            'UID':UID,
            'DATABASE':DATABASE,
            'PASSWORD':PASSWORD,
            'key':key
                    }

            openai.api_key=st.session_state['setup']['key']

            if not check_key():
                st.session_state['status']['ai']=False
            else:
                st.session_state['status']['ai']=True
    
            try:
                connect_db()
            except:
                st.session_state['status']['db']=False
            else:
                st.session_state['status']['db']=True
                st.session_state['tables']=list_tables()
                st.experimental_rerun()

        if st.session_state['status']['db']:
            st.success('connected db')
        else:
            st.error('provide valid db credentials')
        
        if st.session_state['status']['ai']:
            st.success('valid API key')
        else:
            st.error('provide valid api key')

prompt=st.chat_input (placeholder='ask to query on RDBMS') 

if prompt:
    if check_status():
        if st.session_state['tableNames']:
            try:
                user_chat(prompt)
                result=chat_openai(prompt)
                st.session_state.messages.append({'role': 'user', 'content': prompt}) 
                st.session_state.messages.append({'role': 'assistant', 'content':result})
                if query:=get_code(result):
                    try:
                        st.dataframe(sql_excqute (query.replace('\n', ' ')),hide_index=True,use_container_width=True)
                    except TypeError:
                        st.success('done')
                    st.session_state['tables']=list_tables()
            except Exception as e:
                st.error(e)
        else:
            st.warning('please select one or more table')
    else:
        st.error('please provide valide credentials')