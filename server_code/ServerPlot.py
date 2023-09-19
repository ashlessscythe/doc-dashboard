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
    } for r in data if not r.get('deleted', False)
  ]
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
  df_dept = df.groupby(by=['dept', 'month', 'type']).size().reset_index(name='count')
  df_date = df.groupby(by=['status', 'dept', 'type', 'created', 'quarter']).size().reset_index(name='count')
  df_type = df.groupby(by=['type', 'status', 'dept', 'month']).size().reset_index(name='count')
  return df_stat, df_dept, df_date, df_type

@anvil.server.callable
def create_plots():
  df_stat, df_dept, df_date, df_type = get_status_data()
  [print(df) for df in [df_stat, df_dept, df_date, df_type]]
  
  # Initialize subplots for pie charts
  quarters = df_stat['quarter'].unique()
  n_quarters = len(quarters)
  fig1 = make_subplots(rows=1, cols=n_quarters, specs=[[{'type':'domain'}]*n_quarters], subplot_titles=[f'Quarter {q}' for q in quarters])
  
  # Add pie charts for each quarter
  for i, quarter in enumerate(quarters, start=1):
      df_filtered = df_stat[df_stat['quarter'] == quarter]
      fig1.add_trace(
          go.Pie(labels=df_filtered['status'], values=df_filtered['count'], name=f'Quarter {quarter}'),
          row=1, col=i
      )
  
  # Update layout
  fig1.update_layout(title_text='Docs by Status')

  # Initialize figure
  fig2 = go.Figure()
  
  # Create traces
  trace_indices_by_month = {}
  trace_index = 0
  for month in df_dept['month'].unique():
      trace_indices_by_month[month] = []
      for dept in df_dept['dept'].unique():
          for doc_type in df_dept['type'].unique():
              df_filtered = df_dept[(df_dept['month'] == month) & (df_dept['dept'] == dept) & (df_dept['type'] == doc_type)]
              fig2.add_trace(go.Bar(
                  x=[dept],
                  y=df_filtered['count'],
                  name=f"{doc_type} ({calendar.month_abbr[int(month)]})",
                  showlegend=False,
                  visible=(month == df_dept['month'].min())
              ))
              trace_indices_by_month[month].append(trace_index)
              trace_index += 1
            
  # Add dummy traces for all unique types to ensure they appear in the legend
  min_month = df_dept['month'].min()
  for type in df_dept['type'].unique():
      fig2.add_trace(go.Bar(
          x=[None],
          y=[None],
          name=type,
          showlegend=True,
          visible=True if month == min_month else 'legendonly'
      ))
    
  # Add horizontal line
  fig2.add_shape(
      go.layout.Shape(
          type="line",
          x0=min(df_dept['dept']),
          x1=max(df_dept['dept']),
          y0=2,
          y1=2,
          line=dict(dash="dot")
      )
  )
  
  # create dropdown
  month_buttons = []
  total_traces = len(fig2.data)
  for month in df_dept['month'].unique():
      visibility_array = [False] * total_traces  # Initialize with all False
      for index in trace_indices_by_month[month]:
          visibility_array[index] = True  # Set visibility to True for relevant traces
      month_buttons.append(
        dict(
          args=[{"visible": visibility_array}],
          label=calendar.month_abbr[int(month)],
          method="update"
        )
      )
    
  # add dropdown to layout
  fig2.update_layout(
    title='Total Docs by Dept',
    barmode='stack',
    updatemenus=[
      dict(
        buttons=month_buttons,
        direction="down",
        pad={"r": 10, "t": 10},
        showactive=True,
        x=0.1,
        xanchor="left",
        y=1.15,
        yanchor="top"
      )
    ]
  )
  
  # fig3 = px.density_heatmap(
  #   df_date, 
  #   x='created',
  #   y='status',
  #   marginal_x='histogram',
  #   marginal_y='histogram',
  #   title='Docs through time'
  # )

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
  df_sop = df_type[df_type['type'] == 'sop review']

  # Create subplots
  fig4 = make_subplots(rows=1, cols=len(df_sop['dept'].unique()), subplot_titles=df_sop['dept'].unique())
  
  color_map = {'approved': 'green', 'pending': 'orange', 'followup': 'purple', 'rejected': 'red'}  # Add more statuses and colors as needed

  dept_buttons = []
  all_traces = []
  
  col = 1
  for dept in df_sop['dept'].unique():
      for status in df_sop['status'].unique():
          df_filtered = df_sop[(df_sop['dept'] == dept) & (df_sop['status'] == status)]
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
  for status in df_sop['status'].unique():
      fig4.add_trace(go.Bar(
          x=[None],
          y=[None],
          name=status,
          marker_color=color_map.get(status, 'blue'),
          showlegend=True,
          visible=False
      ))
      
  for dept in df_sop['dept'].unique():
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
  for i in range(len(df_sop['status'].unique())):
      fig4.data[i].visible = True

  fig4.update_layout(
    barmode='stack',
    title='SOP Reviews by Month / Status'
  )
  return fig1, fig2, fig4
  