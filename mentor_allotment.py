#!/usr/bin/env python3
"""A simple script to allocate mentees mentors based on their preferences."""

from csv import DictReader, DictWriter
from datetime import datetime
# from pprint import pprint


DPT_MPPNG = {
    "Artificial Intelligence & Machine Learning": "CS",
    "Civil Engineering": "CE",
    "Biotechnology": "BT",
    "Electrical & Electronics Engineering": "ECE",
    "Information Science & Engineering": "CS",
    "Electronics & Communication Engineering": "ECE",
    "Computer Science & Engineering": "CS",
    "Industrial Engineering & Management": "ME",
    "Computer Science & Data Science": "CS",
    "Chemical Engineering": "CH",
    "Electronics & Telecommunication Engineering": "ECE",
    "Mechanical Engineering": "ME",
    "Artificial Intelligence & Data Science": "CS",
    "Aerospace Engineering": "AE",
    "Computer Science & Business Systems": "CS",
    "Electronics & Instrumentation Engineering": "ECE",
    "Medical Electronics": "ML",
}
SAVE_FILE = "allocations.csv"


class Mentee:
    """A class representing a mentee and with methods to check prefference and rank mentors"""
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
        """Returns True is mentor is preferred by the mentee"""
        return mentor.name in self.prefs

    def get_preference_rank(self, mentor):
        """Returns a rank of a mentor based on mentee's preferrences"""
        try:
            idx = self.prefs.index(mentor.name)
            return idx + 1
        except ValueError:
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
        return f"""{self.name}
{self.email}
{self.department}
{self.ctype}
{self.reg_time}
{self.year}
{self.country}
{self.prefs}"""


class Mentor:
    """A class to represent a mentor with methods to macth with a mentee."""
    def __init__(self, name, email, country, ctype, year, department, capacity):
        self.capacity = capacity
        self.country = country
        self.allocated = []
        self.name = name
        self.email = email
        self.year = year
        self.department = department
        self.ctype = ctype

    def check_match(self, mentee):
        """Returns True if mentee and mentor are compatible"""
        return self.country == mentee.country and self.department == mentee.department

    def has_capacity(self):
        """Returns True if menotr can handle more students"""
        return self.capacity > 0

    def __str__(self):
        return f"""{self.name}
{self.email}
{self.ctype}
{self.capacity}
{self.country}
{self.allocated}"""


def allocate_mentors(mentee_list, mentor_list):
    """Allocates mentors to mentees on the basis of their preference and need"""
    allocated = []
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
            allocated.append((mentee, bm, br))
            bm.capacity -= 1
            # print(bm)

    return allocated


def parse_year(year_str):
    """Parses and converts year passed as string integer based on need"""
    try:
        return int(year_str)
    except ValueError:
        return 2026


def parse_country(c):
    """Parses the country passed as a string to a common acceptable"""
    if c == "United States of America (USA)":
        return "USA"
    if c == "The Netherlands":
        return "Netherlands"
    return c


def parse_mentees(csv_file):
    """Parses the mentee details from a CSV file and returns a list of Mentee objects"""
    mentee_list = []
    with open(csv_file, "r", encoding="utf8") as file:
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
            reg_time = datetime.strptime(reg_time, "%m/%d/%Y %H:%M:%S")
            reg_time = (
                reg_time.day * 3600 * 24
                + reg_time.hour * 3600
                + reg_time.minute * 60
                + reg_time.second
            )
            country = parse_country(
                row["One country you are interested in for higher education"]
            )
            mentee = Mentee(
                name, email, year, country, reg_time, ctype, department, prefs
            )
            mentee_list.append(mentee)

        return mentee_list


def parse_mentors(csv_file):
    """Parses the mentor details from a CSV file and returns a list of Mentor objects"""
    mentor_list = []
    with open(csv_file, "r", encoding="utf8") as file:
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
            mentor_list.append(mentor)

        return mentor_list


mentors = parse_mentors("./mentors.csv")
N_MENTORS = len(mentors)

# for m in mentors:
#     print(m)


mentees = sorted(parse_mentees("./mentees.csv"))
N_MENTEES = len(mentees)

# for m in mentees:
#     print(m.year)

allocations = allocate_mentors(mentees, mentors)
N_ALLOCATED = len(allocations)

print(f"Mentors: {N_MENTORS}\nMentees: {N_MENTEES}\nAllocated: {N_ALLOCATED}")

with open(SAVE_FILE, "w", encoding="utf8") as f:
    f_ns = [
        "mentee_name",
        "mentee_email",
        "mentor_name",
        "mentor_email",
        "country",
        "mentee_year",
        "department",
        "mentor_capacity_left",
        "rank",
    ]
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
            "rank": r,
        }
        dw.writerow(item)
    print(f"Saved the allocations in {SAVE_FILE}.")

me_allocated_ns = [m.name for (m, _, _) in allocations]
not_allocated = [m for m in mentees if m.name not in me_allocated_ns]

if len(not_allocated) > 0:
    for m in not_allocated:
        print(m)
