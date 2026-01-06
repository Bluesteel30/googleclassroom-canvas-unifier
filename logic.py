from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import requests
from datetime import datetime
from dotenv import load_dotenv
import pickle
import os


call_apis = True
if call_apis:
    load_dotenv("api.env")
    canvas_api_key = os.getenv('API_KEY')
    base_url = "https://canvas.instructure.com/api/v1/"
    course_link = {}
    headers = {
        "Authorization": "Bearer " + canvas_api_key
        }
    endpoint = "courses"
    canvas_response = requests.get(base_url+endpoint, headers=headers)


    canvas_assignments = []
    course_dictonary = {}
    if canvas_response.status_code == 200:
        courses = canvas_response.json()
        for course in courses:
            course_dictonary[course['name']] = True
            endpoint = "courses/"+str(course['id'])+"/assignments?include[]=submission&order_by=due_at"
            response = requests.get(base_url+endpoint, headers=headers)
            course_assignments_canvas = []
            url = base_url + endpoint

            while url: # Continues to get each page of data from Canvas until it gets everything
                aresponse = requests.get(url, headers=headers)
                if aresponse.status_code != 200:
                    break  

                data = aresponse.json()
                course_assignments_canvas.extend(data)

                # Handle pagination
                link = aresponse.headers.get('Link')
                next_url = None
                if link and 'rel="next"' in link:
                    parts = link.split(',')
                    for part in parts:
                        if 'rel="next"' in part:
                            next_url = part[part.find('<') + 1 : part.find('>')]
                            break
                url = next_url  # If next_url is None, loop stops

            # Now process assignments
            for assignment in course_assignments_canvas:
                submission = assignment.get('submission') or {}
                workflow_state = submission.get('workflow_state', 'Unsubmitted')
                if workflow_state ==  "pending_review":
                    workflow_state = "Pending Review"
                due_date = assignment.get('due_at') or "No Due Date"
                grade = submission.get('grade','Not Yet Graded')
                if  (grade == None):
                    grade = 'Not Yet Graded'
                if grade != 'Not Yet Graded':
                    grade = "Score: " + grade + " Pts"


                Canvas_data=({
                    'name': assignment['name'],
                    'due_at': due_date,
                    'workflow_state': workflow_state,
                    'id': assignment['id'],
                    'course_id': course['id'],
                    'course_name': course['name'],
                    'is_canvas' : True,
                    'grade' : grade

            })
                canvas_assignments.append(Canvas_data)

    else:
        print("Error:", response.status_code)


    SCOPES = [
        'https://www.googleapis.com/auth/classroom.courses.readonly',
        'https://www.googleapis.com/auth/classroom.student-submissions.me.readonly',
        'https://www.googleapis.com/auth/classroom.coursework.me'
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
            creds = flow.run_local_server(
                port=8080,
                access_type='offline',
                prompt='consent')


        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('classroom', 'v1', credentials=creds)

    # List all classroom classes
    results = service.courses().list().execute()
    courses = results.get('courses', [])
    link = {}
    classroom_assignments = []
    for course in courses:
        print(course['name'])
        course_dictonary[course['name']] = False
        course_id = course['id']
        link[course_id] = course['name']
        course_assignments_classroom = []
        page_token = None
        while True:
            response = service.courses().courseWork().list(
                courseId=course_id,
                pageSize=100,
                pageToken=page_token
            ).execute()
            
            course_assignments_classroom.extend(response.get('courseWork', []))
            
            page_token = response.get('nextPageToken')
            if not page_token:
                break  # No more pages
        classroom_assignments.extend(course_assignments_classroom)

        
    for assignment in classroom_assignments:
        submission = service.courses().courseWork().studentSubmissions().list(
        courseId = assignment['courseId'],
        courseWorkId = assignment['id'],
        userId='me'
        ).execute()
        assignment['is_canvas'] = False 
        assignment['course_name'] = link[assignment['courseId']]
        submissions = submission.get('studentSubmissions', [])
        assignment['submission'] = submissions[0] if submissions else None
        if assignment['submission']['state'] == 'CREATED':
            assignment['submission']['state'] = 'Unsubmitted'
        if assignment['submission']['state'] == 'TURNED_IN':
            assignment['submission']['state'] = 'Submitted'


    def parse_due_date(assignment):
        due = assignment.get('due_at')
        if due and due != "No Due Date":
            try:
                return datetime.strptime(due, "%Y-%m-%dT%H:%M:%SZ")
            except Exception:
                return datetime.now()

        due_date = assignment.get('dueDate')
        due_time = assignment.get('dueTime')
        if due_date:
            year = due_date.get('year')
            month = due_date.get('month')
            day = due_date.get('day')

            hour = due_time.get('hours', 23) if due_time else 23
            minute = due_time.get('minutes', 59) if due_time else 59
            second = 59
            try:
                assignment['due_at']=datetime(year, month, day, hour, minute, second)
                return datetime(year, month, day, hour, minute, second)
            except Exception:
                assignment['due_at']=datetime.now()
                return datetime.now()

        return datetime.now()


    total_list = canvas_assignments + classroom_assignments
    total_list.sort(key=parse_due_date, reverse=True)  # Latest first

if call_apis:
    with open('c_d.pkl', 'wb') as f:
        pickle.dump(course_dictonary, f)

    with open('data.pkl', 'wb') as f:
        pickle.dump(total_list, f)
else:
    with open('c_d.pkl', 'rb') as f:  # 'rb' = read binary
        course_dictonary = pickle.load(f)

    with open('data.pkl', 'rb') as f:  # 'rb' = read binary
        total_list = pickle.load(f)
