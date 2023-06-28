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

@anvil.server.callable
def get_doc_data():
  data = app_tables.documents.search()
  df = pd.DataFrame(data)
  print(df.columns())
  df = df.loc[:,['ID', 'status', 'submitted_by', 'dept', 'type', 'description', 'status_change_message', 'created']]
  print(df.head())
  return df

@anvil.server.callable
def create_plots():
  df = get_doc_data()
  fig1 = px.pie(
    df,
    labels='status',
    values='ID',    
    title='Docs by status'
  )

  fig2 = px.pie(
    df,
    labels='dept',
    values='type',
    title="Total Docs by Dept"
  )

  dates, qts = get_dates_data()
  fig3 = px.scatter(
    x=dates, y=qts,
    title='Docs through time'
  )

  return fig1, fig2, fig3