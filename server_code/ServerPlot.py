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
from .ServerDefault import *
from datetime import datetime

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
  # format date
  df['created'] = pd.to_datetime(df['created'], utc=True)
  df['week'] = df['created'].dt.isocalendar().week
  df['quarter'] = df['created'].dt.quarter

  # separate dfs
  df_stat = df.groupby(by=['status', 'quarter']).size().reset_index(name='count')
  df_dept = df.groupby(by=['dept', 'week', 'type']).size().reset_index(name='count')
  df_date = df.groupby(by=['status', 'dept', 'type', 'created', 'quarter']).size().reset_index(name='count')
  return df_stat, df_dept, df_date

@anvil.server.callable
def create_plots():
  df_stat, df_dept, df_date = get_status_data()
  [print(df.head()) for df in [df_stat, df_dept, df_date]]
  
  fig1 = px.pie(
    df_stat,
    names='status',
    values='count',
    facet_col='quarter',
    facet_col_wrap=2,
    title='Docs by status'
  )

  fig2 = px.bar(
    df_dept,
    x='type',
    y='count',
    color='dept',
    title="Total Docs by Dept"
  )
  fig2.add_hline(
    y=2, 
    line_dash='dot', 
    annotation_text='minimum', 
    annotation_position='top left'
  )
  
  fig3 = px.density_heatmap(
    df_date, 
    x='created',
    y='status',
    marginal_x='histogram',
    marginal_y='histogram',
    title='Docs through time'
  )
  
  return fig1, fig2, fig3
  