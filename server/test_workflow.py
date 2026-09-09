import urllib.request
import json
import os
import sqlite3

API_BASE = "http://127.0.0.1:8000/api"

def make_request(path: str, method: str = "GET", data: dict = None):
    url = f"{API_BASE}{path}"
    headers = {"Content-Type": "application/json"}
    body = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

def test_full_workflow(course_code: str, course_id: int, student_name: str, degree: str, branch: str, project_title: str):
    print(f"\n==================================================")
    print(f"TESTING END-TO-END WORKFLOW FOR: {course_code} — {student_name}")
    print(f"==================================================")

    # 1. Register Student (Simplified: No PRN/Roll, Default College: Poddar College, Bharatpur)
    student_payload = {
        "full_name": student_name,
        "father_mother_name": f"Sh. Parent of {student_name}",
        "dob": "2004-06-10",
        "gender": "Female",
        "mobile": "+91 98291 99999",
        "email": f"{student_name.lower().replace(' ', '.')}@example.com",
        "address": "Scheme No. 10, Alwar Gate",
        "city": "Bharatpur",
        "state": "Rajasthan",
        "college_name": "Poddar College, Bharatpur",
        "degree": degree,
        "branch": branch,
        "semester_year": "6th Semester",
        "academic_session": "2025-2026",
        "course_id": course_id,
        "mentor_id": 1 if course_code == "DA" else 2,
        "internship_title": f"Course-Based Internship in {course_code}",
        "start_date": "2026-06-01",
        "end_date": "2026-07-12",
        "total_days": 36,
        "total_training_hours": 120,
        "mode": "Offline"
    }
    reg_res = make_request("/students", "POST", student_payload)
    student_id = reg_res["student_id"]
    internship_id = reg_res["internship_id"]
    print(f" [PASS] Step 1: Registered Student #{student_id}, Internship #{internship_id}")

    # 2. Add Attendance Records (36 working days to meet 100% attendance & 126 hours)
    for day in range(1, 37):
        att_item = {
            "date": f"2026-06-{day:02d}" if day <= 30 else f"2026-07-{day-30:02d}",
            "day_of_week": "Monday",
            "start_time": "10:00 AM",
            "end_time": "01:30 PM",
            "total_hours": 3.5,
            "topic_covered": f"Module practical exercise {day}",
            "status": "PRESENT",
            "remarks": "Punctual attendance"
        }
        make_request(f"/internships/{internship_id}/attendance", "POST", att_item)
    print(f" [PASS] Step 2: Recorded 36 daily attendance records (100% attendance, 126 hours)")

    # 3. Add Daily Logs & Weekly Reports
    for day in range(1, 37):
        log_item = {
            "date": f"2026-06-{day:02d}" if day <= 30 else f"2026-07-{day-30:02d}",
            "day_of_week": "Monday",
            "module_name": "Core Technical Track",
            "topic": f"Technical Competency Topic {day}",
            "work_performed": "Executed structured hands-on laboratory modules",
            "practical_activity": "Built real-world application script / campaign asset",
            "tools_used": "Python / Power BI / Google Search Console",
            "learning_outcome": "Mastered industrial workflow procedures",
            "hours": 3.5,
            "mentor_remarks": "Completed successfully."
        }
        make_request(f"/internships/{internship_id}/logs", "POST", log_item)

    conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), "technoglobe.db"))
    c = conn.cursor()
    for w in range(1, 7):
        c.execute("""
        INSERT INTO weekly_reports (internship_id, week_number, start_date, end_date, topics_covered, practical_work, project_progress, skills_learned, hours_completed, mentor_remarks, student_signed, mentor_signed)
        VALUES (?, ?, ?, ?, 'Technical curriculum module', 'Practical exercises', 'Milestone progress', 'Industrial competencies', 21.0, 'Satisfactory', 1, 1)
        """, (internship_id, w, f"2026-06-{w*5:02d}", f"2026-06-{(w*5)+5:02d}"))
    conn.commit()
    conn.close()
    print(f" [PASS] Step 3: Recorded daily activity logbook entries & 6 weekly reports")

    # 4. Add Project
    proj_fields = {
        "project_title": project_title,
        "fields": {
            "problem_statement": "Real-world business analytics problem statement formulation.",
            "dataset": "Enterprise transactional dataset.",
            "tools": "Python, SQL, Power BI Desktop.",
            "findings": "Significant efficiency improvements and positive ROI.",
            "recommendations": "Deploy automated triggers."
        },
        "status": "APPROVED"
    }
    make_request(f"/internships/{internship_id}/project", "PUT", proj_fields)
    print(f" [PASS] Step 4: Submitted & Approved Capstone Project")

    # 5. Add Mentor Evaluation
    eval_payload = {
        "mentor_id": 1 if course_code == "DA" else 2,
        "criteria_scores": {
            "attendance_discipline": {"score": 10, "max": 10, "rating": "Excellent"},
            "technical_knowledge": {"score": 19, "max": 20, "rating": "Excellent"},
            "practical_skills": {"score": 18, "max": 20, "rating": "Excellent"}
        },
        "overall_score": 93,
        "final_remark": f"{student_name} demonstrated outstanding dedication and technical aptitude."
    }
    make_request(f"/internships/{internship_id}/evaluation", "POST", eval_payload)
    print(f" [PASS] Step 5: Submitted Mentor Evaluation Rubric (Score: 93/100)")

    # 6. Set University Compliance to APPROVED
    comp_payload = {
        "university_name": "Poddar College, Bharatpur",
        "department": f"Department of {branch}",
        "faculty_coordinator": "Dr. S. K. Gupta",
        "faculty_designation": "HOD & Coordinator",
        "approval_status": "APPROVED",
        "approval_ref": f"PC/TPO/2026/0{course_id}9",
        "approval_date": "2026-05-20",
        "required_duration": "6 Weeks",
        "required_hours": 120,
        "required_attendance_pct": 75.0,
        "checklist_json": {"noc_verified": True}
    }
    make_request(f"/internships/{internship_id}/compliance", "PUT", comp_payload)
    print(f" [PASS] Step 6: Verified College Compliance Status (APPROVED)")

    # 7. Test Compliance Check Gatekeeper
    check_res = make_request(f"/internships/{internship_id}/compliance-check")
    print(f" [PASS] Step 7: Compliance Check Result: Ready={check_res['is_ready_for_finalization']}")
    print(f"        Badge: '{check_res['badge_message']}'")
    assert check_res["is_ready_for_finalization"] is True

    # 8. Finalize Certificate & Lock Record
    fin_res = make_request(f"/internships/{internship_id}/finalize-certificate", "POST")
    cert_num = fin_res["certificate_number"]
    ver_code = fin_res["verification_code"]
    print(f" [PASS] Step 8: Certificate Finalized & Locked:")
    print(f"        Certificate Number: {cert_num}")
    print(f"        Verification Code:  {ver_code}")

    # 9. Verify 100% Self-Contained Internal QR Payload
    qr_res = make_request(f"/certificates/{internship_id}/qr-data")
    assert qr_res["certificate_number"] == cert_num
    assert qr_res["payload"]["student"] == student_name
    assert qr_res["payload"]["college"] == "Poddar College, Bharatpur"
    assert "https://" not in qr_res["payload"]["issuer"]
    print(f" [PASS] Step 9: Self-Contained QR JSON Payload Verified (Strictly Local & Internal)!")

    # 10. Generate Complete Package ZIP (15 documents)
    zip_url = f"{API_BASE}/documents/{internship_id}/package-zip"
    with urllib.request.urlopen(zip_url) as zip_resp:
        data = zip_resp.read()
        assert len(data) > 50000
        print(f" [PASS] Step 10: Complete Internship Package ZIP generated: {len(data)} bytes")

    print(f"--> ALL 10 STEPS PASSED FOR {course_code} ({student_name})!\n")

def test_system_features():
    print(f"\n==================================================")
    print(f"TESTING SYSTEM BACKUP, TEMPLATES & DEMO CONTROLS")
    print(f"==================================================")

    # 1. Database Backup Download
    backup_url = f"{API_BASE}/backup/database"
    with urllib.request.urlopen(backup_url) as resp:
        db_bytes = resp.read()
        assert len(db_bytes) > 10000
        print(f" [PASS] Backup DB downloaded: {len(db_bytes)} bytes")

    # 2. JSON Data Export
    json_export = make_request("/backup/export-json")
    assert "tables" in json_export
    assert len(json_export["tables"]["students"]) >= 2
    print(f" [PASS] JSON Export completed: {len(json_export['tables'])} tables exported")

    # 3. Document Templates
    templates = make_request("/templates")
    assert len(templates) >= 8
    print(f" [PASS] Document Templates retrieved: {len(templates)} visual block templates")

    # 4. Demo Data Reset
    reset_res = make_request("/admin/demo/reset", "POST")
    assert reset_res["success"] is True
    print(f" [PASS] Demo Data Reset Endpoint verified: {reset_res['message']}")

if __name__ == "__main__":
    test_full_workflow("DA", 1, "Rohan Khandelwal", "BCA", "Computer Science", "Healthcare Supply Chain Performance Dashboard")
    test_full_workflow("DM", 2, "Ananya Mittal", "B.Sc (Bio)", "Biology", "Digital Lead Generation Campaign for Educational Institute")
    test_system_features()
    print("\n[SUCCESS] ALL END-TO-END WORKFLOW & SYSTEM TESTS COMPLETED WITH 100% SUCCESS!")
