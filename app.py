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

    # """
    # <h1>Velkommen til vores side</h1>
    # <p>Her kan du se vores medlemmer, ansatte, faciliteter, hold, medlemskaber og bookinger</p>
    # <a href="/medlemmer">Medlemmer</a>
    # <a href="/hold">Holdstruktur</a>
    # <a href="/faciliteter">Faciliteter</a>
    # <a href="/mail">Beskeder</a>
    # """


"""
Medlemmer
Data: 
    - Members: mid, cpr, name, age, addr, tel, email
"""
@app.route('/medlemmer')
def medlemmer():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM members")
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
    <h1>Medlemmer</h1>
    <form action="add_medlem" method = "POST">
        <table>
            <tr>
                <th>
                <input type = "submit" value = "Tilføj" />
                </th>
                <th>
                <input type = "text" name = "mid" />
                </th>
                <th>
                <input type = "text" name = "cpr" />
                </th>
                <th>
                <input type = "text" name = "name" />
                </th>
                <th>
                <input type = "text" name = "age" />
                </th>
                <th>
                <input type = "text" name = "addr" />
                </th>
                <th>
                <input type = "text" name = "tel" />
                </th>
                <th>
                <input type = "text" name = "email" />
                </th>
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
            </tr>
    <form action="remove_medlem" method = "POST">
    """

    for row in rows:
        page += f"""<tr><td><input type = "submit" name = "{row[0]}" value = "X"/></td>"""
        for col in row:
            page += "<td>" + str(col) + "</td>"
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
    cur.execute(f"INSERT INTO members VALUES ({int(form_data['mid'])}, '{form_data['cpr']}', '{form_data['name']}', {int(form_data['age'])}, '{form_data['addr']}', '{form_data['tel']}', '{form_data['email']}');")
    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for('medlemmer'))

@app.route('/remove_medlem', methods=['POST'])
def remove_medlem():
    form_data = request.form
    to_delete = list(form_data.keys())[0]

    conn = connect_db()
    cur = conn.cursor()
    cur.execute(f"DELETE FROM members WHERE mid = {to_delete};")
    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for('medlemmer'))

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
                <th><input type = "text" name = "tid" /></th>
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
    cur.execute(f"INSERT INTO teams (tid, name, time, price) VALUES ({int(form_data['tid'])}, '{form_data['name']}', '{form_data['time']}', {int(form_data['price'])});")
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
    </form>


    <table>
        <tr>
            <form action="add_team_member" method = "POST">
            <th><input type = "submit" value = "Tilføj" /></th>
            <th><input type = "text" name = "mid" /></th>
            <th><input type = "text" name = "from_date" /></th>
            <th><input type = "text" name = "to_date" /></th>
            <input type = "hidden" name = "tid" value = "{team_id}" />
            </form>
        </tr>
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
        for col in row:
            page += "<td>" + str(col) + "</td>"
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
    form_data = request.form

    conn = connect_db()
    cur = conn.cursor()
    cur.execute(f"""
                INSERT INTO Memberships (mid, tid, from_date, to_date) 
                VALUES ({form_data['mid']}, {form_data['tid']}, {form_data['from_date']}, {form_data['to_date']});
                """)
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


    #SELECT f.name AS facility_name, b.from_date, b.to_date
    #FROM Bookings b
    #JOIN Teams t ON b.tid = t.tid
    #JOIN Facilities f ON b.address = f.address;

    #INSERT INTO Bookings (tid, address, from_date, to_date)
    #VALUES (1, 'Hovedvejen 1', 1, 5);

    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT f.name, t.name, b.from_date, b.to_date \
        FROM Bookings b \
        JOIN Teams t ON b.tid = t.tid \
        JOIN Facilities f ON b.address = f.address; \
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
    <h1>Faciliteter</h1>
    <table>
        <tr>
            <th>Facilitet</th>
            <th>Hold</th>
            <th>Start</th>
            <th>Slut</th>
        <tr>
    """
    print(rows)
    for row in rows:
            page += "<td>" + str(row[0]) + "</td>"
            page += "<td>" + str(row[1]) + "</td>"
            page += "<td>" + str(datetime.fromtimestamp(int(row[2]))) + "</td>"
            page += "<td>" + str(datetime.fromtimestamp(int(row[3]))) + "</td>"
            page += "</tr>"

    page += "</table>"

    cur.close()
    conn.close()

    return page