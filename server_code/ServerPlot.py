import anvil.email
import anvil.google.auth, anvil.google.drive, anvil.google.mail
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from .ServerModule1 import *

def get_df():
  data = app_tables.documents.search()
  dicts = [
    {
      'status':r['status']['status'], 
      'submitted_by':r['submitted_by']['email'],
      'dept':r['dept']['dept'],
      'type':r['type']['type'],
      'description':r['description'],
      'message':r['status_change_message'],
      'created':r['created']
    } for r in data]
  df = pd.DataFrame.from_dict(dicts)
  return df

def get_status_data():
  df = get_df()
  df_stat = df.groupby(by=['status']).size().reset_index(name='count')
  df_dept = df.groupby(by=['dept']).size().reset_index(name='count')
  df_date = df.groupby(by=['type', 'created']).size().reset_index(name='count')
  df_date['created'] = pd.to_datetime(df_date['created'], utc=True)
  df_date['quarter'] = df_date['created'].dt.quarter
  return df_stat, df_dept, df_date

@anvil.server.callable
def create_plots():
  dept, stat, qtr = get_status_data()
  print(df.head())
  fig1 = px.pie(
    stat,
    labels='status',
    values='count',    
    title='Docs by status'
  )

  fig2 = px.pie(
    dept,
    labels='dept',
    values='count',
    title="Total Docs by Dept"
  )

  fig3 = px.scatter(
    qtr, x='created', y='quarter',
    title='Docs through time'
  )

  return fig1, fig2, fig3