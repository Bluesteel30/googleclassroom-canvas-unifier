from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from datetime import datetime, time

# Scopes to read courses and assignments
SCOPES = [
    'https://www.googleapis.com/auth/classroom.courses.readonly',
    'https://www.googleapis.com/auth/classroom.student-submissions.me.readonly'
]

creds = None
if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)

if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'client_secret.json', SCOPES)
        creds = flow.run_local_server(port=0)

    with open('token.json', 'w') as token:
        token.write(creds.to_json())

service = build('classroom', 'v1', credentials=creds)

# List all courses
results = service.courses().list().execute()
courses = results.get('courses', [])
course_dict = {}
all_assignments = []
for course in courses:
	course_dict[course['id']] = course['name']
	course_id = course['id']
	assignments = []
	page_token = None
	while True:
	    response = service.courses().courseWork().list(
	        courseId=course_id,
	        pageSize=100,
	        pageToken=page_token
	    ).execute()
	    
	    assignments.extend(response.get('courseWork', []))
	    
	    page_token = response.get('nextPageToken')
	    if not page_token:
	        break  # No more pages
	all_assignments.extend(assignments)

def parse_due_date_gc(assignment):
    due_date = assignment.get('dueDate')
    due_time = assignment.get('dueTime')

    if due_date:
        # Extract date parts
        year = due_date.get('year')
        month = due_date.get('month')
        day = due_date.get('day')

        # Extract time parts (optional)
        if due_time:
            hour = due_time.get('hours', 23)
            minute = due_time.get('minutes', 59)
            second = 59
        else:
            # Default time if none given
            hour, minute, second = 23, 59, 59

        try:
            # Compose full datetime
            dt = datetime(year, month, day, hour, minute, second)
            return dt
        except Exception:
            return datetime.min
    else:
        # No due date: sort last
        return datetime.now()

# Example usage with your list:
all_assignments.sort(key=parse_due_date_gc, reverse=True)
print(all_assignments)
