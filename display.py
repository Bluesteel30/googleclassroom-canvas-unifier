from flask import Flask, render_template, request, make_response, redirect, g
from logic import *
import requests
import time

TEMPLATES = {
    '/canvas' : 'canvas.html',
    '/classroom' : 'classroom.html',
    '/' : 'unified.html'
}

app = Flask(__name__)

"""Requests "last_ran" which is the last time the data has been updated. If it doesn't exist then it sets the 
"last_ran" to NONE and then updates the data and sets g.updated to the current time
"""
"""@app.before_request
def refresh_list():
    raw = request.cookies.get("last_ran")
    try:
        last_ran = float(raw)
    except(TypeError, ValueError):
        last_ran = None
    current_time = time.time()
    if last_ran is None or current_time-last_ran > 10*60:
        updateData()
        g.updated = current_time

#Stores the update time as a cookie after the request is made
@app.after_request
def store_last_ran(response):
    if hasattr(g, "updated"):
        response.set_cookie("last_ran", str(g.updated),max_age=60*20)
    return response
"""

@app.route('/toggle-theme', methods = ['GET','POST'])

def toggle_theme():
    light = request.cookies.get("light_mode", "off")
    print(light)
    resp = make_response(redirect(request.referrer or "/"))
    new_value = "off" if light == "on" else "on"
    if light == "on" :   
        resp.set_cookie("light_mode",new_value ,max_age=60*60*24)
    else:
        resp.set_cookie("light_mode", new_value ,max_age=60*60*24)
    return resp

@app.route('/apply-filter', methods = ['GET','POST'])

def apply_filter():
    course_dictonary, total_list = loadAssignments()
    f = ""
    path = request.path
    template = TEMPLATES.get(path, "unified.html")
    light = request.cookies.get("light_mode", "off")
    course_name = request.args.get("course", "")
    new_dict = dict()
    if "View All" in new_dict:
        del new_dict["View All"]
    temp_list = []
    if not course_name or course_name == "View All":
        return render_template(template, course_link=total_list, c=course_dictonary, f = f, light = light)
    for i in total_list:
        if i['course_name'] == course_name:
            f = course_name
            temp_list.append(i)
            new_dict["View All"] = True
            new_dict |= course_dictonary
    return render_template(template, course_link=temp_list, c=new_dict, f = f, light = light)

@app.route('/', methods = ['GET','POST'])

def home():
    course_dictonary, total_list = loadAssignments()
    f = ""
    light = request.cookies.get("light_mode", "off") 
    course_name = request.args.get("course", "")
    if not course_name or course_name == "View All":
        return render_template('unified.html', course_link=total_list, c=course_dictonary, f = f, light = light)
            
    return apply_filter()

@app.route('/canvas', methods = ['GET','POST'])

def canvas():
    course_dictonary, total_list = loadAssignments()
    f = ""
    light = request.cookies.get("light_mode", "off") 
    course_name = request.args.get("course", "")
    if not course_name or course_name == "View All":
        return render_template('canvas.html', course_link=total_list, c=course_dictonary, f = f, light = light)
            
    return apply_filter()

@app.route('/classroom', methods = ['GET','POST'])

def classroom():
    course_dictonary, total_list = loadAssignments()
    f = ""
    light = request.cookies.get("light_mode", "off") 
    course_name = request.args.get("course", "")
    if not course_name or course_name == "View All":
        return render_template('classroom.html', course_link=total_list, c=course_dictonary, f = f, light = light)
            
    return apply_filter()

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)

