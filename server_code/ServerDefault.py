import anvil.email
import anvil.google.auth, anvil.google.drive, anvil.google.mail
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import anvil.pdf
from datetime import datetime

@anvil.server.callable(require_user=True)
def get_user_documents(status=None):
  d = {}
  if anvil.users.get_user()['role'] != 'admin':
    d['submitted_by'] = anvil.users.get_user()
  if status != None:
    d['status'] = app_tables.document_status.get(status=status)
    print(f"post status is {d['status']}")
  return app_tables.documents.search(tables.order_by('created', ascending=False), **d)

@anvil.server.callable(require_user=True)
def add_document(doc):
  print(f"document dict is {doc}")
  # document dict is {'dept': 'DCS', 'type': 'observation', 'description': 'obs', 'attachment': <anvil._serialise.StreamingMedia object at 0x7f39117359f0>}
  app_tables.documents.add_row(
    created=datetime.now(), 
    status=app_tables.document_status.get(status='pending'), 
    submitted_by=anvil.users.get_user(), 
    dept=app_tables.departments.get(dept=doc['dept']),
    type=app_tables.document_type.get(type=doc['type']),
    description=doc['description'],
    attachment=doc['attachment']
  )

def is_admin(user):
  return user['role'] == 'admin'

@anvil.server.background_task
def send_email(user, message):
  anvil.email.send(to=user, from_name="Documents App", subject="Your document has been updated", html=message)

@anvil.server.callable(require_user=is_admin)
def change_status(row, status):
  old_status = row['status']
  user = row['submitted_by']['email']
  message = f"<p>Hi, {user},</p><p>The status of your document ('{row['description']}') changed from <b>{old_status}</b> to <b>{status}</b>.</p><p>Visit the <a href={anvil.server.get_app_origin()}>app</a> to learn more details.</p>"
  row.update(status=app_tables.document_status.get(status=status))
  anvil.server.launch_background_task('send_email', user=user, message=message)

@anvil.server.callable(require_user=is_admin)
def reject(row, message):
  change_status(row, 'rejected')
  row.update(status_change_message=message)

@anvil.server.callable(require_user=is_admin)
def followup(row, message):
  change_status(row, 'followup')
  row.update(status_change_message=message)

@anvil.server.callable(require_user=is_admin)
def get_status_data():
  status_data = [x['status'] for x in app_tables.documents.search()]
  labels = list(set(status_data))
  values = []
  for l in labels:
    values.append(status_data.count(l))
  return labels, values

@anvil.server.callable(require_user=is_admin)
def get_status_dept_data():
  pending_row = app_tables.document_status.get(status='pending')
  rejected_row = app_tables.document_status.get(status='rejected')
  data = app_tables.documents.search(status=q.any_of(pending_row, rejected_row))
  status_data = [x['status']['status'] for x in data]
  dept_data = [x['type']['type'] for x in data]
  return status_data, dept_data

@anvil.server.callable
def get_depts():
  return app_tables.departments.search()

@anvil.server.callable
def get_types():
  return app_tables.document_type.search()

@anvil.server.callable
def get_templates():
  return [t['name'] for t in app_tables.templates.search()]

@anvil.server.callable
def download_template(type):
  row = app_tables.document_type.get(type=type)
  return app_tables.templates.get(name=row)['file']

@anvil.server.callable(require_user=is_admin)
def get_dates_data():
  dates = [x['created'].date() for x in app_tables.documents.search()]
  unique_dates = sorted(set(dates))
  qts = []
  for d in unique_dates:
    qts.append(dates.count(d))
  return unique_dates, qts

@anvil.server.callable(require_user=is_admin)
def create_summary_pdf():
  return anvil.pdf.render_form('SummaryPlots')

  