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

    if State.user['role'] != 'admin':
      self.data_view.columns = self.data_view.columns[:-1]
    self.rp.items = anvil.server.call('get_user_documents', status)

  def new_document_click(self, **event_args):
    """This method is called when the button is clicked"""
    # dictionary
    doc = {}
    if alert(AddDocument(item=doc), large=True, buttons=None, role='card'):
      anvil.server.call('add_document', doc)
      self.rp.items = anvil.server.call('get_user_documents')
      



