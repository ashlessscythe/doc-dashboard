from ._anvil_designer import TemplateDownloadTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class TemplateDownload(TemplateDownloadTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.download_dd.items = [(t['name'], t) for t in anvil.server.call('get_templates')]

    # Any code you write here will run before the form opens.

  def download_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    anvil.media.download(anvil.server.call('get_template', self.item['type']))

