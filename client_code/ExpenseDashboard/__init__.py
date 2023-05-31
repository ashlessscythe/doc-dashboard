from ._anvil_designer import ExpenseDashboardTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ..AddExpense import AddExpense
from .. import State

class ExpenseDashboard(ExpenseDashboardTemplate):
  def __init__(self, status, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    if State.user['role'] != 'admin':
      self.data_view.columns = self.data_view.columns[:-1]
    self.rp.items = anvil.server.call('get_user_expenses', status)

  def new_expense_click(self, **event_args):
    """This method is called when the button is clicked"""
    expense = {}
    if alert(AddExpense(item=expense), large=True, buttons=None):
      anvil.server.call('add_expense', expense)
      self.rp.items = anvil.server.call('get_user_expenses')
