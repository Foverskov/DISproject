from flask import Flask, render_template, request, redirect, url_for, flash
import psycopg2


app = Flask(__name__)

# Connect to the database
conn = psycopg2.connect(
    host="localhost", port="5433",
    database="foverskov",
    user="postgres",
    password="postgres"
)

@app.route('/create', methods=['GET', 'POST'])
def index():
    # Connect to the database
    conn = psycopg2.connect(
        host="localhost", port="5433",
        database="foverskov",
        user="postgres",
        password="postgres"
)
  
    # create a cursor
    cur = conn.cursor()
  
    # Select all products from the table
    cur.execute('''SELECT * FROM teaches''')
  
    # Fetch the data
    data = cur.fetchall()
  
    # close the cursor and connection
    cur.close()
    conn.close()
  
    return render_template('index.html', data=data)
