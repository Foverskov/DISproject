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

    page = ""
    page += """
    <style>
     table, th, td {
    border: 1px solid black;
    border-collapse: collapse;
    }
    </style>
    """
    
    # Oversigt medlemmer
    page += """
    <a href="/">Tilbage</a>
    <h1>Medlemmer</h1>
    <form action="add_medlem" method = "POST">
        <table>
            <tr>
                <th><input type = "submit" value = "Tilføj" /></th>
                <th></th>
                <th> <input type = "text" name = "cpr" /></th>
                <th><input type = "text" name = "name" /> </th>
                <th><input type = "text" name = "age" /> </th>
                <th><input type = "text" name = "addr" /></th>
                <th><input type = "text" name = "tel" /></th>
                <th><input type = "text" name = "email" /></th>
                <th></th>
            </tr>
    </form>
            <tr>
                <th>DELETE</th>
                <th>Medlems ID</th>
                <th>CPR</th>
                <th>Navn</th>
                <th>Alder</th>
                <th>Adresse</th>
                <th>Telefon</th>
                <th>Email</th>
                <th>Se hold</th>
            </tr>
    <form action="remove_medlem" method = "POST">
    """

    for row in members:
        page += f"""<tr><td><input type = "submit" name = "{row[0]}" value = "X"/></td>"""
        for col in row:
            page += "<td>" + str(col) + "</td>"
        page += f"""<td><a href="medlem/{row[0]}">Se hold</a></td>"""
        page += "</tr>"

    page += "</form></table>"

    # Oversigt Employees
    page += """
    <h1>Trænere</h1>
    <form action="add_employee" method = "POST">
        <table>
            <tr>
                <th><input type = "submit" value = "Tilføj" /></th>
                <th></th>
                <th> <input type = "text" name = "cpr" /></th>
                <th><input type = "text" name = "name" /> </th>
                <th><input type = "text" name = "age" /> </th>
                <th><input type = "text" name = "addr" /></th>
                <th><input type = "text" name = "tel" /></th>
                <th><input type = "text" name = "email" /></th>
            </tr>
    </form>
            <tr>
                <th>DELETE</th>
                <th>Employee ID</th>
                <th>CPR</th>
                <th>Navn</th>
                <th>Alder</th>
                <th>Adresse</th>
                <th>Telefon</th>
                <th>Email</th>
                <th>Se hold</th>
            </tr>
    <form action="remove_employee" method = "POST">
    """

    for row in employees:
        page += f"""<tr><td><input type = "submit" name = "{row[0]}" value = "X"/></td>"""
        for col in row:
            page += "<td>" + str(col) + "</td>"
        page += f"""<td><a href="traener/{row[0]}">Se hold</a></td>"""
        page += "</tr>"

    page += "</form></table>"

    cur.close()
    conn.close()

    return page

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

    page = ""
    page += """
    <style>
        table, th, td {
        border: 1px solid black;
        border-collapse: collapse;
        }
    </style>
    """

    page += f"""
    <a href="/medlemmer">Tilbage</a>
    <h1>Medlem: {name[0][0]} ({name[0][1]})</h1>
    <table>
        <tr>
            <th>Hold ID</th>
            <th>Hold navn</th>
            <th>Tidspunkt</th>
            <th>Pris</th>
            <th>Start dato</th>
            <th>Slut dato</th>
        </tr>
    """

    for row in rows:
        page += "<tr>"
        page += f"<td>{row[0]}</td>"
        page += f"<td>{row[1]}</td>"
        page += f"<td>{row[2]}</td>"
        page += f"<td>{row[3]}</td>"
        page += f"<td>{str(datetime.fromtimestamp(int(row[4])).strftime('%d/%m-%Y'))}</td>"
        page += f"<td>{str(datetime.fromtimestamp(int(row[5])).strftime('%d/%m-%Y'))}</td>"
        page += "</tr>"
    
    return page

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

    page = ""
    page += """
    <style>
        table, th, td {
        border: 1px solid black;
        border-collapse: collapse;
        }
    </style>
    """

    page += f"""
    <a href="/medlemmer">Tilbage</a>
    <h1>Træner: {name[0][0]} ({name[0][1]})</h1>
    <table>
        <tr>
            <th>Hold ID</th>
            <th>Hold navn</th>
            <th>Tidspunkt</th>
        </tr>
    """

    for row in rows:
        page += "<tr>"
        page += f"<td>{row[0]}</td>"
        page += f"<td>{row[1]}</td>"
        page += f"<td>{row[2]}</td>"
        page += "</tr>"
    
    return page


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

    page = ""
    page += """
    <style>
     table, th, td {
    border: 1px solid black;
    border-collapse: collapse;
    }
    </style>
    """

    page += """
    <a href="/">Tilbage</a>
    <h1>Hold</h1>
        <table>
            <form action="add_team" method = "POST">
            <tr>
                <th></th>
                <th><input type = "text" name = "name" /></th>
                <th><input type = "text" name = "time" /></th>
                <th><input type = "text" name = "price" /></th>
                <th></th>
                <th><input type = "submit" value = "Tilføj" /></th>
            </tr>
            </form>

            <tr>
                <th>Hold ID</th>
                <th>Holdnavn</th>
                <th>Tid</th>
                <th>Pris</th>
                <th>Medlemmer</th>
                <th>Detaljer</th>
            </tr>
    <form action="team_details" method = "POST">
    """

    for row in rows:
        page += "<tr>"
        for col in row:
            page += "<td>" + str(col) + "</td>"
        page += f"""<td><input type = "submit" name = "{row[0]}" value = "Detaljer"/></td>"""
        page += "</tr>"

    page += "</form></table>"

    cur.close()
    conn.close()

    return page

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



    page = ""
    page += """
    <style>
        table, th, td {
        border: 1px solid black;
        border-collapse: collapse;
        }
    </style>
    """

    page += f"""
    <a href="/hold">Tilbage</a>
    <h1>Hold {team_name}</h1>
    <form action="delete_team" method = "POST">
    <input type = "hidden" name = "tid" value = "{team_id}" />
    <input type = "submit" value = "Slet hold" />
    </form>"""

    page += f"""
    <form action="add_team_member" method = "POST">
    <input type = "hidden" name = "tid" value = "{team_id}" />
    <input type = "hidden" name = "name" value = "" />
    <input type = "submit" value = "Tilføj medlem" />
    </form>

     <table>
        <tr>
            <th>Fjern</th>
            <th>Medlems ID</th>
            <th>Startdato</th>
            <th>Slutdato</th>
            <th>Navn</th>
            <th>Alder</th>
            <th>CPR</th>
            <th>Adresse</th>
            <th>Telefon</th>
            <th>Email</th>
        </tr>
        <form action="remove_team_member" method = "POST">
    """

    for row in rows:
            page += f"""<tr><td><input type = "submit" name = "{row[0]}" value = "X"/></td>"""
            page += "<td>" + str(row[0]) + "</td>"
            page += "<td>" + str(datetime.fromtimestamp(int(row[1])).strftime('%d/%m-%Y')) + "</td>"
            page += "<td>" + str(datetime.fromtimestamp(int(row[2])).strftime('%d/%m-%Y')) + "</td>"
            page += "<td>" + str(row[3]) + "</td>"
            page += "<td>" + str(row[4]) + "</td>"
            page += "<td>" + str(row[5]) + "</td>"
            page += "<td>" + str(row[6]) + "</td>"
            page += "<td>" + str(row[7]) + "</td>"
            page += "<td>" + str(row[8]) + "</td>"
            page += "</tr>"
    page += "</form></table>"


    # Holdets trænere
    page += f"""
    <h1>Trænere for {team_name}</h1>

    <table>
        <tr>
            <form action="add_team_employee" method = "POST">
            <th><input type = "submit" value = "Tilføj" /></th>
            <th><input type = "text" name = "eid" /></th>
            <input type = "hidden" name = "tid" value = "{team_id}" />
            </form>
        </tr>
        <tr>
            <th>Fjern</th>
            <th>Træner ID</th>
            <th>Navn</th>
            <th>Alder</th>
            <th>Telefon</th>
            <th>Email</th>
        </tr>
        <form action="remove_team_employee" method = "POST">    
    """

    for row in team_employee:
            page += f"""<tr><td><input type = "submit" name = "{row[0]}" value = "X"/></td>"""
            page += "<td>" + str(row[0]) + "</td>"
            page += "<td>" + str(row[1]) + "</td>"
            page += "<td>" + str(row[2]) + "</td>"
            page += "<td>" + str(row[3]) + "</td>"
            page += "<td>" + str(row[4]) + "</td>"
            page += "</tr>"
    page += "</form></table>"


    cur.close()
    conn.close()

    return page

@app.route('/delete_team', methods=['POST'])
def delete_team():
    form_data = request.form
    team_id = form_data['tid']

    conn = connect_db()
    cur = conn.cursor()
    # TODO: Dette kan nok gøres smartere
    cur.execute(f"DELETE FROM Memberships WHERE tid = {team_id};")
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

    page = ""

    page += f"""
    <h1>Tilføj medlem til hold: {team_id}</h1>
    <h1>Tilføj medlem til hold</h1>
    <table>
        <tr>
            <form action = "add_team_member" method = "POST" >
            <input type = "hidden" name = "tid" value = "{team_id}" />
            <input type = "submit" value = "SØG" />
            <input type = "text" name = "name" />
            
            </form>
        </tr>
    </table>

    <table>
        <form action="add_member_to_team" method = "POST">
        <input type = "text" name = "from_date" />
        <input type = "text" name = "to_date" />

    """
    for row in rows:
        page += f"""<tr><td>
        <input type = "hidden" name = "mid" value = "{row[0]}" />
        <input type = "hidden" name = "tid" value = "{team_id}" />
        <input type = "submit" name = "Tilføj" value = "Tilføj" />
        </td>
        """
        page += "<td>" + str(row[0]) + "</td>"
        page += "<td>" + str(row[1]) + "</td>"
        page += "<td>" + str(row[2]) + "</td>"
        page += "<td>" + str(row[3]) + "</td>"
        page += "<td>" + str(row[4]) + "</td>"
        page += "<td>" + str(row[5]) + "</td>"
        page += "<td>" + str(row[6]) + "</td>"
        page += "</tr>"

    page += """
            </form>
    </table>
    """

    cur.close()
    conn.close() 
    
    return page 

@app.route('/add_member_to_team', methods=['POST'])
def add_member_to_team():
    form_data = request.form
    from_date = datetime.strptime(form_data['from_date'], '%d/%m/%Y').strftime("%s")
    to_date = datetime.strptime(form_data['to_date'], '%d/%m/%Y').strftime("%s")

    conn = connect_db()
    cur = conn.cursor()
    cur.execute(f"INSERT INTO Memberships VALUES ({form_data['mid']}, {form_data['tid']}, {from_date}, {to_date});")
    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for('hold'))

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

    page = ""
    page += """
    <style>
     table, th, td {
    border: 1px solid black;
    border-collapse: collapse;
    }
    </style>
    """
    page += """
    <a href="/">Tilbage</a>
    <h1>Faciliteter</h1>
    """

    # Facilitet oversigt
    page += """
    <h2>Faciliteter</h2>
    <table>
        <form action="add_facility" method = "POST">
        <tr>
            <th><input type = "text" name = "addr" /></th>
            <th><input type = "text" name = "name" /></th>
            <th><input type = "text" name = "description" /></th>
            <th><input type = "submit" value = "Tilføj"/></th>
        </tr>
        </form>
        <tr>
            <th>Adresse</th>
            <th>Navn</th>
            <th>Beskrivelse</th>
            <th>Bookings</th>
        <tr>
        <form action="facility_details" method = "POST">
    """
    for row in facilities:
            page += "<td>" + str(row[0]) + "</td>"
            page += "<td>" + str(row[1]) + "</td>"
            page += "<td>" + str(row[2]) + "</td>"
            page += "<td><input type = 'submit' value = 'Book' name = '" + str(row[0]) + "'/></td>"
            page += "</tr>"
    page += "</form></table>"

    # Bookings oversigt

    page += """
    <h2>Bookings</h2>
    <form action="faciliteter" method = "GET">
    filter from: <input type = "text" name = "from_date" />
    filter to: <input type = "text" name = "to_date" />
    <input type = "submit" value = "Filtrer"/>
    </form>
    """

    if request.method == 'GET' and request.args.get('from_date', '') != '' and request.args.get('to_date', '') != '':
        page += "<p>Filtrer fra: " + request.args.get('from_date', '') + " Til: " + request.args.get('to_date', '') + "</p>"

    page += """
    <table>
        <tr>
            <th>Adresse</th>
            <th>Facilitet</th>
            <th>Hold</th>
            <th>Start</th>
            <th>Slut</th>
        <tr>
    """
    for row in bookings:
            page += "<td>" + str(row[0]) + "</td>"
            page += "<td>" + str(row[1]) + "</td>"
            page += "<td>" + str(row[2]) + "</td>"
            page += "<td>" + str(datetime.fromtimestamp(int(row[3])).strftime('%d/%m-%Y %H:%M')) + "</td>"
            page += "<td>" + str(datetime.fromtimestamp(int(row[4])).strftime('%d/%m-%Y %H:%M')) + "</td>"
            page += "</tr>"

    page += "</table>"

    cur.close()
    conn.close()

    return page

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

    page = ""
    page += """
    <style>
        table, th, td {
        border: 1px solid black;
        border-collapse: collapse;
        }
    </style>
    """
    page += f"""
    <a href="/faciliteter">Tilbage</a>
    <h1>Facilitet på {vej}</h1>
    
    <form action="delete_facility" method = "POST">
        <input type = "hidden" name = "address" value = "{vej}" />
        <input type = "submit" value = "Slet"/>
    </form>

    <table>
    <form action="add_booking" method = "POST">
        <tr>
            <td></td>
            <td><input type = "text" name = "tid" /></td>
            <input type = "hidden" name = "address" value = "{vej}" />
            <td><input type = "text" name = "from_date" /></td>
            <td><input type = "text" name = "to_date" /></td>
            <td><input type = "submit" value = "Tilføj"/></td>
        </tr>
    </form>
        <tr>
            <th>Hold navn</th>
            <th>Hold id</th>
            <th>Start tidspunkt</th>
            <th>Slut tidspunkt</th>
            <th>Slet</th>
        <tr>
    <form action="delete_booking" method = "POST">
    """

    for row in bookings:
        page += "<tr>"
        page += f"<td>{row[0]}</td>"
        page += f"<td>{row[1]}</td>"
        page += f"<td>{str(datetime.fromtimestamp(int(row[2])).strftime('%d/%m-%Y %H:%M'))}</td>"
        page += f"<td>{str(datetime.fromtimestamp(int(row[3])).strftime('%d/%m-%Y %H:%M'))}</td>"
        page += f"""<td><input type = "submit" name = "{(vej,row[1],row[2],row[3])}" value = "X"/></td>"""
        page += "</tr>"
    
    page += "</form></table>"

    conn.commit()
    cur.close()
    conn.close()

    return page

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