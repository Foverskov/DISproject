import csv
import random

navne_csv = "navne.csv"
efternavne_csv = "efternavne.csv"
vejnavne_csv = "vejnavne.csv"

def get_csv_data(filename):
    data_file = open(filename, "r")
    reader = csv.reader(data_file)
    rows = []
    for row in reader:
        rows.extend(row)
    return rows

def generate_address(road_names):
    address = ""
    address += road_names[random.randint(0, len(road_names) - 1)]
    address += " " + str(random.randint(1, 100))
    address += " " + str(random.randint(1000, 9999))
    return address

def generate_phone_number():
    phone_number = ""
    for i in range(8):
        phone_number += str(random.randint(0, 9))
    return phone_number

def generate_email(first_name):
    email = ""
    email += first_name.lower() + str(random.randint(0,100)) + "@kumail.dk"
    return email

def generate_name(first_names, last_names):
    name = ""
    name += first_names[random.randint(0, len(first_names) - 1)]
    name += " " + last_names[random.randint(0, len(last_names) - 1)]
    return name

def generate_cpr():
    social_security_number = ""
    for i in range(6):
        social_security_number += str(random.randint(0, 9))
    social_security_number += "-"
    for i in range(4):
        social_security_number += str(random.randint(0, 9))
    return social_security_number

def generate_member():
    data = []
    data.append(generate_cpr())
    data.append(generate_name(get_csv_data(navne_csv), get_csv_data(efternavne_csv)))
    data.append(random.randint(8, 99))
    data.append(generate_address(get_csv_data(vejnavne_csv)))
    data.append(generate_phone_number())
    data.append(generate_email(data[1].split(" ")[0]))
    return data

def generate_members(amount, of):
    with open(of, "w") as file:
        writer = csv.writer(file)
        writer.writerow(["mid","cpr", "name", "age", "address", "phone_number", "email"])
        for i in range(amount):
            writer.writerow([i] + generate_member())

generate_members(100, "members.csv")