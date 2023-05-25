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

@app.route('/medlemmer')
def medlemmer():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM members")
    rows = cur.fetchall()

    page = "<table><tr><th>Medlems ID</th><th>CPR</th><th>Navn</th><th>Alder</th><th>Adresse</th><th>Telefon</th><th>Email</th></tr>"

    for row in rows:
        page += "<tr>"
        for col in row:
            page += "<td>" + str(col) + "</td>"
        page += "</tr>"
    page += "</table>"

    cur.close()
    conn.close()

    return page
