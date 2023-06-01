from flask import Flask, render_template, request, redirect, url_for, flash
import psycopg2
import configparser
import os

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
    page = """
    <h1>Velkommen til vores side</h1>
    <p>Her kan du se vores medlemmer, ansatte, faciliteter, hold, medlemskaber og bookinger</p>
    <a href="/medlemmer">Medlemmer</a>
    <a href="/hold">Holdstruktur</a>
    <a href="/faciliteter">Faciliteter</a>
    <a href="/mail">Beskeder</a>
    """
    return page


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
    - Hold: tid, name
    - members: mid(count)
    - Employee: name

Detalje underside.
Data:
    - Members: mid, name
    - In: from, to
"""


"""
Faciliteter
Data:
    - Faciliteter: name, addr
    - Rent: booking, addr, from, to, tid

Features:
    - Filtrering på dato, addresse, availablity
"""