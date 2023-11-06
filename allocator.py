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
SAVE_NOT_MENTEE = "not_allocated_mentees.csv"
SAVE_NOT_MENTOR = "not_allocated_mentors.csv"


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
        return (self.year, self.reg_time, self.name) < (
            other.year,
            other.reg_time,
            self.name,
        )

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
        self.capacity = 2  # capacity
        self.total_capacity = 2  # capacity
        self.country = country
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
{self.country}"""


def allocate_mentors(mentee_list, mentor_list):
    """Allocates mentors to mentees on the basis of their preference and need"""
    allocated = []
    for mentee in mentee_list:
        print("Mentee", mentee.name)
        best_mentor = (None, float("inf"))
        for mentor in mentor_list:
            rank = mentee.get_preference_rank(mentor)
            if mentee.check_preference(mentor) and mentor.has_capacity():
                if rank < best_mentor[1]:
                    best_mentor = (mentor, rank)

        bm, br = best_mentor
        print("Mentor", bm)
        if not bm is None:
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
            ctype = "t"  # "t" if row["Type of course"] == "Technical - MS, PhD etc" else "m"
            prefs = []
            prefs.append(row["Mentor 1"].split(" - ")[1])
            prefs.append(row["Mentor 2"].split(" - ")[1])
            prefs.append(row["Mentor 3"].split(" - ")[1])
            year = parse_year(row["Year of Graduation from BMSCE"])
            department = DPT_MPPNG[row["Department"]]
            reg_time = row["Timestamp"]
            reg_time = datetime.strptime(reg_time, "%m/%d/%Y %H:%M:%S")
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
            ctype = "t"  # row["ctype"]
            department = DPT_MPPNG[row["Department in BMSCE"]]
            capacity = int(row["No of Mentee"])
            mentor = Mentor(name, email, country, ctype, year, department, capacity)
            mentor_list.append(mentor)

        return mentor_list


mentors = parse_mentors("./mentors.csv")
N_MENTORS = len(mentors)

# print("------------------------------------------------------")
# for m in mentors:
#     print(m)
# print("------------------------------------------------------")

mentees = sorted(parse_mentees("./mentees.csv"))
N_MENTEES = len(mentees)

# print("------------------------------------------------------")
# for m in mentees:
#     print(m.name)
# print("------------------------------------------------------")

allocations = allocate_mentors(mentees, mentors)
N_ALLOCATED = len(allocations)

print("------------------------------------------------------")
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
        "mentor_total_capacity",
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
            "mentor_total_capacity": mr.total_capacity,
            "rank": r,
        }
        dw.writerow(item)
    print(f"Saved the allocations in {SAVE_FILE}.")

me_allocated_ns = [m.name for (m, _, _) in allocations]
me_not_allocated = [m for m in mentees if m.name not in me_allocated_ns]

with open(SAVE_NOT_MENTEE, "w") as f:
    field_names = [
        "mentee_name",
        "mentee_email",
        "year",
    ]
    dw = DictWriter(f, fieldnames=field_names)
    dw.writeheader()
    for m in me_not_allocated:
        dw.writerow({"mentee_name": m.name, "mentee_email": m.email, "year": m.year})

    print(
        f"Saved the details of mentees who were not allocated any mentors in {SAVE_NOT_MENTEE}"
    )

mr_allocated_ns = [m.name for (_, m, _) in allocations]
mr_not_allocated = [m for m in mentors if m.name not in mr_allocated_ns]

with open(SAVE_NOT_MENTOR, "w") as f:
    field_names = [
        "mentor_name",
        "mentor_email",
    ]
    dw = DictWriter(f, fieldnames=field_names)
    dw.writeheader()
    for m in mr_not_allocated:
        dw.writerow(
            {
                "mentor_name": m.name,
                "mentor_email": m.email,
            }
        )

    print(
        f"Saved the details of mentees who were not allocated any mentors in {SAVE_NOT_MENTOR}"
    )

# if len(not_allocated) > 0:
#     print("------------------------------------------------------")
#     print("Here are the people who are not allocated any mentors:")
#     for m in not_allocated:
#         print(m)
#         print("------------------------------------------------------")
