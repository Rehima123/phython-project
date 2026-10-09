from datetime import date
from tabulate import tabulate
import os
import json
try:
    import pyttsx3
    engine = pyttsx3.init()
except ImportError:
    engine = None

STUDENTS_FILE = "students.json"
ATTENDANCE_FILE = "attendance.json"
COURSES_FILE = "courses.json"

USERS = {
    "admin":   {"username": "Admin",   "password": "admin123", "role": "admin"},
    "huzeifa": {"username": "huzeifa", "password": "123",      "role": "teacher", "name": "huzeifa"},
    "seid":    {"username": "seid",    "password": "123",      "role": "teacher", "name": "seid"},
    "faruk":   {"username": "faruk",   "password": "f123",     "role": "teacher", "name": "faruk"}
}

# ---------------- HELPERS ----------------
def load_json(file):
    if os.path.exists(file):
        with open(file, "r") as f:
            return json.load(f)
    return {}

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)

def calculate_percentage(records):
    total = len(records)
    if total == 0:
        return 0
    present = sum(1 for r in records if r.get("status") in ("P", "L", "PR"))
    return round((present / total) * 100, 2)

def get_teacher_courses(courses, teacher_name):
    return {cid: d for cid, d in courses.items() if d.get("teacher", "").lower() == teacher_name.lower()}

def attendance_percent(stats):
    attended = stats["present"] + stats["late"] + stats["permission"]
    return round((attended / stats["total"] * 100), 2) if stats["total"] > 0 else 0

def build_course_stats(records):
    stats = {}
    for r in records:
        cid = r.get("course_id", "N/A")
        if cid not in stats:
            stats[cid] = {"total": 0, "present": 0, "late": 0, "absent": 0, "permission": 0}
        stats[cid]["total"] += 1
        status = r.get("status", "")
        if status == "P":    stats[cid]["present"] += 1
        elif status == "L":  stats[cid]["late"] += 1
        elif status == "A":  stats[cid]["absent"] += 1
        elif status == "PR": stats[cid]["permission"] += 1
    return stats

def select_course(courses, teacher_name=None, allow_all=False):
    if teacher_name:
        tc = get_teacher_courses(courses, teacher_name)
        if not tc:
            print("⚠️ You are not assigned to any courses")
            return False
        print(f"\n📚 Your Courses ({teacher_name}):")
        print(tabulate([[cid, d["name"]] for cid, d in tc.items()],
                       ["Course ID", "Course Name"], tablefmt="fancy_grid"))
        cid = input("\nEnter Course ID: ").strip()
        if cid not in tc:
            print("❌ Invalid course ID or not assigned to you")
            return False
        return cid
    else:
        if courses:
            print("\n📚 Available Courses:")
            view_courses(courses)
        prompt = "\nEnter Course ID (or press Enter for all): " if allow_all else "\nEnter Course ID: "
        cid = input(prompt).strip()
        if cid and cid not in courses:
            print("❌ Invalid course ID")
            return False
        return cid if cid else None

# ---------------- LOGIN ----------------
def login():
    print("\n🎓 Attendance System Login")
    print("1 ➡️ Admin")
    print("2 ➡️ Teacher")
    choice = input("Enter your choice (1/2): ")

    if choice == "1":
        username = input("Username: ")
        password = input("Password: ")
        if username == USERS["admin"]["username"] and password == USERS["admin"]["password"]:
            print("✅ Login successful! Role: ADMIN")
            if engine:
                engine.say("Thank you, successfully logged in as admin")
                engine.runAndWait()
            return ("admin", None)
        print("❌ Invalid username or password")
        return None

    elif choice == "2":
        username = input("Username: ")
        password = input("Password: ")
        for user_data in USERS.values():
            if user_data["role"] == "teacher" and username == user_data["username"] and password == user_data["password"]:
                teacher_name = user_data.get("name", username)
                print(f"✅ Login successful! Role: Instructor")
                if engine:
                    engine.say(f"Thank you, successfully logged in as {teacher_name}")
                    engine.runAndWait()
                return ("teacher", teacher_name)
        print("❌ Invalid username or password")
        return None

    print("❌ Invalid choice")
    return None

# ---------------- STUDENT MANAGEMENT ----------------
def add_student(students):
    sid = input("Student ID: ")
    if sid in students:
        print("⚠️ Student already exists")
        return
    students[sid] = {
        "fname":      input("First Name: "),
        "lname":      input("Last Name: "),
        "age":        input("Age: "),
        "department": input("Department: "),
        "year":       input("Year: "),
        "section":    input("Section: "),
        "contact":    input("Contact: ")
    }
    save_json(STUDENTS_FILE, students)
    print("✅ Student added successfully")

def view_students(students):
    if not students:
        print("⚠️ No students available")
        return
    table = [[sid, d["fname"], d["lname"], d["age"], d["department"], d["year"], d["section"], d["contact"]]
             for sid, d in students.items()]
    print(tabulate(table, ["ID","Fname","Lname","Age","Dept","Year","Section","Contact"], tablefmt="fancy_grid"))

def delete_student(students, attendance):
    print("\n🗑️ Delete Student")
    print("1 ➡️ Delete by ID")
    print("2 ➡️ Delete by Name")
    choice = input("Choose option (1/2): ").strip()
    sid_to_delete = None

    if choice == "1":
        sid = input("Enter student ID: ").strip()
        if sid not in students:
            print("❌ Student not found")
            return
        sid_to_delete = sid
    elif choice == "2":
        name = input("Enter student name (first or last): ").lower().strip()
        matches = [(sid, d) for sid, d in students.items()
                   if name in d["fname"].lower() or name in d["lname"].lower()]
        if not matches:
            print("❌ Student not found")
            return
        elif len(matches) == 1:
            print(f"Found: {matches[0][1]['fname']} {matches[0][1]['lname']} (ID: {matches[0][0]})")
            sid_to_delete = matches[0][0]
        else:
            print("\n📋 Multiple students found:")
            print(tabulate([[s, d["fname"], d["lname"], d["department"]] for s, d in matches],
                           ["ID","Fname","Lname","Department"], tablefmt="fancy_grid"))
            sid = input("\nEnter the ID of the student to delete: ").strip()
            if sid not in students:
                print("❌ Invalid ID")
                return
            sid_to_delete = sid
    else:
        print("❌ Invalid choice")
        return

    sd = students[sid_to_delete]
    if input(f"Delete {sd['fname']} {sd['lname']}? (yes/no): ").lower() == "yes":
        del students[sid_to_delete]
        attendance.pop(sid_to_delete, None)
        save_json(STUDENTS_FILE, students)
        save_json(ATTENDANCE_FILE, attendance)
        print("✅ Student deleted successfully")
    else:
        print("❌ Deletion cancelled")

# ---------------- COURSE MANAGEMENT ----------------
def add_course(courses):
    cid = input("Course ID: ").strip()
    if cid in courses:
        print("⚠️ Course already exists")
        return
    courses[cid] = {"name": input("Course Name: ").strip(), "teacher": input("Teacher Name: ").strip()}
    save_json(COURSES_FILE, courses)
    print("✅ Course added successfully")

def view_courses(courses):
    if not courses:
        print("⚠️ No courses available")
        return
    print(tabulate([[cid, d["name"], d.get("teacher","N/A")] for cid, d in courses.items()],
                   ["Course ID","Course Name","Teacher"], tablefmt="fancy_grid"))

def delete_course(courses, attendance):
    if not courses:
        print("⚠️ No courses available")
        return
    view_courses(courses)
    cid = input("\nEnter Course ID to delete: ").strip()
    if cid not in courses:
        print("❌ Course not found")
        return
    course_name = courses[cid]["name"]
    if input(f"Delete '{course_name}'? (yes/no): ").lower() != "yes":
        print("❌ Deletion cancelled")
        return
    del courses[cid]
    save_json(COURSES_FILE, courses)
    if input("Also remove attendance records for this course? (yes/no): ").lower() == "yes":
        for sid in attendance:
            attendance[sid] = [r for r in attendance[sid] if r.get("course_id") != cid]
        save_json(ATTENDANCE_FILE, attendance)
        print(f"✅ Course '{course_name}' and its attendance records deleted")
    else:
        print(f"✅ Course '{course_name}' deleted (attendance records kept)")

# ---------------- MARK ATTENDANCE ----------------
def mark_attendance(students, attendance, courses, teacher_name=None):
    if not courses:
        print("⚠️ No courses found. Admin must add course first.")
        return
    if teacher_name:
        tc = get_teacher_courses(courses, teacher_name)
        if not tc:
            print("⚠️ You are not assigned to any courses")
            return
        print(tabulate([[cid, d["name"]] for cid, d in tc.items()],
                       ["Course ID","Course Name"], tablefmt="fancy_grid"))
        course_id = input("Enter Course ID: ").strip()
        if course_id not in tc:
            print("❌ Invalid course ID or not assigned to you")
            return
    else:
        view_courses(courses)
        course_id = input("Enter Course ID: ").strip()
        if course_id not in courses:
            print("❌ Invalid course ID")
            return

    course_name = courses[course_id]["name"]
    month = input("Enter month (e.g., sep, march): ").strip().lower() or date.today().strftime("%B").lower()
    today = input("Enter date (YYYY-MM-DD) or Enter for today: ").strip() or str(date.today())

    print("\n1 ➡️ Present\n2 ➡️ Absent\n3 ➡️ Late\n4 ➡️ Permission")
    for sid, data in students.items():
        if sid not in attendance:
            attendance[sid] = []
        if any(r["date"] == today and r["course_id"] == course_id for r in attendance[sid]):
            print(f"⚠️ {data['fname']} already marked today for course {course_name}")
            continue
        while True:
            choice = input(f"{data['fname']} {data['lname']} (1/2/3/4): ").strip()
            if choice in ("1","2","3","4"):
                break
            print("❌ Invalid input. Enter 1, 2, 3, or 4.")
        status = {"1":"P","2":"A","3":"L","4":"PR"}[choice]
        attendance[sid].append({"date": today, "course_id": course_id, "status": status, "month": month})

    save_json(ATTENDANCE_FILE, attendance)
    print("✅ Attendance recorded for course", course_name)

# ---------------- ATTENDANCE REPORT ----------------
def attendance_report(students, attendance, courses, teacher_name=None):
    course_filter = select_course(courses, teacher_name, allow_all=not teacher_name)
    if course_filter is False:
        return

    table = []
    for sid, data in students.items():
        records = attendance.get(sid, [])
        if course_filter:
            records = [r for r in records if r.get("course_id") == course_filter]
            if records:
                stats = build_course_stats(records)[course_filter]
                table.append([sid, data["fname"], data["lname"], courses[course_filter]["name"],
                               stats["total"], stats["present"], stats["late"],
                               stats["absent"], stats["permission"], f"{attendance_percent(stats)}%"])
        else:
            for cid, stats in build_course_stats(records).items():
                course_name = courses.get(cid, {}).get("name", "N/A")
                table.append([sid, data["fname"], data["lname"], course_name,
                               stats["total"], stats["present"], stats["late"],
                               stats["absent"], stats["permission"], f"{attendance_percent(stats)}%"])

    headers = ["SId","Fname","Lname","Course","Total","Present","Late","Absent","Permission","Attendance %"]
    title = f"Attendance Report for Course: {courses[course_filter]['name']}" if course_filter else "Attendance Report (All Courses)"
    print(f"\n📊 {title}")
    if table:
        print(tabulate(table, headers, tablefmt="fancy_grid"))
    else:
        print("⚠️ No records found")

# ---------------- MONTHLY TREND ----------------
def monthly_trend_report(students, attendance, courses, teacher_name=None):
    course_filter = select_course(courses, teacher_name, allow_all=not teacher_name)
    if course_filter is False:
        return
    month = input("Enter month (e.g., sep, march, 2026-03): ").strip().lower()

    table = []
    for sid, data in students.items():
        records = [r for r in attendance.get(sid, [])
                   if r.get("month","").lower() == month or r["date"].startswith(month)]
        if course_filter:
            records = [r for r in records if r.get("course_id") == course_filter]
            if records:
                stats = build_course_stats(records)[course_filter]
                table.append([sid, data["fname"], data["lname"], courses[course_filter]["name"],
                               stats["total"], stats["present"], stats["absent"], f"{attendance_percent(stats)}%"])
        else:
            for cid, stats in build_course_stats(records).items():
                course_name = courses.get(cid, {}).get("name", "N/A")
                table.append([sid, data["fname"], data["lname"], course_name,
                               stats["total"], stats["present"], stats["absent"], f"{attendance_percent(stats)}%"])

    print(f"\n📅 Monthly Attendance Trend - {month}")
    if course_filter:
        print(f"Course: {courses[course_filter]['name']}")
    if table:
        print(tabulate(table, ["SId","Fname","Lname","Course","Total","Present","Absent","Attendance %"], tablefmt="fancy_grid"))
    else:
        print("⚠️ No attendance records found for this month")

# ---------------- DATE-WISE REPORT ----------------
def date_report(students, attendance, courses, teacher_name=None):
    course_filter = select_course(courses, teacher_name, allow_all=not teacher_name)
    if course_filter is False:
        return
    teacher_courses = get_teacher_courses(courses, teacher_name) if teacher_name else {}

    d = input("Enter date (YYYY-MM-DD): ").strip()
    table = []
    for sid, data in students.items():
        for r in attendance.get(sid, []):
            if r.get("date") != d:
                continue
            cid = r.get("course_id", "N/A")
            if course_filter and cid != course_filter:
                continue
            if teacher_name and cid not in teacher_courses:
                continue
            course_name = courses.get(cid, {}).get("name", "N/A")
            table.append([r["date"], sid, data["fname"], data["lname"], course_name, r["status"]])

    print(f"\n📅 Attendance Report for {d}")
    if course_filter:
        print(f"Course: {courses[course_filter]['name']}")
    if teacher_name:
        print(f"Teacher: {teacher_name}")
    if table:
        print(tabulate(table, ["Date","ID","Fname","Lname","Course","Status"], tablefmt="fancy_grid"))
    else:
        print("⚠️ No records found")

# ---------------- SEARCH STUDENT ----------------
def search_student(students, attendance, courses, teacher_name=None):
    keyword = input("Enter Student ID or Name: ").strip()
    table = []
    found = False

    for sid, data in students.items():
        full_name = f"{data['fname']} {data['lname']}".lower()
        if keyword != sid and keyword.lower() not in full_name:
            continue

        records = attendance.get(sid, [])
        stats_map = build_course_stats(records)

        if teacher_name:
            tc = get_teacher_courses(courses, teacher_name)
            for cid, stats in stats_map.items():
                if cid not in tc:
                    continue
                table.append([sid, data["fname"], data["lname"], tc[cid]["name"],
                               stats["present"], stats["absent"], stats["late"],
                               stats["permission"], f"{attendance_percent(stats)}%"])
                found = True
        else:
            for cid, stats in stats_map.items():
                course_name = courses.get(cid, {}).get("name", "N/A")
                table.append([sid, data["fname"], data["lname"], course_name,
                               data.get("contact", "N/A"), f"{attendance_percent(stats)}%"])
                found = True

    if found:
        print("\n🎓 Student Found")
        if teacher_name:
            print(tabulate(table, ["ID","Fname","Lname","Course","Present","Absent","Late","Permission","Attendance %"], tablefmt="fancy_grid"))
        else:
            print(tabulate(table, ["ID","Fname","Lname","Course","Phone","Attendance %"], tablefmt="fancy_grid"))
    else:
        print("❌ Student not found" + (" or not enrolled in your courses" if teacher_name else ""))

# ---------------- TOTAL ATTENDANCE REPORT ----------------
def total_attendance_report(students, attendance):
    table = []
    for sid, data in students.items():
        records = attendance.get(sid, [])
        total   = len(records)
        present = sum(1 for r in records if r["status"] in ["P", "L", "PR"])
        absent  = sum(1 for r in records if r["status"] == "A")
        percent = round((present / total * 100), 2) if total > 0 else 0
        table.append([sid, data["fname"], data["lname"], total, present, absent, f"{percent}%"])
    print("\n📊 TOTAL STUDENT ATTENDANCE REPORT")
    if table:
        print(tabulate(table, ["ID","First Name","Last Name","Total Class","Present","Absent","Attendance %"], tablefmt="fancy_grid"))
    else:
        print("⚠️ No records found")

# ---------------- TOP STUDENTS ----------------
def top_students(students, attendance):
    ranking = []
    for sid, data in students.items():
        stats_map = build_course_stats(attendance.get(sid, []))
        if not stats_map:
            continue
        avg = round(sum(attendance_percent(s) for s in stats_map.values()) / len(stats_map), 2)
        ranking.append((avg, data["fname"], data["lname"]))
    ranking.sort(reverse=True)
    medals = ["🥇","🥈","🥉"]
    table = [[medals[i] if i < 3 else "", f, l, f"{p}%"] for i,(p,f,l) in enumerate(ranking[:5])]
    if table:
        print(tabulate(table, ["Rank","Fname","Lname","Avg Attendance %"], tablefmt="fancy_grid"))
    else:
        print("⚠️ No attendance records found")

# ---------------- LOW ATTENDANCE ----------------
def low_warning(students, attendance):
    table = []
    for sid, data in students.items():
        stats_map = build_course_stats(attendance.get(sid, []))
        for cid, stats in stats_map.items():
            pct = attendance_percent(stats)
            if pct < 75:
                table.append(["⚠️", data["fname"], data["lname"], cid, f"{pct}%"])
    if table:
        print(tabulate(table, ["Warning","Fname","Lname","Course ID","Attendance %"], tablefmt="fancy_grid"))
    else:
        print("✅ No low attendance students")

# ---------------- DAILY SUMMARY ----------------
def daily_summary(students, attendance, courses, teacher_name=None):
    course_filter = select_course(courses, teacher_name, allow_all=not teacher_name)
    if course_filter is False:
        return

    selected_date = input("Enter Date (YYYY-MM-DD): ").strip() or str(date.today())
    course_summary = {}

    for sid, data in students.items():
        for r in attendance.get(sid, []):
            if r["date"] != selected_date:
                continue
            cid = r.get("course_id", "N/A")
            if course_filter and cid != course_filter:
                continue
            if cid not in course_summary:
                course_summary[cid] = {"present":0,"absent":0,"late":0,"permission":0,"total":0,"absent_students":[]}
            course_summary[cid]["total"] += 1
            if r["status"] == "P":    course_summary[cid]["present"] += 1
            elif r["status"] == "A":
                course_summary[cid]["absent"] += 1
                course_summary[cid]["absent_students"].append(f"{data['fname']} {data['lname']}")
            elif r["status"] == "L":  course_summary[cid]["late"] += 1
            elif r["status"] == "PR": course_summary[cid]["permission"] += 1

    print(f"\n📊 Daily Summary for {selected_date}")
    table = []
    for cid, stats in course_summary.items():
        course_name = courses.get(cid, {}).get("name", "N/A")
        table.append([course_name, stats["total"], stats["present"], stats["late"],
                      stats["absent"], stats["permission"], f"{attendance_percent(stats)}%"])
    if table:
        print(tabulate(table, ["Course","Total Students","Present","Late","Absent","Permission","Attendance %"], tablefmt="fancy_grid"))
        for cid, stats in course_summary.items():
            if stats["absent_students"]:
                print(f"\n❌ Absent Students in {courses.get(cid,{}).get('name',cid)}:")
                for s in stats["absent_students"]:
                    print(f"  • {s}")
    else:
        print("⚠️ No attendance records found")

# ---------------- ADMIN MENU ----------------
def admin_menu():
    while True:
        students   = load_json(STUDENTS_FILE)
        attendance = load_json(ATTENDANCE_FILE)
        courses    = load_json(COURSES_FILE)
        print("\n===== ADMIN MENU =====")
        print("1  Add Student")
        print("2  View Students")
        print("3  Delete Student")
        print("4  Add Course")
        print("5  View Courses")
        print("6  Delete Course")
        print("7  Attendance Report")
        print("8  Monthly Attendance Trend")
        print("9  Date-wise Report")
        print("10 Search Student")
        print("11 Total Attendance Report")
        print("12 Top Students")
        print("13 Low Attendance Warning")
        print("14 Daily Summary")
        print("15 Exit")
        choice = input("Choice: ").strip()
        if   choice == "1":  add_student(students)
        elif choice == "2":  view_students(students)
        elif choice == "3":  delete_student(students, attendance)
        elif choice == "4":  add_course(courses)
        elif choice == "5":  view_courses(courses)
        elif choice == "6":  delete_course(courses, attendance)
        elif choice == "7":  attendance_report(students, attendance, courses)
        elif choice == "8":  monthly_trend_report(students, attendance, courses)
        elif choice == "9":  date_report(students, attendance, courses)
        elif choice == "10": search_student(students, attendance, courses)
        elif choice == "11": total_attendance_report(students, attendance)
        elif choice == "12": top_students(students, attendance)
        elif choice == "13": low_warning(students, attendance)
        elif choice == "14": daily_summary(students, attendance, courses)
        elif choice == "15": break
        else: print("❌ Invalid choice")

# ---------------- TEACHER MENU ----------------
def teacher_menu(teacher_name):
    while True:
        students   = load_json(STUDENTS_FILE)
        attendance = load_json(ATTENDANCE_FILE)
        courses    = load_json(COURSES_FILE)
        print(f"\n===== TEACHER MENU ({teacher_name}) =====")
        print("1 View Students")
        print("2 Mark Attendance")
        print("3 Attendance Report")
        print("4 Monthly Attendance Trend")
        print("5 Date-wise Report")
        print("6 Search Student")
        print("7 Daily Summary")
        print("8 Exit")
        choice = input("Choice: ").strip()
        if   choice == "1": view_students(students)
        elif choice == "2": mark_attendance(students, attendance, courses, teacher_name)
        elif choice == "3": attendance_report(students, attendance, courses, teacher_name)
        elif choice == "4": monthly_trend_report(students, attendance, courses, teacher_name)
        elif choice == "5": date_report(students, attendance, courses, teacher_name)
        elif choice == "6": search_student(students, attendance, courses, teacher_name)
        elif choice == "7": daily_summary(students, attendance, courses, teacher_name)
        elif choice == "8": break
        else: print("❌ Invalid choice")

# ---------------- RUN ----------------
result = login()
if result:
    role, teacher_name = result
    if role == "admin":
        admin_menu()
    elif role == "teacher":
        teacher_menu(teacher_name)
else:
    print("❌ Access denied")