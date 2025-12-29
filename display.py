from flask import Flask, render_template, request
from logic import *
import requests
app = Flask(__name__)


#creates a page which is acessed through the / path  this is the homepage which displays the unified assignments
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

#creates a page with the path /canvas which displays solely canvas asignments
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

#creates a page with the path /classroom which displays solely classroom asignments
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

