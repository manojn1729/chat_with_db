import streamlit as st
import openai
import pyodbc
import os
import pandas as pd
from dotenv import load_dotenv
from myfunctions import *

load_dotenv()

openai.api_key=os.getenv('key')

with st.sidebar:
    if x:=st.text_input('Table name',placeholder='Type table name'):
        st.session_state['tableName']=x

if "messages" not in st.session_state:
     st.session_state['messages'] = []

if "tableName" not in st.session_state:
    st.session_state['tableName']=None

if "cursur" not in st.session_state:
    st.session_state['cnxn'], st.session_state['cursor']=setup_cursor() 

for message in st.session_state.messages:
    x=user_chat (message['content']) if message['role']=='user' else assistant_chat (message['content'])

prompt=st.chat_input (placeholder='ask to query on RDBMS') 
if prompt:
    if st.session_state['tableName']:
        user_chat (f' {prompt}')
        response=openai.Completion.create(
        model="text-davinci-003",
        prompt="generate single Mysql query for the Givn DDL  "+generate_ddl(st.session_state['tableName'],st.session_state['cnxn'])+"/t"+prompt,
        max_tokens=250,
        temperature=0.3
        )

        assistant_chat(response.choices[0].text.replace('\n', ' ')) 

        st.dataframe(sql_excqute (response.choices[0].text.replace('\n', ' '), st.session_state['cnxn']),hide_index=True,use_container_width=True)

        st.session_state.messages.append({'role': 'user', 'content': prompt}) 
        st.session_state.messages.append({'role': 'ai', 'content': response.choices[0].text.replace('\n', ' ')})
    else:
        st.warning('please enter the table name')