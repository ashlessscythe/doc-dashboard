from ._anvil_designer import MainTemplate
from anvil import *
import plotly.graph_objects as go
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from .. import State
from ..DocumentDashboard import DocumentDashboard
from ..SummaryPlots import SummaryPlots
from ..DownloadTemplate import DownloadTemplate
from ..DownloadSOP import DownloadSOP

class Main(MainTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    
    self.switch_to_dashboard(None)
    if State.user['role'] == 'admin':
      self.separator_label_2.visible = True
      self.summary_btn.visible = True
      self.summary_btn.enabled = True

  def log_out_click(self, **event_args):
    """This method is called when the button is clicked"""
    anvil.users.logout()
    open_form('Login')

  def switch_to_dashboard(self, status):
    self.content_panel.clear()
    print(f"status is {status}")
    self.content_panel.add_component(DocumentDashboard(status=status))
  
  def pending_approval_click(self, **event_args):
    self.switch_to_dashboard('pending')

  def pending_followup_click(self, **event_args):
    self.switch_to_dashboard('followup')

  def past_docs_click(self, **event_args):
    self.switch_to_dashboard(q.any_of('approved'))

  def all_docs_click(self, **event_args):
    self.switch_to_dashboard(None)

  def summary_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.content_panel.clear()
    self.content_panel.add_component(SummaryPlots())

  def templates_btn_click(self, **event_args):
    # self.content_panel.clear()
    # self.content_panel.add_component(DownloadTemplate())
    # try with alert
    alert(
      content=DownloadTemplate(),
      buttons=["Close"],
      large=True, 
      dismissible=True,
      role='card'
    )

  def schedule_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    alert(
      content=DownloadSOP(),
      buttons=["Close"],
      large=True,
      dismissible=True,
      role='card'
    )





  














