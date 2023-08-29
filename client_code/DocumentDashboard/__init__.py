from ._anvil_designer import DocumentDashboardTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ..AddDocument import AddDocument
from .. import State

class DocumentDashboard(DocumentDashboardTemplate):
  def __init__(self, status, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    # set global
    State.status = status
    self.dd_dept_filter.items = [(d['dept']) for d in anvil.server.call('get_depts')]

    if State.user['role'] != 'admin':
      # self.data_view.columns = self.data_view.columns[:-1]
      self.label_filter.visible = False
      self.dd_dept_filter.visible = False
      self.btn_apply.visible = False
    self.rp.items = anvil.server.call('get_user_documents', State.status, State.dept_filter)

  def new_document_click(self, **event_args):
    """This method is called when the button is clicked"""
    # dictionary
    doc = {}
    if alert(AddDocument(item=doc), large=True, buttons=None, role='card'):
      anvil.server.call('add_document', doc)
      self.rp.items = anvil.server.call('get_user_documents')

  def dd_dept_filter_change(self, **event_args):
    """This method is called when an item is selected"""
    self.refresh_data_bindings()

  def filter_table(self, **event_args):
    State.dept_filter = self.dd_dept_filter.selected_value
    self.rp.items = anvil.server.call('get_user_documents', State.status, State.dept_filter)
  
  def btn_apply_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.filter_table()



      



