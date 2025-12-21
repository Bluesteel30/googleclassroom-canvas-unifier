from flask import Flask, render_template, request
import requests
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from datetime import datetime
from dotenv import load_dotenv
load_dotenv("api.env")
api = os.getenv('API_KEY')
headers = {
	"Authorization": "Bearer " + api
	}

base_url = "https://canvas.instructure.com/api/v1/"
courses_data = {}
all_assignments = []
endpoint = "courses"
response = requests.get(base_url+endpoint, headers=headers)
if response.status_code == 200:
	courses = response.json()
	for course in courses:
		course_id = course["id"]
		courses_data[course_id] = {"name": course["name"], "assignments":[]}
		url = base_url + endpoint

		while url:
			aresponse = requests.get(url, headers=headers)
			if aresponse.status_code != 200:
				break  

			data = aresponse.json()
			all_assignments.extend(data)

			# Handle pagination
			link = aresponse.headers.get('Link')
			next_url = None
			if link and 'rel="next"' in link:
				parts = link.split(',')
				for part in parts:
					if 'rel="next"' in part:
						next_url = part[part.find('<') + 1 : part.find('>')]
						break
			url = next_url
		for assignment in all_assignments:
			submission = assignment.get('submission') or {}
			courses_data[course_id]["assignments"].append({
				"id": assignment["id"],
				"name": assignment["name"],
				"due_at": assignment.get("due_at") or "No Due Date",
				"workflow_state": submission.get("workflow_state", "Unsubmitted"),
				"course_id": course_id
			})
else:
	print("Error:", response.status_code)

courses_data = {}

# Fetch all courses
SCOPES = [
    'https://www.googleapis.com/auth/classroom.courses.readonly',
    'https://www.googleapis.com/auth/classroom.student-submissions.me.readonly',
    'https://www.googleapis.com/auth/classroom.coursework.me.readonly'
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
results = service.courses().list().execute()
courses = results.get('courses', [])

for course in courses:
    course_id = int(course['id'])
    courses_data[course_id] = {
        "name": course['name'],
        "assignments": []
    }

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
            break

    # Add student submission state for each assignment
    for a in assignments:
        submission = service.courses().courseWork().studentSubmissions().list(
            courseId=course_id,
            courseWorkId=a['id'],
            userId='me'
        ).execute()

        submissions = submission.get('studentSubmissions', [])
        state = submissions[0]['state'].lower() if submissions else 'unsubmitted'
        if state == 'created':
            state = 'unsubmitted'  # normalize

        # Parse due date if present
        due_date = a.get('dueDate')
        due_time = a.get('dueTime')
        if due_date:
            from datetime import datetime
            year = due_date['year']
            month = due_date['month']
            day = due_date['day']
            hour = due_time.get('hours', 23) if due_time else 23
            minute = due_time.get('minutes', 59) if due_time else 59
            second = 59
            due_at = datetime(year, month, day, hour, minute, second)
        else:
            due_at = "No Due Date"

        # Add to courses_data in same format as Canvas
        courses_data[course_id]['assignments'].append({
            "id": a['id'],
            "name": a['title'],
            "due_at": due_at,
            "workflow_state": state,
            "course_id": course_id
        })


results = service.courses().list().execute()
courses = results.get('courses', [])

for course in courses:
    course_id = int(course['id'])
    courses_data[course_id] = {
        "name": course['name'],
        "assignments": []
    }

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
            break

    # Add student submission state for each assignment
    for a in assignments:
        submission = service.courses().courseWork().studentSubmissions().list(
            courseId=course_id,
            courseWorkId=a['id'],
            userId='me'
        ).execute()

        submissions = submission.get('studentSubmissions', [])
        state = submissions[0]['state'].lower() if submissions else 'unsubmitted'
        if state == 'created':
            state = 'unsubmitted'  # normalize

        # Parse due date if present
        due_date = a.get('dueDate')
        due_time = a.get('dueTime')
        if due_date:
            from datetime import datetime
            year = due_date['year']
            month = due_date['month']
            day = due_date['day']
            hour = due_time.get('hours', 23) if due_time else 23
            minute = due_time.get('minutes', 59) if due_time else 59
            second = 59
            due_at = datetime(year, month, day, hour, minute, second)
        else:
            due_at = "No Due Date"

        # Add to courses_data in same format as Canvas
        courses_data[course_id]['assignments'].append({
            "id": a['id'],
            "name": a['title'],
            "due_at": due_at,
            "workflow_state": state,
            "course_id": course_id
        })

















