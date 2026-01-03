from flask import Flask, render_template, request, make_response, redirect
from logic import *
import requests



TEMPLATES = {
    '/canvas' : 'canvas.html',
    '/classroom' : 'classroom.html',
    '/' : 'unified.html'



}




first = ""
app = Flask(__name__)




@app.route('/toggle-theme', methods = ['GET','POST'])

def toggle_theme():
    light = request.cookies.get("light_mode", "off")
    print(light)
    resp = make_response(redirect(request.referrer or "/unified"))
    new_value = "off" if light == "on" else "on"
    if light == "on" :   
        resp.set_cookie("light_mode",new_value ,max_age=3600)
    else:
        resp.set_cookie("light_mode", new_value ,max_age=3600)
    return resp

@app.route('/apply-filter', methods = ['GET','POST'])

def apply_filter():
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






    




#creates a page which is acessed through the / path  this is the homepage which displays the unified assignments
@app.route('/', methods = ['GET','POST'])

def home():
    f = ""
    light = request.cookies.get("light_mode", "off") 
    course_name = request.args.get("course", "")
    if not course_name or course_name == "View All":
        return render_template('unified.html', course_link=total_list, c=course_dictonary, f = f, light = light)
            
    return apply_filter()





#creates a page with the path /canvas which displays solely canvas asignments
@app.route('/canvas', methods = ['GET','POST'])


def canvas():
    f = ""
    light = request.cookies.get("light_mode", "off") 
    course_name = request.args.get("course", "")
    if not course_name or course_name == "View All":
        return render_template('canvas.html', course_link=total_list, c=course_dictonary, f = f, light = light)
            
    return apply_filter()

@app.route('/classroom', methods = ['GET','POST'])

#creates a page with the path /classroom which displays solely classroom asignments
def classroom():
    f = ""
    light = request.cookies.get("light_mode", "off") 
    course_name = request.args.get("course", "")
    if not course_name or course_name == "View All":
        return render_template('classroom.html', course_link=total_list, c=course_dictonary, f = f, light = light)
            
    return apply_filter()

if __name__ == '__main__':

    app.run(debug=True, use_reloader=False)

