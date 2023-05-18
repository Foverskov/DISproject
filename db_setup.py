import psycopg2
import csv
import os

members_csv = os.join("data", "members.csv")
employees_csv = os.join("data", "employees.csv")

# Connect to the database
conn = psycopg2.connect(database="flask_db", user="postgres",
                        password="root", host="localhost", port="5432")
# create a cursor
cur = conn.cursor()

# Reset and create tables
cur.execute(
    '''
    DROP TABLE IF EXISTS Members;
    DROP TABLE IF EXISTS Employees;
    DROP TABLE IF EXISTS Facilities;
    DROP TABLE IF EXISTS Teams;
    DROP TABLE IF EXISTS Memberships;
    DROP TABLE IF EXISTS Bookings;
    DROP TABLE IF EXISTS Calendar;
    DROP TABLE IF EXISTS Manage;
    DROP TABLE IF EXISTS HourlyEmployees;
    DROP TABLE IF EXISTS SalariedEmployees;

    CREATE TABLE Members
    (mid INT PRIMARY KEY,
    ssn INT,
    name TEXT,
    age INT,
    address TEXT,
    telephone TEXT,
    email TEXT,
    );
    CREATE TABLE Employees
    (eid INT PRIMARY KEY,
    ssn INT,
    name TEXT,
    age INT,
    address TEXT,
    telephone TEXT,
    email TEXT,
    );
    CREATE TABLE Facilities
    (address TEXT PRIMARY KEY,
    name TEXT,
    description TEXT,
    );
    CREATE TABLE Teams
    (tid INT PRIMARY KEY,
    name TEXT,
    time TEXT,
    price INT,
    );
    CREATE TABLE Memberships
    (mid INT,
    tid INT,
    from_date DATE,
    to_date DATE,
    PRIMARY KEY (mid, tid),
    FOREIGN KEY (mid) REFERENCES Members(mid),
    FOREIGN KEY (tid) REFERENCES Teams(tid),
    );
    CREATE TABLE Bookings
    (bid INT,
    tid INT,
    address TEXT,
    PRIMARY KEY (bid, tid, address),
    FOREIGN KEY (tid) REFERENCES Teams(tid),
    FOREIGN KEY (address) REFERENCES Facilities(address)
    );
    CREATE TABLE Calendar
    (bid INT PRIMARY KEY,
    from_datetime DATETIME,
    to_datetime DATETIME,
    FOREIGN KEY (bid) REFERENCES Bookings(bid)
    );
    CREATE TABLE Manage
    (tid INT,
    eid INT,
    PRIMARY KEY (tid, eid),
    FOREIGN KEY (tid) REFERENCES Teams(tid),
    FOREIGN KEY (eid) REFERENCES Employees(eid)
    );
    CREATE TABLE HourlyEmployees
    (eid INT PRIMARY KEY,
    hourly_rate INT,
    hours_worked INT,
    FOREIGN KEY (eid) REFERENCES Employees(eid)
    );
    CREATE TABLE SalariedEmployees
    (eid INT PRIMARY KEY,
    salary INT,
    FOREIGN KEY (eid) REFERENCES Employees(eid)
    );
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
    INSERT INTO Facilities VALUES ('Hovedvejen 1', 'Fitness', 'Fitness center');
    INSERT INTO Facilities VALUES ('Hovedvejen 2', 'Tennis', 'Tennis court');
    INSERT INTO Facilities VALUES ('Hovedvejen 3', 'Badminton', 'Badminton court');
    INSERT INTO Facilities VALUES ('Hovedvejen 4', 'Squash', 'Squash court');
    '''
)

# commit the changes
conn.commit()
  
# close the cursor and connection
cur.close()
conn.close()