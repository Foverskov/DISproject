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
# Note: Time and dates are in unix time
cur.execute(
    '''
    DROP TABLE IF EXISTS Members CASCADE; \
    DROP TABLE IF EXISTS Employees CASCADE; \
    DROP TABLE IF EXISTS Facilities CASCADE; \
    DROP TABLE IF EXISTS Teams CASCADE; \
    DROP TABLE IF EXISTS Bookings CASCADE; \
    DROP TABLE IF EXISTS Memberships; \
    DROP TABLE IF EXISTS Manage; \
    DROP TABLE IF EXISTS HourlyEmployees; \
    DROP TABLE IF EXISTS SalariedEmployees; \
    CREATE TABLE Members \
    (mid SERIAL PRIMARY KEY, \
    ssn TEXT, \
    name TEXT, \
    age INT, \
    address TEXT, \
    telephone TEXT, \
    email TEXT \
    ); \
    CREATE TABLE Employees \
    (eid SERIAL PRIMARY KEY, \
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
    (tid SERIAL PRIMARY KEY, \
    name TEXT, \
    time TEXT, \
    price INT \
    ); \
    CREATE TABLE Memberships \
    (mid INT, \
    tid INT, \
    from_date BIGINT, \
    to_date BIGINT, \
    PRIMARY KEY (mid, tid), \
    FOREIGN KEY (mid) REFERENCES Members(mid) ON DELETE CASCADE, \
    FOREIGN KEY (tid) REFERENCES Teams(tid) ON DELETE CASCADE \
    ); \
    CREATE TABLE Bookings \
    (tid SERIAL, \
    address TEXT, \
    from_date BIGINT, \
    to_date BIGINT, \
    PRIMARY KEY (tid, address, from_date, to_date), \
    FOREIGN KEY (tid) REFERENCES Teams(tid) ON DELETE CASCADE, \
    FOREIGN KEY (address) REFERENCES Facilities(address) ON DELETE CASCADE \
    ); \
    CREATE TABLE Manage \
    (tid INT, \
    eid INT, \
    PRIMARY KEY (tid, eid), \
    FOREIGN KEY (tid) REFERENCES Teams(tid) ON DELETE CASCADE, \
    FOREIGN KEY (eid) REFERENCES Employees(eid) ON DELETE CASCADE \
    ); \
    CREATE TABLE HourlyEmployees \
    (eid SERIAL PRIMARY KEY, \
    hourly_rate INT, \
    hours_worked INT, \
    FOREIGN KEY (eid) REFERENCES Employees(eid) ON DELETE CASCADE \
    ); \
    CREATE TABLE SalariedEmployees \
    (eid SERIAL PRIMARY KEY, \
    salary INT, \
    FOREIGN KEY (eid) REFERENCES Employees(eid) ON DELETE CASCADE \
    );\
    ''')

def import_members():
    with open(members_csv, 'r') as f:
        reader = csv.reader(f)
        next(reader) # Skip the header row.
        for row in reader:
            cur.execute("INSERT INTO Members VALUES (DEFAULT, %s, %s, %s, %s, %s, %s)",row[1:])

def import_employees():
    with open(employees_csv, 'r') as f:
        reader = csv.reader(f)
        next(reader) # Skip the header row.
        for row in reader:
            cur.execute("INSERT INTO Employees VALUES (DEFAULT, %s, %s, %s, %s, %s, %s)",row[1:])

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

# Create a trigger, which ensures, that all expired memberships will be removed
cur.execute(
    '''
    CREATE OR REPLACE FUNCTION remove_expired_members()
        RETURNS TRIGGER AS $$
    BEGIN
        DELETE FROM Memberships
        WHERE tid = NEW.tid
            AND mid IN (
            SELECT mid
            FROM Memberships
            WHERE tid = NEW.tid
                AND to_date < EXTRACT(EPOCH FROM CURRENT_TIMESTAMP)::bigint
            );

        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    CREATE TRIGGER remove_expired_manage_trigger
    BEFORE INSERT OR UPDATE ON Memberships
    FOR EACH ROW
    EXECUTE FUNCTION remove_expired_members();
    '''
)

# commit the changes
conn.commit()
  
# close the cursor and connection
cur.close()
conn.close()