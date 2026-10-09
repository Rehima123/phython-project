import json
import os
from style import section, menu, success, error, warn, info, title_line, prompt, login_screen, styled_table, C

# -------------------------
# LOGIN SYSTEM
# -------------------------

USERS = {
    "admin": "1234",
    "teacher": "1111"
}


def login():
    login_screen()
    username = prompt("Username")
    password = prompt("Password")

    if username in USERS and USERS[username] == password:
        success("Login Successful")
        return True

    error("Invalid login")
    return False


# -------------------------
# STUDENT CLASS
# -------------------------

class Student:

    def __init__(self, student_id, name):
        self.student_id = student_id
        self.name = name
        self.attendance = []

    def to_dict(self):
        return {
            "id": self.student_id,
            "name": self.name,
            "attendance": self.attendance
        }


# -------------------------
# ATTENDANCE SYSTEM
# -------------------------

class AttendanceSystem:

    def __init__(self):

        self.students = {}
        self.file = "students.json"

        self.load_data()

    # -------------------------
    # DATA STORAGE
    # -------------------------

    def load_data(self):

        if os.path.exists(self.file):

            with open(self.file, "r") as f:

                data = json.load(f)

                for s in data:
                    student = Student(s["id"], s["name"])
                    student.attendance = s["attendance"]
                    self.students[s["id"]] = student

    def save_data(self):

        data = [s.to_dict() for s in self.students.values()]

        with open(self.file, "w") as f:
            json.dump(data, f, indent=4)

    # -------------------------
    # ADD STUDENT
    # -------------------------

    def add_student(self):
        section("Add New Student")
        student_id = prompt("Enter ID")

        if student_id in self.students:
            warn("Student already exists")
            return

        name = prompt("Enter Name")

        self.students[student_id] = Student(student_id, name)

        success("Student Added")

    # -------------------------
    # LIST STUDENTS
    # -------------------------

    def list_students(self):
        if not self.students:
            warn("No students")
            return

        section("Student List")
        print(f"  {C.BOLD}{C.CYAN}{'ID':<8} {'Name'}{C.RESET}")
        print(f"  {C.GRAY}{'─'*30}{C.RESET}")

        for s in self.students.values():
            print(f"  {C.YELLOW}{s.student_id:<8}{C.RESET} {C.WHITE}{s.name}{C.RESET}")

    # -------------------------
    # MARK ATTENDANCE
    # -------------------------

    def mark_attendance(self):
        section("Mark Attendance")
        date = prompt("Enter date (YYYY-MM-DD)")

        menu("Status Options", [("1","Present"), ("2","Absent"), ("3","Late")])

        for s in self.students.values():

            if any(r["date"] == date for r in s.attendance):
                warn(f"{s.name} already marked today")
                continue

            choice = prompt(f"{C.BOLD}{C.WHITE}{s.name}{C.RESET}{C.CYAN} status (1/2/3)")

            if choice == "1":
                status = "P"
            elif choice == "2":
                status = "A"
            elif choice == "3":
                status = "L"
            else:
                error("Invalid")
                continue

            s.attendance.append({
                "date": date,
                "status": status
            })

        success("Attendance saved")

    # -------------------------
    # PERCENTAGE
    # -------------------------

    def calculate_percentage(self, student):

        total = len(student.attendance)

        if total == 0:
            return 0

        present = sum(
            1 for r in student.attendance
            if r["status"] in ["P", "L"]
        )

        return (present / total) * 100

    # -------------------------
    # SEARCH STUDENT
    # -------------------------

    def search_student(self):
        section("Search Student")
        keyword = prompt("Enter ID or Name").lower()

        for s in self.students.values():

            if keyword in s.student_id.lower() or keyword in s.name.lower():

                title_line("Student Found")
                info(f"ID:   {s.student_id}")
                info(f"Name: {s.name}")

                percent = self.calculate_percentage(s)

                info(f"Attendance: {percent:.1f}%")

    # -------------------------
    # DAILY REPORT
    # -------------------------

    def daily_report(self):
        section("Daily Report")
        date = prompt("Enter date")
        
        course_filter = prompt("Enter course ID (or press Enter for all)").strip()

        title_line(f"Report — {date}")
        print(f"  {C.BOLD}{C.CYAN}{'ID':<6} {'Name':<12} {'Status'}{C.RESET}")
        print(f"  {C.GRAY}{'─'*30}{C.RESET}")

        for s in self.students.values():

            for r in s.attendance:

                if r["date"] == date:
                    
                    if course_filter:
                        if r.get("course_id") != course_filter:
                            continue

                    status_color = {
                        "P": C.GREEN, "L": C.YELLOW, "A": C.RED
                    }.get(r["status"], C.WHITE)
                    print(
                        f"  {C.YELLOW}{s.student_id:<6}{C.RESET} {C.WHITE}{s.name:<12}{C.RESET} {C.BOLD}{status_color}{r['status']}{C.RESET}"
                    )

    # -------------------------
    # MONTHLY REPORT
    # -------------------------

    def monthly_report(self):
        section("Monthly Report")
        month = prompt("Enter month (YYYY-MM)")
        
        course_filter = prompt("Enter course ID (or press Enter for all)").strip()

        title_line(f"Monthly Report — {month}")
        print(f"  {C.BOLD}{C.CYAN}{'Student':<12} {'Present':<9} {'Absent':<9} {'%'}{C.RESET}")
        print(f"  {C.GRAY}{'─'*40}{C.RESET}")

        for s in self.students.values():

            records = [
                r for r in s.attendance
                if r["date"].startswith(month)
            ]
            
            if course_filter:
                records = [
                    r for r in records
                    if r.get("course_id") == course_filter
                ]

            if not records:
                continue

            present = sum(
                1 for r in records
                if r["status"] in ["P", "L"]
            )

            total = len(records)

            percent = (present / total) * 100

            pct_color = C.GREEN if percent >= 75 else C.YELLOW if percent >= 50 else C.RED
            print(
                f"  {C.WHITE}{s.name:<12}{C.RESET} {C.GREEN}{present:<9}{C.RESET} {C.RED}{total-present:<9}{C.RESET} {C.BOLD}{pct_color}{percent:.1f}%{C.RESET}"
            )

    # -------------------------
    # TOP STUDENTS
    # -------------------------

    def top_students(self):
        section("Top Attendance Students")
        ranking = []

        for s in self.students.values():

            percent = self.calculate_percentage(s)

            ranking.append((percent, s.name))

        ranking.sort(reverse=True)

        medals = ["🥇","🥈","🥉"]
        for i, (p, name) in enumerate(ranking[:5], 1):
            medal = medals[i-1] if i <= 3 else f"#{i}"
            pct_color = C.GREEN if p >= 75 else C.YELLOW if p >= 50 else C.RED
            print(f"  {medal}  {C.WHITE}{name:<20}{C.RESET} {C.BOLD}{pct_color}{p:.1f}%{C.RESET}")

    # -------------------------
    # LOW ATTENDANCE WARNING
    # -------------------------

    def low_warning(self):
        section("Low Attendance Warning  (<75%)")
        found = False

        for s in self.students.values():

            percent = self.calculate_percentage(s)

            if percent < 75:
                pct_color = C.YELLOW if percent >= 50 else C.RED
                print(f"  {C.BOLD}{C.YELLOW}⚠{C.RESET}  {C.WHITE}{s.name:<20}{C.RESET} {C.BOLD}{pct_color}{percent:.1f}%{C.RESET}")
                found = True

        if not found:
            success("No low attendance students")

    # -------------------------
    # REMOVE STUDENT
    # -------------------------

    def remove_student(self):
        section("Remove Student")
        sid = prompt("Enter student ID")

        if sid in self.students:

            del self.students[sid]

            success("Student removed")

        else:

            error("Not found")

    # -------------------------
    # SUMMARY
    # -------------------------

    def summary(self):
        section("Daily Summary")
        today = prompt("Enter today's date")

        present = 0
        absent = 0

        for s in self.students.values():

            for r in s.attendance:

                if r["date"] == today:

                    if r["status"] in ["P", "L"]:
                        present += 1
                    else:
                        absent += 1

        title_line(f"Summary — {today}")
        info(f"Total Students : {len(self.students)}")
        info(f"Present Today  : {C.GREEN}{present}{C.RESET}")
        info(f"Absent Today   : {C.RED}{absent}{C.RESET}")

    # -------------------------
    # MAIN MENU
    # -------------------------

    def run(self):

        while True:

            menu("ATTENDANCE SYSTEM", [
                ("1",  "Add Student"),
                ("2",  "Mark Attendance"),
                ("3",  "List Students"),
                ("4",  "Search Student"),
                ("5",  "Daily Report"),
                ("6",  "Monthly Report"),
                ("7",  "Top Attendance Students"),
                ("8",  "Low Attendance Warning"),
                ("9",  "Remove Student"),
                ("10", "Exit"),
            ])

            choice = prompt("Choose")

            if choice == "1":
                self.add_student()

            elif choice == "2":
                self.mark_attendance()

            elif choice == "3":
                self.list_students()

            elif choice == "4":
                self.search_student()

            elif choice == "5":
                self.daily_report()

            elif choice == "6":
                self.monthly_report()

            elif choice == "7":
                self.top_students()

            elif choice == "8":
                self.low_warning()

            elif choice == "9":
                self.remove_student()

            elif choice == "10":

                self.save_data()
                self.summary()

                success("Data saved. Goodbye!")

                break

            else:
                error("Invalid choice")


# -------------------------
# RUN PROGRAM
# -------------------------

if __name__ == "__main__":

    if login():

        system = AttendanceSystem()

        system.run()