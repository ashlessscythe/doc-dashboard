from ._anvil_designer import SummaryPlotsTemplate
from anvil import *
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
    fig1, fig2, fig3 = anvil.server.call('create_plots')
    
    self.plot_1.figure = fig1
    self.plot_2.figure = fig2
    self.plot_3.figure = fig3

  def download_summ_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    media_object = anvil.server.call('create_summary_pdf')
    anvil.media.download(media_object)

  def switch_1_change(self, **event_args):
    """This method is called when this switch is checked or unchecked"""
    self.update_plots()






