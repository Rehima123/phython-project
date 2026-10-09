import json
import os

# -------------------------
# LOGIN SYSTEM
# -------------------------

USERS = {
    "admin": "1234",
    "teacher": "1111"
}


def login():

    print("\n===== LOGIN =====")

    username = input("Username: ")
    password = input("Password: ")

    if username in USERS and USERS[username] == password:
        print("Login Successful\n")
        return True

    print("Invalid login\n")
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

        student_id = input("Enter ID: ")

        if student_id in self.students:
            print("Student already exists")
            return

        name = input("Enter Name: ")

        self.students[student_id] = Student(student_id, name)

        print("Student Added")

    # -------------------------
    # LIST STUDENTS
    # -------------------------

    def list_students(self):

        if not self.students:
            print("No students")
            return

        print("\nID     Name")
        print("-------------------")

        for s in self.students.values():
            print(f"{s.student_id:<6} {s.name}")

    # -------------------------
    # MARK ATTENDANCE
    # -------------------------

    def mark_attendance(self):

        date = input("Enter date (YYYY-MM-DD): ")

        print("\n1 Present")
        print("2 Absent")
        print("3 Late")

        for s in self.students.values():

            if any(r["date"] == date for r in s.attendance):

                print(f"{s.name} already marked today")
                continue

            choice = input(f"{s.name} status: ")

            if choice == "1":
                status = "P"

            elif choice == "2":
                status = "A"

            elif choice == "3":
                status = "L"

            else:
                print("Invalid")
                continue

            s.attendance.append({
                "date": date,
                "status": status
            })

        print("Attendance saved")

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

        keyword = input("Enter ID or Name: ").lower()

        for s in self.students.values():

            if keyword in s.student_id.lower() or keyword in s.name.lower():

                print("\nID:", s.student_id)
                print("Name:", s.name)

                percent = self.calculate_percentage(s)

                print("Attendance %:", round(percent, 1))

    # -------------------------
    # DAILY REPORT
    # -------------------------

    def daily_report(self):

        date = input("Enter date: ")
        
        course_filter = input("Enter course ID (or press Enter for all): ").strip()

        print("\nID    Name       Status")
        print("------------------------")

        for s in self.students.values():

            for r in s.attendance:

                if r["date"] == date:
                    
                    # Apply course filter if provided
                    if course_filter:
                        if r.get("course_id") != course_filter:
                            continue

                    print(
                        f"{s.student_id:<5} {s.name:<10} {r['status']}"
                    )

    # -------------------------
    # MONTHLY REPORT
    # -------------------------

    def monthly_report(self):

        month = input("Enter month (YYYY-MM): ")
        
        course_filter = input("Enter course ID (or press Enter for all): ").strip()

        print("\nStudent   Present   Absent   %")

        for s in self.students.values():

            records = [
                r for r in s.attendance
                if r["date"].startswith(month)
            ]
            
            # Apply course filter if provided
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

            print(
                f"{s.name:<10} {present:<8} {total-present:<8} {percent:.1f}%"
            )

    # -------------------------
    # TOP STUDENTS
    # -------------------------

    def top_students(self):

        ranking = []

        for s in self.students.values():

            percent = self.calculate_percentage(s)

            ranking.append((percent, s.name))

        ranking.sort(reverse=True)

        print("\nTop Attendance Students")

        for i, (p, name) in enumerate(ranking[:5], 1):

            print(f"{i}. {name} - {p:.1f}%")

    # -------------------------
    # LOW ATTENDANCE WARNING
    # -------------------------

    def low_warning(self):

        print("\nLow Attendance Students (<75%)")

        for s in self.students.values():

            percent = self.calculate_percentage(s)

            if percent < 75:

                print(f"{s.name} - {percent:.1f}%")

    # -------------------------
    # REMOVE STUDENT
    # -------------------------

    def remove_student(self):

        sid = input("Enter student ID: ")

        if sid in self.students:

            del self.students[sid]

            print("Student removed")

        else:

            print("Not found")

    # -------------------------
    # SUMMARY
    # -------------------------

    def summary(self):

        today = input("\nEnter today's date: ")

        present = 0
        absent = 0

        for s in self.students.values():

            for r in s.attendance:

                if r["date"] == today:

                    if r["status"] in ["P", "L"]:
                        present += 1
                    else:
                        absent += 1

        print("\n===== DAILY SUMMARY =====")

        print("Total Students:", len(self.students))
        print("Present Today:", present)
        print("Absent Today:", absent)

    # -------------------------
    # MAIN MENU
    # -------------------------

    def run(self):

        while True:

            print("\n===== ATTENDANCE SYSTEM =====")

            print("1 Add Student")
            print("2 Mark Attendance")
            print("3 List Students")
            print("4 Search Student")
            print("5 Daily Report")
            print("6 Monthly Report")
            print("7 Top Attendance Students")
            print("8 Low Attendance Warning")
            print("9 Remove Student")
            print("10 Exit")

            choice = input("Choose: ")

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

                print("\nData saved. Goodbye!")

                break

            else:
                print("Invalid choice")


# -------------------------
# RUN PROGRAM
# -------------------------

if __name__ == "__main__":

    if login():

        system = AttendanceSystem()

        system.run()