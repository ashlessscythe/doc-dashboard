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
from plotly.subplots import make_subplots
from .ServerDefault import *
from datetime import datetime
import calendar

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
  df['month'] = df['created'].dt.month
  df['quarter'] = df['created'].dt.quarter

  # separate dfs
  df_stat = df.groupby(by=['status', 'quarter']).size().reset_index(name='count')
  df_dept = df.groupby(by=['dept', 'week', 'type']).size().reset_index(name='count')
  df_date = df.groupby(by=['status', 'dept', 'type', 'created', 'quarter']).size().reset_index(name='count')
  df_type = df.groupby(by=['type', 'status', 'dept', 'month']).size().reset_index(name='count')
  return df_stat, df_dept, df_date, df_type

@anvil.server.callable
def create_plots():
  df_stat, df_dept, df_date, df_type = get_status_data()
  [print(df.head()) for df in [df_stat, df_dept, df_date, df_type]]
  
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

  # Filter to only include data that has 'month' information
  df_type = df_type[df_type['month'].notna()]
    
  # Convert month numbers to month names
  df_type['month'] = df_type['month'].apply(lambda x: calendar.month_abbr[int(x)])
    
  # fig4 = px.bar(df_type,
  #               x='month',
  #               y='count',
  #               color='status',
  #               barmode='stack',
  #               title='Document Status by Department and Month',
  #               labels={'count': 'Document Count'},
  #               category_orders={"month": list(calendar.month_abbr[1:])},
  #               facet_col='dept')
  
  # Filter by type 'SOP Review'
  df_type = df_type[df_type['type'] == 'sop review']

  # Create subplots
  fig4 = make_subplots(rows=1, cols=len(df_type['dept'].unique()), subplot_titles=df_type['dept'].unique())
  
  color_map = {'approved': 'green', 'pending': 'orange', 'followup': 'purple', 'rejected': 'red'}  # Add more statuses and colors as needed

  dept_buttons = []
  all_traces = []
  
  col = 1
  for dept in df_type['dept'].unique():
      for status in df_type['status'].unique():
          df_filtered = df_type[(df_type['dept'] == dept) & (df_type['status'] == status)]
          text_labels = [f"{count} ({status})" for count in df_filtered['count']]
          fig4.add_trace(go.Bar(
              x=df_filtered['month'],
              y=df_filtered['count'],
              name=status,
              marker_color=color_map.get(status, 'blue'),
              showlegend=False, #hide these
              text=text_labels,
              textposition='inside',
              visible=True
          ), row=1, col=col)
          all_traces.append(dept)
      col += 1

  # Add dummy traces for all unique statuses to ensure they appear in the legend
  for status in df_type['status'].unique():
      fig4.add_trace(go.Bar(
          x=[None],
          y=[None],
          name=status,
          marker_color=color_map.get(status, 'blue'),
          showlegend=True,
          visible=False
      ))
      
  for dept in df_type['dept'].unique():
      visibility_array = [dept == trace for trace in all_traces]
      dept_buttons.append(
          dict(
              args=[{"visible": visibility_array}],
              label=dept,
              method="update"
          )
      )
  # # Add table
  # df_first_dept = df_type[df_type['dept'] == df_type['dept'].unique()[0]]
  # table_data = pd.pivot_table(df_first_dept, values='count', index=['month'], columns=['status'], fill_value=0).reset_index()
  # table_trace = go.Table(
  #     header=dict(values=table_data.columns.tolist(), align='left'),
  #     cells=dict(values=table_data.values.T.tolist(), align='left'),
  #     domain=dict(x=[0.5, 1], y=[0, 0.3])
  # )
  # fig4.add_trace(table_trace)

  # Make the first set of traces visible by default
  for i in range(len(df_type['status'].unique())):
      fig4.data[i].visible = True

  fig4.update_layout(
    barmode='stack',
    title='SOP Reviews by Month / Status'
  )
  return fig1, fig2, fig4
  