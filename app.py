from flask import Flask, render_template, request, redirect, url_for, flash
import psycopg2
import configparser
import os
from datetime import datetime

# python -m flask --app app.py run

app = Flask(__name__)

def connect_db():
    # Connect to the database
    if not os.path.isfile('config.ini'):
        raise Exception('config.ini not found. Please create it from config.ini.example')
    config = configparser.ConfigParser()
    config.read('config.ini')
    db = config['DB_LOGIN']
    conn = psycopg2.connect(database=db['database'], user=db['user'],
                            password=db['password'], host=db['host'], port=db['port'])
    return conn

# ERROR HANDLING ValueError
@app.errorhandler(ValueError)
def handle_value_error(e):
    return render_template('error.html'), 500

# ERROR HANDLING psycopg2.errors.ForeignKeyViolation
@app.errorhandler(psycopg2.errors.ForeignKeyViolation)
def handle_foreign_key_violation(e):
    return render_template('error.html'), 500

# ERROR HANDLING psycopg2.errors.UniqueViolation
@app.errorhandler(psycopg2.errors.UniqueViolation)
def handle_unique_violation(e):
    return render_template('error.html'), 500


@app.route('/')
def index():
    page = render_template('index.html')
    return page

"""
Medlemmer
Data: 
    - Members: mid, cpr, name, age, addr, tel, email
    - Employees: mid, cpr, name, age, addr, tel, email
"""
@app.route('/medlemmer')
def medlemmer():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM members")
    members = cur.fetchall()
    cur.execute("SELECT * FROM employees;")
    employees = cur.fetchall()


    return render_template('medlemmer.html', members=members, employees=employees)

@app.route('/traenere')
def traenere():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM employees;")
    employees = cur.fetchall()

    return render_template('træner.html', employees=employees)

@app.route('/add_medlem', methods=['POST'])
def add_medlem():
    form_data = request.form
    print(form_data)

    conn = connect_db()
    cur = conn.cursor()

    
    cur.execute(f"INSERT INTO members VALUES (DEFAULT, '{form_data['cpr']}', '{form_data['name']}', {int(form_data['age'])}, '{form_data['addr']}', '{form_data['tel']}', '{form_data['email']}');")
    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for('medlemmer')) 


@app.route('/remove_medlem', methods=['POST'])
def remove_medlem():
    form_data = request.form
    mid = list(form_data.keys())[0]

    conn = connect_db()
    cur = conn.cursor()
    cur.execute(f"DELETE FROM members WHERE mid = {mid};")
    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for('medlemmer'))

@app.route('/add_employee', methods=['POST'])
def add_employee():
    form_data = request.form
    print(form_data)

    conn = connect_db()
    cur = conn.cursor()
    cur.execute(f"INSERT INTO employees VALUES (DEFAULT, '{form_data['cpr']}', '{form_data['name']}', {int(form_data['age'])}, '{form_data['addr']}', '{form_data['tel']}', '{form_data['email']}');")
    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for('medlemmer'))

@app.route('/remove_employee', methods=['POST'])
def remove_employee():
    form_data = request.form
    mid = list(form_data.keys())[0]

    conn = connect_db()
    cur = conn.cursor()
    cur.execute(f"DELETE FROM employees WHERE eid = {mid};")
    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for('medlemmer'))

# Custom filter to convert timestamps to dates
@app.template_filter('timestamp_to_date')
def timestamp_to_date(timestamp):
    return datetime.fromtimestamp(int(timestamp)).strftime('%d/%m-%Y')

@app.route('/medlem/<mid>')
def medlem(mid):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute(f"""
    SELECT t.tid, t.name, t.time, t.price, ms.from_date, ms.to_date
    FROM Teams t
    LEFT JOIN Memberships ms ON t.tid = ms.tid
    LEFT JOIN Members m ON ms.mid = m.mid
    WHERE m.mid = {mid};
    """)
    rows = cur.fetchall()
    cur.execute(f"SELECT name, mid FROM members WHERE mid = {mid};")
    name = cur.fetchall()

    cur.close()
    conn.close()

    return render_template('medlem.html', rows=rows, name=name)

@app.route('/traener/<eid>')
def trainer(eid):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute(f"""
    SELECT t.tid, t.name, t.time
    FROM Teams t
    LEFT JOIN Manage m ON t.tid = m.tid
    LEFT JOIN Employees e ON m.eid = e.eid
    WHERE e.eid = {eid};
    """)
    rows = cur.fetchall()
    cur.execute(f"SELECT name, eid FROM Employees WHERE eid = {eid};")
    name = cur.fetchall()

    cur.close()
    conn.close()

    return render_template('traener.html', rows=rows, name=name)

"""
Hold
Data:
    - Teams: tid, name
    - Memberships:
    - Members: mid(count)
    - Manages:
    - Employees: name

Detalje underside.
Data:
    - Members: mid, name
    - In: from, to
"""

@app.route('/hold')
def hold():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
    SELECT t.tid, t.name, t.time, t.price, COUNT(m.mid)
    FROM Teams t
    LEFT JOIN Memberships ms ON t.tid = ms.tid
    LEFT JOIN Members m ON ms.mid = m.mid
    GROUP BY t.tid, t.name;
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    return render_template('hold.html', rows=rows)

@app.route('/add_team', methods=['POST'])
def add_team():
    form_data = request.form
    conn = connect_db()
    cur = conn.cursor()
    cur.execute(f"INSERT INTO teams (tid, name, time, price) VALUES (DEFAULT, '{form_data['name']}', '{form_data['time']}', {int(form_data['price'])});")
    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for('hold'))

@app.route('/team_details', methods=['POST'])
def team_details():
    form_data = request.form
    team_id = list(form_data.keys())[0]

    conn = connect_db()
    cur = conn.cursor()
    cur.execute(f"""
                SELECT m.mid, ms.from_date, ms.to_date, m.name, m.age, m.ssn, m.address, m.telephone, m.email FROM Members m 
                LEFT JOIN Memberships ms ON m.mid = ms.mid 
                WHERE ms.tid = {team_id};
                """)
    rows = cur.fetchall()
    cur.execute(f"""
                SELECT t.name FROM Teams t
                WHERE t.tid = {team_id}; 
                """)
    team_name = cur.fetchall()[0][0]
    cur.execute(f"""
                SELECT e.eid, e.name, e.age, e.telephone, e.email 
                FROM Employees e LEFT JOIN Manage m ON e.eid = m.eid 
                WHERE m.tid = {team_id};
                """)
    team_employee = cur.fetchall()

    cur.close()
    conn.close()

    return render_template('team_details.html', rows=rows, team_name=team_name, team_employee=team_employee, team_id=team_id, datetime=datetime)


@app.route('/delete_team', methods=['POST'])
def delete_team():
    form_data = request.form
    team_id = form_data['tid']

    conn = connect_db()
    cur = conn.cursor()
    # TODO: Dette kan nok gøres smartere
    cur.execute(f"DELETE FROM Memberships WHERE tid = {team_id};")
    cur.execute(f"DELETE FROM Manage WHERE tid = {team_id};")
    cur.execute(f"DELETE FROM Teams WHERE tid = {team_id};")
    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for('hold'))

@app.route('/add_team_member', methods=['POST'])
def add_team_member():
    conn = connect_db()
    cur = conn.cursor()
    form_data = request.form

    team_id = form_data['tid']
    mname = form_data['name']

    cur.execute(f"""
            SELECT mid, name, age, ssn, address, telephone, email FROM members 
            WHERE name LIKE '{mname}%' ;
            """)
    rows = cur.fetchall()
    
    #! Datoer skal være i format dd/mm-yyyy
    #from_date = datetime.strptime(form_data['from_date'], '%d/%m-%Y').strftime("%s")
    #to_date = datetime.strptime(form_data['to_date'], '%d/%m-%Y').strftime("%s")

    cur.close()
    conn.close() 
    
    return render_template('add_team_member.html', rows=rows, team_id = team_id)

@app.route('/add_member_to_team', methods=['POST'])
def add_member_to_team():
    form_data = request.form
    from_date = datetime.strptime(form_data['from_date'], '%d/%m-%Y').strftime("%s")
    to_date = datetime.strptime(form_data['to_date'], '%d/%m-%Y').strftime("%s")
    
    # Retrieve member ID and team ID from the form data
    member_id = form_data.get('mid')
    team_id = form_data.get('tid')

    conn = connect_db()
    cur = conn.cursor()

    # Check if member ID and team ID are valid
    if member_id is not None and team_id is not None:
        cur.execute(f"INSERT INTO Memberships VALUES ({member_id}, {team_id}, {from_date}, {to_date});")
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('hold'))
    else:
        # Handle the case where member ID or team ID is missing
        error_message = "Invalid member ID or team ID."
        return render_template('error.html', error=error_message)

@app.route('/add_team_employee', methods=['POST'])
def add_team_employee():
    form_data = request.form

    conn = connect_db()
    cur = conn.cursor()


    cur.execute(f"""
                INSERT INTO Manage (eid, tid)
                VALUES ({form_data['eid']}, {form_data['tid']});
                """)

    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for('hold'))

@app.route('/remove_team_member', methods=['POST'])
def remove_team_member():
    form_data = request.form

    conn = connect_db()
    cur = conn.cursor()
    cur.execute(f"DELETE FROM Memberships WHERE mid = {list(form_data.keys())[0]};")
    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for('hold'))

@app.route('/remove_team_employee', methods=['POST'])
def remove_team_employee():
    form_data = request.form

    conn = connect_db()
    cur = conn.cursor()
    cur.execute(f"DELETE FROM Manage WHERE eid = {list(form_data.keys())[0]};")
    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for('hold'))

"""
Faciliteter
Data:
    - Faciliteter: name, addr
    - Bookings: from, to, tid, addr
    - Teams: tid, name

Features:
    - Filtrering på dato, addresse, availablity
"""

@app.route('/faciliteter')
def faciliteter():
    conn = connect_db()
    cur = conn.cursor()

    if request.method == 'GET' and request.args.get('from_date', '') != '' and request.args.get('to_date', '') != '':
        booking_from_date = datetime.strptime(request.args.get('from_date', ''), '%d/%m-%Y %H:%M').strftime("%s")
        booking_to_date = datetime.strptime(request.args.get('to_date', ''), '%d/%m-%Y %H:%M').strftime("%s")
    else:
        booking_from_date = -9223372036854775807 # Min int
        booking_to_date = 9223372036854775807 # Max int

    cur.execute(f"""
        SELECT f.address, f.name, t.name, b.from_date, b.to_date \
        FROM Bookings b \
        JOIN Teams t ON b.tid = t.tid \
        JOIN Facilities f ON b.address = f.address \
        WHERE ({booking_from_date} <= b.from_date AND b.from_date <= {booking_to_date})  \
        OR ({booking_from_date} <= b.to_date AND b.to_date <= {booking_to_date}) ; \
    """)
    bookings = cur.fetchall()
    cur.execute("SELECT * FROM Facilities;")
    facilities = cur.fetchall()

    cur.close()
    conn.close()

    return render_template('Faciliteter.html', bookings =bookings,facilities = facilities, booking_from_date = booking_from_date,booking_to_date=booking_to_date)

@app.route('/add_facility', methods=['POST'])
def add_facility():
    form_data = request.form
    conn = connect_db()
    cur = conn.cursor()

    cur.execute(f"INSERT INTO Facilities (address, name, description) VALUES ('{form_data['addr']}', '{form_data['name']}', '{form_data['description']}');")
    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for('faciliteter'))

@app.route('/facility_details', methods=['POST'])
def facility_details():
    form_data = request.form
    vej = list(form_data.keys())[0]

    conn = connect_db()
    cur = conn.cursor()

    cur.execute(f"""
                SELECT t.name, t.tid, b.from_date, b.to_date \
                FROM Bookings b \
                JOIN Teams t ON b.tid = t.tid \
                WHERE b.address = '{vej}'; \
                """)
    bookings = cur.fetchall()

    conn.commit()
    cur.close()
    conn.close()
    return render_template('Facility_details.html' ,vej=vej, bookings=bookings,)

@app.route('/delete_facility', methods=['POST'])
def delete_facility():
    form_data = request.form
    address = form_data['address']

    conn = connect_db()
    cur = conn.cursor()
    # TODO: Dette kan nok gøres smartere
    cur.execute(f"DELETE FROM Bookings WHERE address = '{address}';")
    cur.execute(f"DELETE FROM Facilities WHERE address = '{address}';")
    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for('faciliteter'))

@app.route('/add_booking', methods=['POST'])
def add_booking():
    form_data = request.form
    conn = connect_db()
    cur = conn.cursor()

    from_date = datetime.strptime(form_data['from_date'], '%d/%m-%Y %H:%M').strftime("%s")
    to_date = datetime.strptime(form_data['to_date'], '%d/%m-%Y %H:%M').strftime("%s")

    cur.execute(f"INSERT INTO Bookings (tid, address, from_date, to_date) VALUES ('{form_data['tid']}', '{form_data['address']}', '{from_date}', '{to_date}');")
    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for('faciliteter'))

@app.route('/delete_booking', methods=['POST'])
def delete_booking():
    form_data = request.form
    conn = connect_db()
    cur = conn.cursor()

    addr, tid, from_time, to_time = eval(list(form_data.keys())[0])

    cur.execute(f"DELETE FROM Bookings WHERE tid = {tid} AND address = '{addr}' AND from_date = {from_time} AND to_date = {to_time};")
    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for('faciliteter'))