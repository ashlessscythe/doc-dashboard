from ._anvil_designer import SummaryPlotsTemplate
from anvil import *
import plotly.graph_objects as go
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
    labels, values = anvil.server.call('get_status_data')
    self.plot_1.data = go.Pie(labels=labels, values=values, hole=.4)
    self.plot_1.layout.title = "Expense requests by status"

    status_data, amount_data = anvil.server.call('get_status_amount_data')
    self.plot_2.data = go.Pie(labels=status_data, values=amount_data, textinfo="value", hole=.4)
    self.plot_2.layout.title = "Total money reimbursed vs. to be reimbursed"

    dates, qts = anvil.server.call('get_dates_data')
    self.plot_3.data = go.Scatter(x=dates, y=qts)
    self.plot_3.layout.title = "Expense requests through time"

  def download_summ_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    media_object = anvil.server.call('create_summary_pdf')
    anvil.media.download(media_object)





