from ._anvil_designer import RowTemplate1Template
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from datetime import datetime
from ... import State
from ...DocumentSummary import DocumentSummary
from ..._RejectComment import _RejectComment
from ..._FollowupComment import _FollowupComment
from ..._ConfirmDelete import _ConfirmDelete

class RowTemplate1(RowTemplate1Template):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.
    self.btns_panel.visible = (State.user['role'] == 'admin')
    self.delete.visible = True

  def set_styling(self):
    if self.item['status']['status'] == 'pending':
      self.approve.visible, self.reject.visible, self.followup.visible = True, True, True
      self.status_label.background = '#D6BA58'
    elif self.item['status']['status'] == 'approved':
      self.approve.visible, self.reject.visible, self.followup.visible = False, False, False
      self.status_label.background = '#1EB980'
    elif self.item['status']['status'] == 'followup':
      self.approve.visible, self.reject.visible, self.followup.visible = True, True, False
      self.status_label.background = '#78C0E0'
    else:
      self.approve.visible, self.reject.visible, self.followup.visible = False, False, True
      self.status_label.background = '#D64D47'
  
  def approve_click(self, **event_args):
    anvil.server.call('change_status', self.item, 'approved')
    self.refresh_data_bindings()
    
  def reject_click(self, **event_args):
    msg = {}
    if alert(_RejectComment(item=msg), large=True, buttons=[("Save", True), ("Cancel", False)]):
      anvil.server.call('reject', self.item, msg['msg'])
    self.refresh_data_bindings()

  def followup_click(self, **event_args):
    msg = {}
    if alert(_FollowupComment(item=msg), large=True, buttons=[("Save", True), ("Cancel", False)]):
      anvil.server.call('followup', self.item, msg['msg'])
    self.refresh_data_bindings()
    
  def delete_click(self, **event_args):
    """This method is called when the button is clicked"""
    msg = {'msg':'Really delete?'}
    if alert(
      content=_ConfirmDelete(item=msg), 
      title='Confirm Delete',
      large=True,
      buttons=[
        ("Yes", True),
        ("No", False)
      ]):
      print(f"msg is {msg} item is {self.item}")
      anvil.server.call('delete_doc', self.item)
      n = Notification(
        message="Item deleted",
        timeout=2
      )
      n.show()
      open_form('Main')
      self.refresh_data_bindings()
      
  def description_link_click(self, **event_args):
    alert(content=DocumentSummary(item=self.item, status=self.item['status']), large=True)

  def form_refreshing_data_bindings(self, **event_args):
    """This method is called when refreshing_data_bindings is called"""
    self.set_styling()








    

    


