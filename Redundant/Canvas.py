import requests
base_url = "https://canvas.instructure.com/api/v1/"
course_link = {}
headers = {
    "Authorization": "Bearer 7~YcceBzL7wPGaLXnARWvv9aBXHw9HR8FLUTkYT6rNUUruxUhn3h6tEQW8ZeJwFc66"
    }
endpoint = "courses"
response = requests.get(base_url+endpoint, headers=headers)
if response.status_code == 200:
    courses = response.json()
    for course in courses:
    	i = course['id']
        endpoint = "courses/"+str(i)+"/assignments?include[]=submission&order_by=due_at"
        response = requests.get(base_url+endpoint, headers=headers)
        all_assignments = []
        url = base_url + endpoint  # Start with first page

        while url:
            aresponse = requests.get(url, headers=headers)
            if aresponse.status_code != 200:
                break  # Stop on error

            data = aresponse.json()
            all_assignments.extend(data)  # Add current page's assignments

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
        assignment_list = []
        for assignment in all_assignments:
            submission = assignment.get('submission') or {}
            workflow_state = submission.get('workflow_state', 'Unsubmitted')
            due_date = assignment.get('due_at') or "No Due Date"
            assignment_list.append({
                'name': assignment['name'],
                'due_at': due_date,
                'workflow_state': workflow_state,
                'id': str(assignment['id'])
        })
        course_link[course['name']] = assignment_list

else:
    print("Error:", response.status_code)
print(course_link)