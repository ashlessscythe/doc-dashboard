from ._anvil_designer import SummaryPlotsTemplate
from anvil import *
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

Plot.templates["default"] = "rally"

class SummaryPlots(SummaryPlotsTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.

  def update_plots(self):
    labels, values = anvil.server.call('get_status_data')
    self.plot_1.figure = px.pie(labels=labels, values=values, hole=.4)
    self.plot_1.layout.title = "Documents by status"

    status_data, dept_data = anvil.server.call('get_status_dept_data')
    self.plot_2.figure = go.Pie(labels=status_data, values=dept_data, textinfo="value", hole=.4)
    self.plot_2.layout.title = "Total Docs by Dept"

    dates, qts = anvil.server.call('get_dates_data')
    print(f"dates is {dates} qts is {qts}")
    # self.plot_3.data = go.Scatter(x=dates, y=qts)
    
    self.plot_3.data = go.Pie(values=qts, labels=dates)
    self.plot_3.layout.title = "Docs through time"

  def download_summ_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    media_object = anvil.server.call('create_summary_pdf')
    anvil.media.download(media_object)

  def switch_1_change(self, **event_args):
    """This method is called when this switch is checked or unchecked"""
    self.update_plots()






