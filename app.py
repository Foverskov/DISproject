from flask import Flask, render_template, request, redirect, url_for, flash
import psycopg2


app = Flask(__name__)

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
    conn = psycopg2.connect(
        host="localhost", port="5433",
        database="postgres",
        user="postgres",
        password="postgres"
    )
    cur = conn.cursor()
    cur.execute("SELECT * FROM members")
    rows = cur.fetchall()

    page = "<table><tr><th>Medlems ID</th><th>Navn</th><th>Alder</th><th>Adresse</th><th>Telefon</th><th>Email</th></tr>"

    for row in rows:
        page += "<tr>"
        for col in row:
            page += "<td>" + str(col) + "</td>"
        page += "</tr>"
    page += "</table>"

    cur.close()
    conn.close()

    return page
