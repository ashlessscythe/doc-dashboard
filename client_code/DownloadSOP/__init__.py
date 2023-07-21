from ._anvil_designer import DownloadSOPTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class DownloadSOP(DownloadSOPTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.dept_dd.items = [(d['dept']) for d in anvil.server.call('get_depts')]

    # Any code you write here will run before the form opens.

  def download_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    anvil.media.download(
      anvil.server.call(
        'download_sop', 
        self.item['dept'], 
        self.item['month'],
        self.item['sop']
      )
    )

  def dept_dd_change(self, **event_args):
    """This method is called when an item is selected"""
    # get months for dept
    dd_items = [(d['month']['month']) for d in anvil.server.call('get_sop_months', self.item['dept'])]
    self.month_dd.items = set(dd_items)
    self.month_dd.visible = True
    if len(dd_items) > 0:
      self.month_dd.placeholder = 'Select Month'
    else:
      self.month_dd.placeholder = 'No SOP for selected dept'

  def month_dd_change(self, **event_args):
    """This method is called when an item is selected"""
    dd_items = [(s['name']) for s in anvil.server.call('get_sops', self.item['dept'], self.item['month'])]
    self.sop_dd.items = dd_items
    self.sop_dd.visible = True
    if len(dd_items) > 0:
      self.sop_dd.placeholder = 'Select SOP'
    else:
      self.sop_dd.placeholder = 'No SOP for selected dept'


