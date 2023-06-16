from ._anvil_designer import AddDocumentTemplate
from anvil import *
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class AddDocument(AddDocumentTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    # initialize drop-downs
    self.dept_dd.items = [(d['dept']) for d in anvil.server.call('get_depts')]
    self.type_dd.items = [(t['type']) for t in anvil.server.call('get_types')]

  def doc_upload_change(self, file, **event_args):
    """This method is called when a new file is loaded into this FileLoader"""
    self.item['attachment'] = file

  def save_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    if not 'attachment' in self.item:
       # notify
      pass
    self.item['dept'] = self.dept_dd.selected_value
    self.item['type'] = self.type_dd.selected_value
    self.item['description'] = self.description_box.text
    if self.item['dept'] and self.item['type']:
      self.raise_event("x-close-alert", value=True)
    else:
      if not self.item['dept']:
        self.dept_dd.role = "input-error"
      if not self.item['type']:
        self.type_dd.role = "input-error"
      if not self.item['attachment']:
        self.doc_upload.role = 'input-error'

  def cancel_button_click(self, **event_args):
    self.raise_event("x-close-alert", value=False)

  def dept_dd_change(self, **event_args):
    """This method is called when the text in this text box is edited"""
    if self.dept_dd.role == "input-error" and self.dept_dd.selected_value:
      self.dept_dd.role = "default"

  def type_dd_change(self, **event_args):
    """This method is called when the text in this text box is edited"""
    if self.type_dd.role == "input-error" and self.type_dd.selected_value:
      self.type_dd.role = "default"









    


  

  

  


