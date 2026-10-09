from datetime import date
import os
import json
from style import (
    section, menu, success, error, warn, info,
    title_line, prompt, login_screen, pct_bar, styled_table, C
)
try:
    import pyttsx3
    engine = pyttsx3.init()
except ImportError:
    engine = None

STUDENTS_FILE = "students.json"
ATTENDANCE_FILE = "attendance.json"
COURSES_FILE = "courses.json"

USERS = {
    "admin":   {"username": "admin",   "password": "admin123", "role": "admin"},
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
            warn("You are not assigned to any courses")
            return False
        section(f"Your Courses — {teacher_name}")
        styled_table(["Course ID", "Course Name"], [[cid, d["name"]] for cid, d in tc.items()])
        cid = prompt("Enter Course ID").strip()
        if cid not in tc:
            error("Invalid course ID or not assigned to you")
            return False
        return cid
    else:
        if courses:
            section("Available Courses")
            view_courses(courses)
        _prompt = "Enter Course ID (or press Enter for all)" if allow_all else "Enter Course ID"
        cid = prompt(_prompt).strip()
        if cid and cid not in courses:
            error("Invalid course ID")
            return False
        return cid if cid else None

# ---------------- LOGIN ----------------
def login():
    login_screen()

    # ── Role selection ──
    while True:
        menu("Select Role", [("1", "Admin"), ("2", "Teacher")])
        role_choice = prompt("Select role (1/2)").strip()
        if role_choice in ("1", "2"):
            break
        error("Invalid choice. Enter 1 or 2.")

    username = prompt("Username").strip()
    password = prompt("Password").strip()

    if role_choice == "1":
        admin = USERS["admin"]
        if username == admin["username"] and password == admin["password"]:
            success("Login successful!  Role: ADMIN")
            if engine:
                engine.say("Thank you, successfully logged in as admin")
                engine.runAndWait()
            return ("admin", None)
        error("Invalid username or password")
        return None

    elif role_choice == "2":
        for user_data in USERS.values():
            if (user_data["role"] == "teacher"
                    and username.lower() == user_data["username"].lower()
                    and password == user_data["password"]):
                teacher_name = user_data.get("name", username)
                success(f"Login successful!  Role: Instructor ({teacher_name})")
                if engine:
                    engine.say(f"Thank you, successfully logged in as {teacher_name}")
                    engine.runAndWait()
                return ("teacher", teacher_name)
        error("Invalid username or password")
        return None

# ---------------- STUDENT MANAGEMENT ----------------
def add_student(students):
    section("Add New Student")
    sid = prompt("Student ID")
    if sid in students:
        warn("Student already exists")
        return
    students[sid] = {
        "fname":      prompt("First Name"),
        "lname":      prompt("Last Name"),
        "age":        prompt("Age"),
        "department": prompt("Department"),
        "year":       prompt("Year"),
        "section":    prompt("Section"),
        "contact":    prompt("Contact")
    }
    save_json(STUDENTS_FILE, students)
    success("Student added successfully")

def view_students(students):
    if not students:
        warn("No students available")
        return
    rows = [[sid, d["fname"], d["lname"], d["age"], d["department"], d["year"], d["section"], d["contact"]]
            for sid, d in students.items()]
    styled_table(["ID","Fname","Lname","Age","Dept","Year","Section","Contact"], rows)

def delete_student(students, attendance):
    section("Delete Student")
    menu("Delete By", [("1", "Delete by ID"), ("2", "Delete by Name")])
    choice = prompt("Choose option (1/2)").strip()
    sid_to_delete = None

    if choice == "1":
        sid = prompt("Enter student ID").strip()
        if sid not in students:
            error("Student not found")
            return
        sid_to_delete = sid
    elif choice == "2":
        name = prompt("Enter student name (first or last)").lower().strip()
        matches = [(sid, d) for sid, d in students.items()
                   if name in d["fname"].lower() or name in d["lname"].lower()]
        if not matches:
            error("Student not found")
            return
        elif len(matches) == 1:
            info(f"Found: {matches[0][1]['fname']} {matches[0][1]['lname']} (ID: {matches[0][0]})")
            sid_to_delete = matches[0][0]
        else:
            title_line("Multiple students found:")
            styled_table(["ID","Fname","Lname","Department"],
                         [[s, d["fname"], d["lname"], d["department"]] for s, d in matches])
            sid = prompt("Enter the ID of the student to delete").strip()
            if sid not in students:
                error("Invalid ID")
                return
            sid_to_delete = sid
    else:
        error("Invalid choice")
        return

    sd = students[sid_to_delete]
    if prompt(f"Delete {sd['fname']} {sd['lname']}? (yes/no)").lower() == "yes":
        del students[sid_to_delete]
        attendance.pop(sid_to_delete, None)
        save_json(STUDENTS_FILE, students)
        save_json(ATTENDANCE_FILE, attendance)
        success("Student deleted successfully")
    else:
        warn("Deletion cancelled")

# ---------------- COURSE MANAGEMENT ----------------
def add_course(courses):
    section("Add New Course")
    cid = prompt("Course ID").strip()
    if cid in courses:
        warn("Course already exists")
        return
    courses[cid] = {"name": prompt("Course Name").strip(), "teacher": prompt("Teacher Name").strip()}
    save_json(COURSES_FILE, courses)
    success("Course added successfully")

def view_courses(courses):
    if not courses:
        warn("No courses available")
        return
    styled_table(["Course ID","Course Name","Teacher"],
                 [[cid, d["name"], d.get("teacher","N/A")] for cid, d in courses.items()])

def delete_course(courses, attendance):
    if not courses:
        warn("No courses available")
        return
    section("Delete Course")
    view_courses(courses)
    cid = prompt("Enter Course ID to delete").strip()
    if cid not in courses:
        error("Course not found")
        return
    course_name = courses[cid]["name"]
    if prompt(f"Delete '{course_name}'? (yes/no)").lower() != "yes":
        warn("Deletion cancelled")
        return
    del courses[cid]
    save_json(COURSES_FILE, courses)
    if prompt("Also remove attendance records for this course? (yes/no)").lower() == "yes":
        for sid in attendance:
            attendance[sid] = [r for r in attendance[sid] if r.get("course_id") != cid]
        save_json(ATTENDANCE_FILE, attendance)
        success(f"Course '{course_name}' and its attendance records deleted")
    else:
        success(f"Course '{course_name}' deleted (attendance records kept)")

# ---------------- MARK ATTENDANCE ----------------
def mark_attendance(students, attendance, courses, teacher_name=None):
    if not courses:
        warn("No courses found. Admin must add course first.")
        return
    section("Mark Attendance")
    if teacher_name:
        tc = get_teacher_courses(courses, teacher_name)
        if not tc:
            warn("You are not assigned to any courses")
            return
        styled_table(["Course ID","Course Name"],
                     [[cid, d["name"]] for cid, d in tc.items()])
        course_id = prompt("Enter Course ID").strip()
        if course_id not in tc:
            error("Invalid course ID or not assigned to you")
            return
    else:
        view_courses(courses)
        course_id = prompt("Enter Course ID").strip()
        if course_id not in courses:
            error("Invalid course ID")
            return

    course_name = courses[course_id]["name"]
    month = prompt("Enter month (e.g., sep, march)").strip().lower() or date.today().strftime("%B").lower()
    today = prompt("Enter date (YYYY-MM-DD) or Enter for today").strip() or str(date.today())

    menu("Status Options", [("1","Present"), ("2","Absent"), ("3","Late"), ("4","Permission")])
    for sid, data in students.items():
        if sid not in attendance:
            attendance[sid] = []
        if any(r["date"] == today and r["course_id"] == course_id for r in attendance[sid]):
            warn(f"{data['fname']} already marked today for {course_name}")
            continue
        while True:
            choice = prompt(f"{C.BOLD}{C.WHITE}{data['fname']} {data['lname']}{C.RESET}{C.CYAN} (1/2/3/4)").strip()
            if choice in ("1","2","3","4"):
                break
            error("Invalid input. Enter 1, 2, 3, or 4.")
        status = {"1":"P","2":"A","3":"L","4":"PR"}[choice]
        attendance[sid].append({"date": today, "course_id": course_id, "status": status, "month": month})

    save_json(ATTENDANCE_FILE, attendance)
    success(f"Attendance recorded for course: {course_name}")

# ---------------- ATTENDANCE REPORT ----------------
def attendance_report(students, attendance, courses, teacher_name=None):
    section("Attendance Report")
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
    report_title = f"Course: {courses[course_filter]['name']}" if course_filter else "All Courses"
    title_line(f"Attendance Report — {report_title}")
    styled_table(headers, table)

# ---------------- MONTHLY TREND ----------------
def monthly_trend_report(students, attendance, courses, teacher_name=None):
    section("Monthly Attendance Trend")
    course_filter = select_course(courses, teacher_name, allow_all=not teacher_name)
    if course_filter is False:
        return
    month = prompt("Enter month (e.g., sep, march, 2026-03)").strip().lower()

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

    title_line(f"Monthly Trend — {month}")
    if course_filter:
        info(f"Course: {courses[course_filter]['name']}")
    styled_table(["SId","Fname","Lname","Course","Total","Present","Absent","Attendance %"], table)

# ---------------- DATE-WISE REPORT ----------------
def date_report(students, attendance, courses, teacher_name=None):
    section("Date-wise Report")
    course_filter = select_course(courses, teacher_name, allow_all=not teacher_name)
    if course_filter is False:
        return
    teacher_courses = get_teacher_courses(courses, teacher_name) if teacher_name else {}

    d = prompt("Enter date (YYYY-MM-DD)").strip()
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

    title_line(f"Attendance Report — {d}")
    if course_filter:
        info(f"Course: {courses[course_filter]['name']}")
    if teacher_name:
        info(f"Teacher: {teacher_name}")
    styled_table(["Date","ID","Fname","Lname","Course","Status"], table)

# ---------------- SEARCH STUDENT ----------------
def search_student(students, attendance, courses, teacher_name=None):
    section("Search Student")
    keyword = prompt("Enter Student ID or Name").strip()
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
        title_line("Student Found")
        if teacher_name:
            styled_table(["ID","Fname","Lname","Course","Present","Absent","Late","Permission","Attendance %"], table)
        else:
            styled_table(["ID","Fname","Lname","Course","Phone","Attendance %"], table)
    else:
        error("Student not found" + (" or not enrolled in your courses" if teacher_name else ""))

# ---------------- TOTAL ATTENDANCE REPORT ----------------
def total_attendance_report(students, attendance):
    section("Total Attendance Report")
    table = []
    for sid, data in students.items():
        records = attendance.get(sid, [])
        total   = len(records)
        present = sum(1 for r in records if r["status"] in ["P", "L", "PR"])
        absent  = sum(1 for r in records if r["status"] == "A")
        percent = round((present / total * 100), 2) if total > 0 else 0
        table.append([sid, data["fname"], data["lname"], total, present, absent, f"{percent}%"])
    title_line("Total Student Attendance Report")
    styled_table(["ID","First Name","Last Name","Total Class","Present","Absent","Attendance %"], table)

# ---------------- TOP STUDENTS ----------------
def top_students(students, attendance):
    section("Top Attendance Students")
    ranking = []
    for sid, data in students.items():
        stats_map = build_course_stats(attendance.get(sid, []))
        if not stats_map:
            continue
        avg = round(sum(attendance_percent(s) for s in stats_map.values()) / len(stats_map), 2)
        ranking.append((avg, data["fname"], data["lname"]))
    ranking.sort(reverse=True)
    medals = ["🥇","🥈","🥉"]
    table = [[medals[i] if i < 3 else f"#{i+1}", f, l, f"{p}%"] for i,(p,f,l) in enumerate(ranking[:5])]
    if table:
        styled_table(["Rank","Fname","Lname","Avg Attendance %"], table)
    else:
        warn("No attendance records found")

# ---------------- LOW ATTENDANCE ----------------
def low_warning(students, attendance):
    section("Low Attendance Warning  (<75%)")
    table = []
    for sid, data in students.items():
        stats_map = build_course_stats(attendance.get(sid, []))
        for cid, stats in stats_map.items():
            pct = attendance_percent(stats)
            if pct < 75:
                table.append(["⚠️", data["fname"], data["lname"], cid, f"{pct}%"])
    if table:
        styled_table(["Warning","Fname","Lname","Course ID","Attendance %"], table)
    else:
        success("No low attendance students")

# ---------------- DAILY SUMMARY ----------------
def daily_summary(students, attendance, courses, teacher_name=None):
    section("Daily Summary")
    course_filter = select_course(courses, teacher_name, allow_all=not teacher_name)
    if course_filter is False:
        return

    selected_date = prompt("Enter Date (YYYY-MM-DD)").strip() or str(date.today())
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

    title_line(f"Daily Summary — {selected_date}")
    table = []
    for cid, stats in course_summary.items():
        course_name = courses.get(cid, {}).get("name", "N/A")
        table.append([course_name, stats["total"], stats["present"], stats["late"],
                      stats["absent"], stats["permission"], f"{attendance_percent(stats)}%"])
    if table:
        styled_table(["Course","Total Students","Present","Late","Absent","Permission","Attendance %"], table)
        for cid, stats in course_summary.items():
            if stats["absent_students"]:
                print(f"\n{C.BOLD}{C.RED}  Absent in {courses.get(cid,{}).get('name',cid)}:{C.RESET}")
                for s in stats["absent_students"]:
                    print(f"  {C.RED}•{C.RESET} {s}")
    else:
        warn("No attendance records found")

# ---------------- ADMIN MENU ----------------
def admin_menu():
    while True:
        students   = load_json(STUDENTS_FILE)
        attendance = load_json(ATTENDANCE_FILE)
        courses    = load_json(COURSES_FILE)
        menu("ADMIN MENU", [
            ("1",  "Add Student"),
            ("2",  "View Students"),
            ("3",  "Delete Student"),
            ("4",  "Add Course"),
            ("5",  "View Courses"),
            ("6",  "Delete Course"),
            ("7",  "Attendance Report"),
            ("8",  "Monthly Attendance Trend"),
            ("9",  "Date-wise Report"),
            ("10", "Search Student"),
            ("11", "Total Attendance Report"),
            ("12", "Top Students"),
            ("13", "Low Attendance Warning"),
            ("14", "Daily Summary"),
            ("15", "Exit"),
        ])
        choice = prompt("Choice").strip()
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
        else: error("Invalid choice")

# ---------------- TEACHER MENU ----------------
def teacher_menu(teacher_name):
    while True:
        students   = load_json(STUDENTS_FILE)
        attendance = load_json(ATTENDANCE_FILE)
        courses    = load_json(COURSES_FILE)
        menu(f"TEACHER MENU  —  {teacher_name}", [
            ("1", "View Students"),
            ("2", "Mark Attendance"),
            ("3", "Attendance Report"),
            ("4", "Monthly Attendance Trend"),
            ("5", "Date-wise Report"),
            ("6", "Search Student"),
            ("7", "Daily Summary"),
            ("8", "Exit"),
        ])
        choice = prompt("Choice").strip()
        if   choice == "1": view_students(students)
        elif choice == "2": mark_attendance(students, attendance, courses, teacher_name)
        elif choice == "3": attendance_report(students, attendance, courses, teacher_name)
        elif choice == "4": monthly_trend_report(students, attendance, courses, teacher_name)
        elif choice == "5": date_report(students, attendance, courses, teacher_name)
        elif choice == "6": search_student(students, attendance, courses, teacher_name)
        elif choice == "7": daily_summary(students, attendance, courses, teacher_name)
        elif choice == "8": break
        else: error("Invalid choice")

# ---------------- RUN ----------------
while True:
    result = login()
    if result is None:
        if prompt("Try again? (yes/no)").strip().lower() != "yes":
            break
        continue
    role, teacher_name = result
    if role == "admin":
        admin_menu()
    elif role == "teacher":
        teacher_menu(teacher_name)
    break