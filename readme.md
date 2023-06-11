# Database setup

```config.ini.example``` must be filled out with database credentials, and be renamed to ```config.ini```.

For example in file ```config.ini```:

```
[DB_LOGIN]
database = postgres
user = postgres
password = postgres
host = localhost
port = 5432
```

Then to set up the database, run ```python db_setup.py```.

This will delete the following tables:
* Members
* Employees
* Facilities
* Teams
* Bookings
* Memberships
* Manage
* HourlyEmployees
* SalariedEmployees

and replace it with our data.

# Website

To start the site, run ```python -m flask --app app.py run``` and open the prompted link.
