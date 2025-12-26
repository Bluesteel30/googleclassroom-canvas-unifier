from flask import Flask, render_template, request
import requests
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from datetime import datetime
from dotenv import load_dotenv
import pickle


current = False
if current:
    load_dotenv("api.env")
    api = os.getenv('API_KEY')
    base_url = "https://canvas.instructure.com/api/v1/"
    course_link = {}
    headers = {
        "Authorization": "Bearer " + api
        }
    endpoint = "courses"
    response = requests.get(base_url+endpoint, headers=headers)


    total_list = []
    c_d = {}
    if response.status_code == 200:
        courses = response.json()
        for course in courses:
            c_d[course['name']] = True
            endpoint = "courses/"+str(course['id'])+"/assignments?include[]=submission&order_by=due_at"
            response = requests.get(base_url+endpoint, headers=headers)
            course_assignments = []
            url = base_url + endpoint

            while url: # Continues to get each page of data from Canvas until it gets everything
                aresponse = requests.get(url, headers=headers)
                if aresponse.status_code != 200:
                    break  

                data = aresponse.json()
                course_assignments.extend(data)

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
            for assignment in course_assignments:
                submission = assignment.get('submission') or {}
                workflow_state = submission.get('workflow_state', 'Unsubmitted')
                due_date = assignment.get('due_at') or "No Due Date"
                Canvas_data=({
                    'name': assignment['name'],
                    'due_at': due_date,
                    'workflow_state': workflow_state,
                    'id': assignment['id'],
                    'course_id': course['id'],
                    'course_name': course['name'],
                    'is_canvas' : True

            })
                total_list.append(Canvas_data)

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

    # List all courses
    results = service.courses().list().execute()
    courses = results.get('courses', [])
    link = {}
    every_assignment = []
    for course in courses:
        print(course['name'])
        c_d[course['name']] = False
        course_id = course['id']
        link[course_id] = course['name']
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
        every_assignment.extend(assignments)

        
    for i in every_assignment:
        submission = service.courses().courseWork().studentSubmissions().list(
        courseId = i['courseId'],
        courseWorkId = i['id'],
        userId='me'
        ).execute()
        i['is_canvas'] = False 
        i['course_name'] = link[i['courseId']]
        submissions = submission.get('studentSubmissions', [])
        i['submission'] = submissions[0] if submissions else None
        if i['submission']['state'] == 'CREATED':
            i['submission']['state'] = 'unsubmitted'
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


    total_list.extend(every_assignment)
    total_list.sort(key=parse_due_date, reverse=True)  # Latest first

if current:
    with open('c_d.pkl', 'wb') as f:
        pickle.dump(c_d, f)

    with open('data.pkl', 'wb') as f:
        pickle.dump(total_list, f)
else:
    with open('c_d.pkl', 'rb') as f:  # 'rb' = read binary
        c_d = pickle.load(f)

    with open('data.pkl', 'rb') as f:  # 'rb' = read binary
        total_list = pickle.load(f)

app = Flask(__name__)

print(c_d)
@app.route('/', methods = ['GET','POST'])


def home():
    f = ""
    new_dict = dict()
    if "View All" in new_dict:
        del new_dict["View All"]
    temp_list = []
    course_name = request.form.get("course")
    if not course_name or course_name == "View All":
        return render_template('index.html', course_link=total_list, c=c_d, f = f)

    for i in total_list:
        if i['course_name'] == course_name:
            f = course_name
            temp_list.append(i)
            new_dict["View All"] = True
            new_dict |= c_d
            
    return render_template('index.html', course_link=temp_list, c=new_dict, f = f)
@app.route('/canvas', methods = ['GET','POST'])
def canvas():
    f = ""
    new_dict = dict()
    if "View All" in new_dict:
        del new_dict["View All"]
    temp_list = []
    course_name = request.form.get("course")

    if not course_name or course_name == "View All":
        return render_template('canvas.html', course_link=total_list, c=c_d, f = f)

    for i in total_list:
        if i['course_name'] == course_name:
            f = course_name
            temp_list.append(i)
            new_dict["View All"] = True
            new_dict |= c_d
    return render_template('canvas.html', course_link=temp_list, c=new_dict, f = f)
@app.route('/classroom', methods = ['GET','POST'])
def classroom():
    f = ""
    new_dict = dict()
    if "View All" in new_dict:
        del new_dict["View All"]

    temp_list = []
    course_name = request.form.get("course")

    if not course_name or course_name == "View All":
        return render_template('gc.html', course_link=total_list, c=c_d, f = f)

    for i in total_list:
        if i['course_name'] == course_name:
            f = course_name
            temp_list.append(i)
            new_dict["View All"] = False
            new_dict |= c_d


    return render_template('gc.html', course_link=temp_list, c=new_dict, f = f)

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)

