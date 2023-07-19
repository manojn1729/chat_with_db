import streamlit as st 
import pyodbc
import os
import pandas as pd
from dotenv import load_dotenv
load_dotenv()

def user_chat (message):
    with st.chat_message("user", avatar='👶'):
        st.write(message)

def assistant_chat (message):
    with st.chat_message("assistant", avatar='🤖'):
        st.code(message, language='sql')

def setup_cursor():
    cnxn = pyodbc.connect("DRIVER={{{0}}}; SERVER={1};DATABASE={2}; UID={3}; PASSWORD={4};TransactionIsolationLevel=READ UNCOMMITTED;".format(os.getenv('DRIVER'),
                                                                                             os.getenv('SERVER'),
                                                                                             os.getenv('DATABASE'),
                                                                                             os.getenv('UID'),
                                                                                             os.getenv('PASSWORD')))
    return cnxn,cnxn.cursor()

def sql_excqute (query, cnxn):
    return pd.read_sql (query, cnxn)

def generate_ddl(table_name,cnxn):
    df=pd.read_sql (f"describe {table_name}", cnxn)
    query=f"Create table {table_name} ("
    for i,row in df.iterrows():
        query+=f"{row['Field']} {row['Type']}, "
    query=query[:-2]
    query+="}"
    return query