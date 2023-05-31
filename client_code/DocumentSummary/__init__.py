from ._anvil_designer import DocumentSummaryTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class DocumentSummary(DocumentSummaryTemplate):
  def __init__(self, status, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    if status != 'rejected':
      self.label_8.visible = False
      self.rejection_label.visible = False

  def download_button_click(self, **event_args):
    if self.item['attachment'] != None:
      anvil.media.download(self.item['attachment'])
