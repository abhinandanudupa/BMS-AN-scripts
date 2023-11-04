#!/usr/bin/env python3

from csv import reader, DictReader, DictWriter
from datetime import datetime
from pprint import pprint


DPT_MPPNG = {
        "Artificial Intelligence & Machine Learning":	"CS",
        "Civil Engineering":	"CE",
        "Biotechnology":	"BT",
        "Electrical & Electronics Engineering":	"ECE",
        "Information Science & Engineering":	"CS",
        "Electronics & Communication Engineering":	"ECE",
        "Computer Science & Engineering":	"CS",
        "Industrial Engineering & Management":	"ME",
        "Computer Science & Data Science": "CS",
        "Chemical Engineering":	"CH",
        "Electronics & Telecommunication Engineering":	"ECE",
        "Mechanical Engineering":	"ME",
        "Artificial Intelligence & Data Science":	"CS",
        "Aerospace Engineering":	"AE",
        "Computer Science & Business Systems":	"CS",
        "Electrical & Electronics Engineering": "ECE",
        "Electronics & Instrumentation Engineering": "ECE",
        "Aerospace Engineering": "AE",
        "Medical Electronics": "ML",
        }


class Mentee:
    def __init__(self, name, email, year, country, reg_time, ctype, department, prefs):
        self.year = year
        self.reg_time = reg_time
        self.ctype = ctype
        self.name = name
        self.country = country
        self.email = email
        self.department = department
        self.prefs = prefs

    def check_preference(self, mentor):
        return mentor.name in self.prefs

    def get_preference_rank(self, mentor):
        try:
            idx = self.prefs.index(mentor.name)
            return idx
        except:
            return float("inf")

    def __lt__(self, other):
        if self.year < other.year:
            return True
        if self.reg_time < other.reg_time:
            return True
        return False

    def __eq__(self, other):
        return self.year == other.year and self.reg_time == other.reg_time

    def __str__(self):
        return (
f"""{self.name}
{self.email}
{self.department}
{self.ctype}
{self.reg_time}
{self.year}
{self.country}
{self.prefs}""")


class Mentor:
    def __init__(self, name, email, country, ctype, year, department, capacity=1):
        self.capacity = capacity
        self.country = country
        self.allocated = []
        self.name = name
        self.email = email
        self.department = department
        self.ctype = ctype

    def fill_capacity(self, mentee):
        if self.capacity <= 0:
            raise Exception("Mentor capacity is full!")
        if not self.check_match(mentee):
            return Exception("Mentor and Mentee don't match!")

        self.capacity -= 1
        self.allocated.append(mentee)

    def check_match(self, mentee):
        return self.country == mentee.country and self.department == mentee.department

    def has_capacity(self):
        return self.capacity > 0

    def __str__(self):
        return (
f"""{self.name}
{self.email}
{self.ctype}
{self.capacity}
{self.country}
{self.allocated}""")


def allocate_mentors(mentee_list, mentor_list):
    allocations = []
    for mentee in mentee_list:
        best_mentor = (None, float("inf"))
        for mentor in mentor_list:
            if mentee.check_preference(mentor) and mentor.has_capacity():
                rank = mentee.get_preference_rank(mentor)
                if rank < best_mentor[1]:
                    best_mentor = (mentor, rank)

            elif mentor.check_match(mentee) and mentor.has_capacity():
                rank = mentee.get_preference_rank(mentor)
                if rank < best_mentor[1]:
                    best_mentor = (mentor, rank)

        bm, br = best_mentor
        if bm is not None:
            allocations.append((mentee, bm, br))
            bm.capacity -= 1
            # print(bm)

    for mentee, mentor, rank in allocations:
        item = {
                "mentor_name": mentor.name,
                "mentor_email": mentor.email,
                "mentee_name": mentee.name,
                "mentee_email": mentee.email,
                }
        # pprint(item)

    return allocations


def parse_year(year_str):
    try:
        return int(year_str)
    except:
        return 2026


def parse_country(c):
    if c == "United States of America (USA)":
        return "USA"
    if c == "The Netherlands":
        return "Netherlands"
    return c


def parse_mentees(csv_file):
    mentees = []
    with open(csv_file, "r") as file:
        csv_itr = DictReader(file)
        for row in csv_itr:
            # pprint(row)
            name = row["Full Name"]
            email = row["Email Address"]
            ctype = "t" if row["Type of course"] == "Technical - MS, PhD etc" else "m"
            prefs = []
            prefs.append(row["Mentor 1"].split(" - ")[1])
            prefs.append(row["Mentor 2"].split(" - ")[1])
            prefs.append(row["Mentor 3"].split(" - ")[1])
            year = parse_year(row["Year of Graduation from BMSCE"])
            department = DPT_MPPNG[row["Department"]]
            reg_time = row["Timestamp"]
            reg_time = datetime.strptime(reg_time, '%m/%d/%Y %H:%M:%S')
            reg_time = reg_time.day * 3600 * 24 + reg_time.hour * 3600 + reg_time.minute * 60 + reg_time.second
            country = parse_country(row["One country you are interested in for higher education"])
            mentee = Mentee(name, email, year, country, reg_time, ctype, department, prefs)
            mentees.append(mentee)

        return mentees


def parse_mentors(csv_file):
    mentors = []
    with open(csv_file, "r") as file:
        csv_itr = DictReader(file)
        for row in csv_itr:
            # pprint(row)
            name = row["Full Name"]
            email = row["Email Address"]
            year = int(row["Year of Passout (YYYY)"])
            country = parse_country(row["Country in which University is located"])
            ctype = row["ctype"]
            department = DPT_MPPNG[row["Department in BMSCE"]]
            capacity = int(row["No of Mentee"])
            mentor = Mentor(name, email, country, ctype, year, department, capacity)
            mentors.append(mentor)

        return mentors


mentors = parse_mentors("./mentors.csv")
mr_l = len(mentors)

# for m in mentors:
#     print(m)


mentees = sorted(parse_mentees("./mentees.csv"))
me_l = len(mentees)

# for m in mentees:
#     print(m.year)

allocations = allocate_mentors(mentees, mentors)
a_l = len(allocations)

print(f"Mentors: {mr_l}\nMentees: {me_l}\nAllocated: {a_l}")

save_file = "allocations.csv"
with open(save_file, "w") as f:
    f_ns = ["mentee_name", "mentee_email", "mentor_name", "mentor_email", "country", "mentee_year", "department", "mentor_capacity_left",]
    dw = DictWriter(f, fieldnames=f_ns)

    dw.writeheader()
    for me, mr, r in allocations:
        item = {
                "mentee_name": me.name,
                "mentee_email": me.email,
                "mentor_name": mr.name,
                "mentor_email": mr.email,
                "country": me.country,
                "mentee_year": me.year,
                "department": me.department,
                "mentor_capacity_left": mr.capacity,
                }
        dw.writerow(item)
    print(f"Saved the allocations in {save_file}.")

not_allocated = []
me_allocated_ns = [m.name for (m, _, _) in allocations]
not_allocated = [m for m in mentees if m.name not in me_allocated_ns]

if len(not_allocated) > 0:
    for m in not_allocated:
        print(m)

