import streamlit as st 
import re
import pyodbc
import os
import pandas as pd
import openai
from dotenv import load_dotenv
load_dotenv()

def user_chat (message):
    with st.chat_message("user", avatar='👶'):
        st.write(message)

def assistant_chat (message):
    with st.chat_message("assistant", avatar='🤖'):
        st.write(message)

# def setup():
#     st.session_state['setup']={
#         'DRIVER':os.getenv('DRIVER'),
#         'SERVER':os.getenv('SERVER'),
#         'UID':os.getenv('UID'),
#         'DATABASE':os.getenv('DATABASE'),
#         'PASSWORD':os.getenv('PASSWORD'),
#         'key':os.getenv('key')
#     }

def setup_cursor():
    cnxn = pyodbc.connect("DRIVER={{{0}}}; SERVER={1};DATABASE={2}; UID={3}; PASSWORD={4};TransactionIsolationLevel=READ UNCOMMITTED;".format(
       st.session_state['setup']['DRIVER'],
       st.session_state['setup']['SERVER'],
       st.session_state['setup']['DATABASE'],
       st.session_state['setup']['UID'],
       st.session_state['setup']['PASSWORD']))
    return cnxn,cnxn.cursor()

def sql_excqute (query):
    return pd.read_sql (query,st.session_state['cnxn'])


def chat_openai(prompt):
  
    full_response=''
    with st.chat_message("assistant", avatar='🤖'):
        message=[{"role":"system","content":"Given the following SQL tables, your job is to write MySQL queries given by a user’s request wrap inside ```sql.\n\n"+generate_ddl(st.session_state['tableNames'])}]
        message+=message+formate_sql(st.session_state.messages[-4:]).copy()+[{'role': 'user', 'content':prompt}]
        message_placeholder = st.empty()
        full_response = ""
        for i in openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=message,
        temperature=0,
        max_tokens=1024,
        top_p=1,
        n=1,
        stream=True
    ):

            full_response += i.choices[0].delta.get("content", "")
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
    
    return full_response
    

def generate_ddl(table_names):
    response=''
    for table in table_names:
        df = sql_excqute(f"describe {table}")
        columns = [f"{row['Field']} {row['Type']}" for _, row in df.iterrows()]
        primary_keys = [row['Field'] for _, row in df.iterrows() if row['Key'] == 'PRI']
        primary_key_constraint = f", primary key ({','.join(primary_keys)})" if primary_keys else ''
        df=sql_excqute(f'''SELECT 
        TABLE_NAME,COLUMN_NAME, REFERENCED_TABLE_NAME,REFERENCED_COLUMN_NAME
        FROM
        INFORMATION_SCHEMA.KEY_COLUMN_USAGE
        WHERE
        REFERENCED_TABLE_SCHEMA = 'sakila' AND
        TABLE_NAME = '{table}';''')
        forigin_key=[f"FOREIGN KEY ({row['COLUMN_NAME']}) REFERENCES {row['REFERENCED_TABLE_NAME']}({row['REFERENCED_COLUMN_NAME']})" for _,row in df.iterrows()]
        forigin_key_constraint=f", {','.join(forigin_key)}" if forigin_key else ''
        query=f"CREATE TABLE {table} ({', '.join(columns)}{primary_key_constraint}{forigin_key_constraint})\n\n"
        response+=query
    
    return response


def get_code(message):
    response=[]
    pattern='```sql([\s\S]*?)```'
    match=re.findall(pattern,message)
    if len(match)!=0: return match[0] 

def formate_sql(messages):
    pattern='```sql([\s\S]*?)```'
    for i,message in enumerate(messages):
        if message['role']!='user':
            temp=re.findall(pattern,message['content'])
            if len(temp)!=0:
                tstring=''
                for templ1 in temp:
                    tstring=tstring+'```sql'+templ1+'```'+'\n'
                messages[i]['content']=tstring
    return messages

def list_tables():
    df=sql_excqute('show tables')
    return df.iloc[:,0].values
                



def connect_db():
    st.session_state['cnxn'], st.session_state['cursor']=setup_cursor()
    st.session_state['tables']=list_tables()


def check_key():
  try:
    response = openai.Completion.create(
    model="text-davinci-003",
    prompt="",
    max_tokens=1)
  except:
    return False
  return True

def check_status():
    return st.session_state['status']['db'] and st.session_state['status']['ai']
