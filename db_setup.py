import psycopg2
import csv
import os
import configparser

members_csv = os.path.join("data", "members.csv")
employees_csv = os.path.join("data", "employees.csv")

# Connect to the database
# check if config file exists
if not os.path.isfile('config.ini'):
    raise Exception('config.ini not found. Please create it from config.ini.example')
config = configparser.ConfigParser()
config.read('config.ini')
db = config['DB_LOGIN']
conn = psycopg2.connect(database=db['database'], user=db['user'],
                        password=db['password'], host=db['host'], port=db['port'])

# create a cursor
cur = conn.cursor()

# Reset and create tables
cur.execute(
    '''
    DROP TABLE IF EXISTS Members CASCADE; \
    DROP TABLE IF EXISTS Employees CASCADE; \
    DROP TABLE IF EXISTS Facilities CASCADE; \
    DROP TABLE IF EXISTS Teams CASCADE; \
    DROP TABLE IF EXISTS Memberships; \
    DROP TABLE IF EXISTS Bookings CASCADE; \
    DROP TABLE IF EXISTS Calendar; \
    DROP TABLE IF EXISTS Manage; \
    DROP TABLE IF EXISTS HourlyEmployees; \
    DROP TABLE IF EXISTS SalariedEmployees; \
    CREATE TABLE Members \
    (mid INT PRIMARY KEY, \
    ssn TEXT, \
    name TEXT, \
    age INT, \
    address TEXT, \
    telephone TEXT, \
    email TEXT \
    ); \
    CREATE TABLE Employees \
    (eid INT PRIMARY KEY, \
    ssn TEXT, \
    name TEXT, \
    age INT, \
    address TEXT, \
    telephone TEXT, \
    email TEXT \
    ); \
    CREATE TABLE Facilities \
    (address TEXT PRIMARY KEY, \
    name TEXT, \
    description TEXT \
    ); \
    CREATE TABLE Teams \
    (tid INT PRIMARY KEY, \
    name TEXT, \
    time TEXT, \
    price INT \
    ); \
    CREATE TABLE Memberships \
    (mid INT, \
    tid INT, \
    from_date DATE, \
    to_date DATE, \
    PRIMARY KEY (mid, tid), \
    FOREIGN KEY (mid) REFERENCES Members(mid), \
    FOREIGN KEY (tid) REFERENCES Teams(tid) \
    ); \
    CREATE TABLE Bookings \
    (bid INT, \
    tid INT, \
    address TEXT, \
    PRIMARY KEY (bid, tid, address), \
    FOREIGN KEY (tid) REFERENCES Teams(tid), \
    FOREIGN KEY (address) REFERENCES Facilities(address) \
    ); \
    CREATE TABLE Calendar \
    (bid INT, \
    tid INT, \
    address TEXT, \
    PRIMARY KEY (bid, tid, address), \
    from_datetime TIMESTAMP, \
    to_datetime TIMESTAMP, \
    FOREIGN KEY (bid,tid,address) REFERENCES Bookings(bid,tid,address) \
    ); \
    CREATE TABLE Manage \
    (tid INT, \
    eid INT, \
    PRIMARY KEY (tid, eid), \
    FOREIGN KEY (tid) REFERENCES Teams(tid), \
    FOREIGN KEY (eid) REFERENCES Employees(eid) \
    ); \
    CREATE TABLE HourlyEmployees \
    (eid INT PRIMARY KEY, \
    hourly_rate INT, \
    hours_worked INT, \
    FOREIGN KEY (eid) REFERENCES Employees(eid) \
    ); \
    CREATE TABLE SalariedEmployees \
    (eid INT PRIMARY KEY, \
    salary INT, \
    FOREIGN KEY (eid) REFERENCES Employees(eid) \
    );\
    ''')

def import_members():
    with open(members_csv, 'r') as f:
        reader = csv.reader(f)
        next(reader) # Skip the header row.
        for row in reader:
            cur.execute("INSERT INTO Members VALUES (%s, %s, %s, %s, %s, %s, %s)",row)

def import_employees():
    with open(employees_csv, 'r') as f:
        reader = csv.reader(f)
        next(reader) # Skip the header row.
        for row in reader:
            cur.execute("INSERT INTO Employees VALUES (%s, %s, %s, %s, %s, %s, %s)",row)

cur.execute(
    '''
    INSERT INTO Facilities VALUES ('Hovedvejen 1', 'Fitness', 'Fitness center'); \
    INSERT INTO Facilities VALUES ('Hovedvejen 2', 'Tennis', 'Tennis court'); \
    INSERT INTO Facilities VALUES ('Hovedvejen 3', 'Badminton', 'Badminton court'); \
    INSERT INTO Facilities VALUES ('Hovedvejen 4', 'Squash', 'Squash court');
    '''
)
import_members()
import_employees()

# commit the changes
conn.commit()
  
# close the cursor and connection
cur.close()
conn.close()