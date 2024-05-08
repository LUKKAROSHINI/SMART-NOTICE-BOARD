from flask import Flask, render_template, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
from datetime import datetime
from sqlalchemy import desc, text

app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:admin@localhost:3306/klef_cseh'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:rosh@localhost:3306/klef_cseh'
db = SQLAlchemy(app)
app.config['SECRET_KEY'] = 'klcseh'
class Empmaster(db.Model):
    empid = db.Column(db.Integer, primary_key=True)
    epassword = db.Column(db.String(100))
    estatus = db.Column(db.Integer)

class Emptask(db.Model):
    empid = db.Column(db.Integer, primary_key=True)
    taskdatetime = db.Column(db.DateTime, default='2001-01-01 00:00:00')
    taskvenue = db.Column(db.String(70), nullable=True)
    taskdetails = db.Column(db.String(70), nullable=True)
    taskupdatedon = db.Column(db.DateTime, default='2001-01-01 00:00:00')
    taskupdatedby = db.Column(db.Integer, default=1)

@app.route('/')
def index():
    return render_template('home page.html')

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return render_template('index.html')
        # return 'Logged in as {}'.format(session['username'])
    else:
        return render_template('home page.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return render_template('home page.html')


@app.route('/login', methods=['POST'])
def login():
    # Get form data
    username = request.form.get('username')
    password = request.form.get('password')

    # Perform authentication (replace this with your authentication logic)
    if username == 'admin' and password == 'password':
        session['username'] = 'admin'
        success = True
        message = 'Login successful!'
    else:
        success = False
        message = 'Incorrect username or password.'

    # Create response data
    response_data = {
        'success': success,
        'message': message
    }

    # Return response as JSON
    return jsonify(response_data)

@app.route('/uploadUserAccount', methods=['POST'])
def uploadUserAccount():
    file = request.files['file']
    if file:
        df = pd.read_excel(file)
        expected_headers = ['empid', 'epassword', 'estatus']
        actual_headers = df.columns.tolist()
        if not all(header in actual_headers for header in expected_headers):
            missing_headers = [header for header in expected_headers if header not in actual_headers]
            return "Not a valid file, Kindly upload the file with the following structure<br>'empid', 'epassword', 'estatus'"

        for index, row in df.iterrows():
            employee = Empmaster.query.filter_by(empid=row['empid']).first()
            if employee:
                # If record exists, update it
                employee.epassword = row['epassword']
                employee.estatus = row['estatus']
            else:
                empmaster = Empmaster(empid=row['empid'], epassword=row['epassword'],estatus=row['estatus'])
                db.session.add(empmaster)
        db.session.commit()
        res=  'File uploaded and data stored successfully!'
        return render_template('index.html', success_msg2=res)
    else:
        res = 'File uploaded failed!'
        return render_template('index.html', msg2=res)


@app.route('/addUserAccount', methods=['POST'])
def addUserAccount():
    empid = request.form.get('empid')  # Assuming empid is sent in the request form
    epassword = request.form.get('epassword')  # Assuming epassword is sent in the request form

    if empid and epassword:  # Check if empid and epassword are not None or empty
        employee = Empmaster.query.filter_by(empid=empid).first()
        if employee:
            # If record exists, update it
            employee.epassword = epassword
            employee.estatus = 1
        else:
            empmaster = Empmaster(empid=empid, epassword=epassword, estatus=1)
            db.session.add(empmaster)

        db.session.commit()
        res = 'Record updated successfully!'
        return render_template('index.html', success_msg1=res)
    else:
        res = 'Process Failed, Try again.'
        return render_template('index.html', msg1=res)

#Group by Excel
@app.route('/uploadTask', methods=['POST'])
def uploadTask():
    file = request.files['file1']
    if file:
        df = pd.read_excel(file)
        expected_headers = ['empid', 'taskdate', 'tasktime', 'taskvenue', 'taskdetails','taskupdatedby']
        actual_headers = df.columns.tolist()
        if not all(header in actual_headers for header in expected_headers):
            missing_headers = [header for header in expected_headers if header not in actual_headers]
            res = "Not a valid file, Kindly upload the file with the following structure<br>'empid', 'taskdate', 'tasktime', 'taskvenue', 'taskdetails','taskupdatedby'"
            return render_template('index.html', msg4=res)

        for index, row in df.iterrows():
            date_str = row['taskdate']
            time_str = row['tasktime']
            date_str = str(date_str)[:10]
            datetime_str = f'{date_str} {time_str}'
            datetime_value = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')

            emptask1 = Emptask(empid=row['empid'],
            taskdatetime = datetime_value ,
            taskvenue = row['taskvenue'],
            taskdetails = row['taskdetails'],
            taskupdatedby = row['empid'],
            taskupdatedon=datetime.now()
            )
            db.session.add(emptask1)
        db.session.commit()
        # return 'File uploaded and data stored successfully!'
        res = 'Record updated successfully!'
        return render_template('index.html', success_msg4=res)

    else:
        res = 'Process Failed, Try again.'
        return render_template('index.html', msg4=res)

#individual
@app.route('/addTask', methods=['POST'])
def addTask():
    empid = request.form.get('empid')
    taskdate = request.form.get('taskdate')
    tasktime = request.form.get('tasktime')
    taskvenue = request.form.get('taskvenue')
    taskdetails = request.form.get('taskdetails')
    print("addTask   >" +  str(empid)  + ">" + str(taskdate) + ">" + str(tasktime) )
    if empid and taskdate and tasktime and taskvenue and taskdetails:
        try:
            datetime_str = f'{taskdate} {tasktime}'
            datetime_value = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M')
            print("datetime_value   >" + str(datetime_value))
            Emptask1 = Emptask(empid=int(empid),
                               taskdatetime=datetime_value,
                               taskvenue=taskvenue,
                               taskdetails=taskdetails,
                               taskupdatedby=int(empid)
                               )
            db.session.add(Emptask1)
            db.session.commit()
            res = 'Task updated successfully!'
            return render_template('index.html', success_msg3=res)
        except ValueError as e:
            res = 'Process Failed. Try again.'
            return render_template('index.html', msg3=str(e))
    else:
        res = 'Missing/Mismatch field.'
        return render_template('index.html', msg3=res)



@app.route('/getAllTasks')
def getAllTasks():
    tasks = Emptask.query.order_by(desc(Emptask.taskdatetime)).all()
    tasks_list = []
    for task in tasks:
        task_data = {
            'empid': task.empid,
            'taskdatetime': task.taskdatetime.strftime('%Y-%m-%d %H:%M:%S'),
            'taskvenue': task.taskvenue,
            'taskdetails': task.taskdetails,
            'taskupdatedon': task.taskupdatedon.strftime('%Y-%m-%d %H:%M:%S'),
            'taskupdatedby': task.taskupdatedby
        }
        tasks_list.append(task_data)
    # Return tasks as JSON data
    return jsonify(tasks_list)

@app.route('/getTasks/<int:userid>')
def get_tasks(userid):
    empid = userid
    if empid is None:
        return 'empid parameter is required', 400
    print("User Id : " + str(userid))
    # Construct the SQL query as a string
    sql_query = text("SELECT * FROM Emptask WHERE empid = :userid")
    result = db.session.execute(sql_query, {'userid': userid})
    tasks = result.fetchall()

    tasks_list = []
    for task in tasks:
        task_data = {
            'empid': task.empid,
            'taskdatetime': task.taskdatetime.strftime('%Y-%m-%d %H:%M:%S'),
            'taskvenue': task.taskvenue,
            'taskdetails': task.taskdetails,
            'taskupdatedon': task.taskupdatedon.strftime('%Y-%m-%d %H:%M:%S'),
            'taskupdatedby': task.taskupdatedby
        }
        tasks_list.append(task_data)
    # res = jsonify(tasks_list) #res = 'Missing/Mismatch field.'
    active_tab = 'viewData'
    return render_template('index.html', tasks_list=tasks_list,active_tab=active_tab)

if __name__ == '__main__':
    app.run(debug=True)

# $(document).ready(function()
# {
# // Define
# the
# userid
# var
# userid = 123; // Replace
# with the actual userid
#
# // Make AJAX request to fetch tasks data with userid parameter
# $.ajax({
# url: '/getTasks/' + userid,
# type: 'GET',
# success: function(data)
# {
# // Iterate
# over
# each
# task and append
# to
# tasks - container
# $.each(data, function(index, task)
# {
#     var
# taskHtml = '<div class="task">';
# taskHtml += '<p><strong>Employee ID:</strong> ' + task.empid + '</p>';
# taskHtml += '<p><strong>Task Date Time:</strong> ' + task.taskdatetime + '</p>';
# taskHtml += '<p><strong>Task Venue:</strong> ' + task.taskvenue + '</p>';
# taskHtml += '<p><strong>Task Details:</strong> ' + task.taskdetails + '</p>';
# taskHtml += '<p><strong>Task Updated By:</strong> ' + task.taskupdatedby + '</p>';
# taskHtml += '<p><strong>Task Updated On:</strong> ' + task.taskupdatedon + '</p>';
# taskHtml += '</div>';
# $('#tasks-container').append(taskHtml);
# });
# },
# error: function(xhr, status, error)
# {
#     console.error('Error fetching tasks:', error);
# }
# });
# });

