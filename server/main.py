import os
import sys
sys.path.insert(0, os.path.dirname(__file__))
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, Depends, Header, UploadFile, File, Form, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from database import get_db, init_db
from seed_data import hash_password, seed
import pdf_service
import fitz

app = FastAPI(title="TechnoGlobe Internship & Certificate Management System API", version="1.0.0")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

@app.on_event("startup")
def on_startup():
    init_db()
    seed()

# -------------------------------------------------------------
# Helpers & Audit
# -------------------------------------------------------------
def log_audit(action: str, entity_type: str, entity_id: int, details: dict, user_name: str = "Admin"):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO audit_logs (user_id, user_name, action, entity_type, entity_id, details_json)
        VALUES (1, ?, ?, ?, ?, ?)
        """, (user_name, action, entity_type, entity_id, json.dumps(details)))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Audit log error: {e}")

# -------------------------------------------------------------
# 1. Authentication
# -------------------------------------------------------------
class LoginRequest(BaseModel):
    email: str
    password: str

@app.post("/api/auth/login")
def login(req: LoginRequest):
    conn = get_db()
    cursor = conn.cursor()
    hashed = hash_password(req.password)
    cursor.execute("SELECT id, name, email, role FROM users WHERE email = ? AND password_hash = ?", (req.email, hashed))
    user = cursor.fetchone()
    conn.close()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    user_dict = dict(user)
    # Return user with pseudo-token
    return {
        "success": True,
        "token": f"tg-auth-{user_dict['id']}-{hash_password(user_dict['email'])[:16]}",
        "user": user_dict
    }

@app.get("/api/auth/me")
def get_current_user():
    # Return default admin for simplified frictionless local session
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email, role FROM users WHERE role = 'CENTRE_ADMIN' LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return {"id": 1, "name": "Centre Administrator", "email": "admin@technoglobe.co.in", "role": "CENTRE_ADMIN"}

# -------------------------------------------------------------
# 2. Dashboard Stats
# -------------------------------------------------------------
@app.get("/api/dashboard/stats")
def get_dashboard_stats():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM students")
    total_students = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM internships WHERE status IN ('REGISTERED', 'TRAINING', 'PROJECT_SUBMITTED')")
    active_internships = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM internships WHERE status IN ('COMPLETED', 'CERTIFIED')")
    completed_internships = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM internships i JOIN courses c ON i.course_id = c.id WHERE c.code = 'DA'")
    da_students = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM internships i JOIN courses c ON i.course_id = c.id WHERE c.code = 'DM'")
    dm_students = cursor.fetchone()[0]

    # Attendance overall %
    cursor.execute("""
    SELECT 
        SUM(CASE WHEN status = 'PRESENT' THEN 1 ELSE 0 END) as pres,
        COUNT(*) as total
    FROM attendance
    """)
    att_row = cursor.fetchone()
    avg_att = (att_row[0] / att_row[1] * 100) if att_row and att_row[1] > 0 else 0.0

    cursor.execute("SELECT COUNT(*) FROM internships WHERE status IN ('TRAINING', 'PROJECT_SUBMITTED') AND id NOT IN (SELECT internship_id FROM evaluations)")
    pending_evals = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM certificates WHERE is_finalized = 1")
    certificates_generated = cursor.fetchone()[0]

    # Recent internships list
    cursor.execute("""
    SELECT i.id, i.internship_title, i.start_date, i.end_date, i.status, i.certificate_number,
           s.full_name as student_name, s.college_name, s.degree, s.branch,
           c.name as course_name, c.code as course_code,
           m.name as mentor_name
    FROM internships i
    JOIN students s ON i.student_id = s.id
    JOIN courses c ON i.course_id = c.id
    JOIN mentors m ON i.mentor_id = m.id
    ORDER BY i.id DESC
    LIMIT 10
    """)
    recent_internships = [dict(r) for r in cursor.fetchall()]

    conn.close()

    return {
        "total_students": total_students,
        "active_internships": active_internships,
        "completed_internships": completed_internships,
        "da_students": da_students,
        "dm_students": dm_students,
        "avg_attendance_pct": round(avg_att, 1),
        "pending_evaluations": pending_evals,
        "certificates_generated": certificates_generated,
        "recent_internships": recent_internships
    }

# -------------------------------------------------------------
# 3. Students Management
# -------------------------------------------------------------
class StudentCreate(BaseModel):
    full_name: str
    father_mother_name: str
    dob: str
    gender: str
    mobile: str
    email: str
    address: str
    city: str
    state: str
    college_name: str = "Poddar College, Bharatpur"
    enrollment_roll_no: Optional[str] = ""
    registration_no: Optional[str] = ""
    degree: str
    branch: str
    semester_year: str
    academic_session: str
    # Internship enrollment details
    course_id: int
    mentor_id: int
    batch_id: Optional[int] = None
    internship_title: Optional[str] = ""
    internship_type: Optional[str] = "Course-Based Internship"
    start_date: str
    end_date: str
    total_days: int = 36
    total_training_hours: int = 120
    mode: str = "Offline"

@app.get("/api/students")
def list_students(search: Optional[str] = None, course: Optional[str] = None, status: Optional[str] = None):
    conn = get_db()
    cursor = conn.cursor()

    query = """
    SELECT s.*, 
           i.id as internship_id, i.internship_title, i.status as internship_status, 
           i.certificate_number, i.verification_code, i.start_date, i.end_date,
           c.name as course_name, c.code as course_code,
           m.name as mentor_name
    FROM students s
    LEFT JOIN internships i ON s.id = i.student_id
    LEFT JOIN courses c ON i.course_id = c.id
    LEFT JOIN mentors m ON i.mentor_id = m.id
    WHERE 1=1
    """
    params = []
    if search:
        s_term = f"%{search}%"
        query += " AND (s.full_name LIKE ? OR s.college_name LIKE ? OR s.degree LIKE ? OR i.certificate_number LIKE ?)"
        params.extend([s_term, s_term, s_term, s_term])
    if course:
        query += " AND c.code = ?"
        params.append(course)
    if status:
        query += " AND i.status = ?"
        params.append(status)

    query += " ORDER BY s.id DESC"
    cursor.execute(query, params)
    students = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return students

@app.get("/api/students/{id}")
def get_student(id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE id = ?", (id,))
    st = cursor.fetchone()
    if not st:
        conn.close()
        raise HTTPException(status_code=404, detail="Student not found")
    
    student = dict(st)
    cursor.execute("""
    SELECT i.*, c.name as course_name, c.code as course_code, m.name as mentor_name
    FROM internships i
    JOIN courses c ON i.course_id = c.id
    JOIN mentors m ON i.mentor_id = m.id
    WHERE i.student_id = ?
    """, (id,))
    internships = [dict(r) for r in cursor.fetchall()]
    conn.close()

    student["internships"] = internships
    return student

@app.post("/api/students")
def create_student(req: StudentCreate):
    conn = get_db()
    cursor = conn.cursor()

    college = req.college_name or "Poddar College, Bharatpur"
    cursor.execute("""
    INSERT INTO students (
        full_name, father_mother_name, dob, gender, mobile, email, address, city, state,
        college_name, degree, branch, semester_year, academic_session, is_demo
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
    """, (
        req.full_name, req.father_mother_name, req.dob, req.gender, req.mobile, req.email,
        req.address, req.city, req.state, college,
        req.degree, req.branch, req.semester_year, req.academic_session
    ))
    student_id = cursor.lastrowid

    # Retrieve course to get default title if not provided
    cursor.execute("SELECT name, title, code FROM courses WHERE id = ?", (req.course_id,))
    c_row = cursor.fetchone()
    title = req.internship_title or (c_row["title"] if c_row else "Course-Based Internship")

    # Create Internship record
    cursor.execute("""
    INSERT INTO internships (
        student_id, course_id, batch_id, mentor_id, internship_title, internship_type,
        start_date, end_date, total_days, total_training_hours, mode, status
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'REGISTERED')
    """, (
        student_id, req.course_id, req.batch_id, req.mentor_id, title,
        req.internship_type, req.start_date, req.end_date, req.total_days, req.total_training_hours, req.mode
    ))
    internship_id = cursor.lastrowid

    # Initialize University Compliance record
    cursor.execute("""
    INSERT INTO compliance_records (
        internship_id, university_name, department, approval_status,
        required_duration, required_hours, required_attendance_pct, checklist_json
    ) VALUES (?, ?, ?, 'PENDING', ?, ?, 75.0, '{}')
    """, (internship_id, req.college_name, req.branch, f"{req.total_days // 6} Weeks", req.total_training_hours))

    # Initialize blank project
    cursor.execute("""
    INSERT INTO projects (internship_id, project_title, fields_json, status)
    VALUES (?, ?, '{}', 'IN_PROGRESS')
    """, (internship_id, f"{c_row['name'] if c_row else 'Capstone'} Capstone Project"))

    conn.commit()
    conn.close()

    log_audit("STUDENT_REGISTERED", "STUDENT", student_id, {"student_name": req.full_name, "internship_id": internship_id})
    return {"success": True, "student_id": student_id, "internship_id": internship_id}

# -------------------------------------------------------------
# 4. Courses & Modules Management
# -------------------------------------------------------------
@app.get("/api/courses")
def list_courses():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM courses ORDER BY id ASC")
    courses = [dict(r) for r in cursor.fetchall()]
    for c in courses:
        cursor.execute("SELECT * FROM course_modules WHERE course_id = ? ORDER BY module_number ASC", (c["id"],))
        c["modules"] = [dict(m) for m in cursor.fetchall()]
    conn.close()
    return courses

@app.get("/api/courses/{id}")
def get_course(id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM courses WHERE id = ?", (id,))
    c_row = cursor.fetchone()
    if not c_row:
        conn.close()
        raise HTTPException(status_code=404, detail="Course not found")
    course = dict(c_row)
    cursor.execute("SELECT * FROM course_modules WHERE course_id = ? ORDER BY module_number ASC", (id,))
    course["modules"] = [dict(m) for m in cursor.fetchall()]
    conn.close()
    return course

class CourseModuleUpdate(BaseModel):
    title: str
    description: str
    topics: List[str]
    practical_activities: List[str]
    learning_outcomes: List[str]
    hours: int

@app.put("/api/modules/{id}")
def update_module(id: int, req: CourseModuleUpdate):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE course_modules 
    SET title = ?, description = ?, topics_json = ?, practical_activities_json = ?, learning_outcomes_json = ?, hours = ?
    WHERE id = ?
    """, (req.title, req.description, json.dumps(req.topics), json.dumps(req.practical_activities), json.dumps(req.learning_outcomes), req.hours, id))
    conn.commit()
    conn.close()
    return {"success": True}

# -------------------------------------------------------------
# 5. Mentors & Batches
# -------------------------------------------------------------
@app.get("/api/mentors")
def list_mentors():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM mentors WHERE is_active = 1")
    mentors = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return mentors

@app.get("/api/batches")
def list_batches():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT b.*, c.name as course_name, m.name as mentor_name
    FROM batches b
    JOIN courses c ON b.course_id = c.id
    LEFT JOIN mentors m ON b.mentor_id = m.id
    ORDER BY b.id DESC
    """)
    batches = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return batches

# -------------------------------------------------------------
# 6. Internships Full Detail & Workflow
# -------------------------------------------------------------
@app.get("/api/internships/{id}")
def get_internship_detail(id: int):
    try:
        ctx = pdf_service.get_base_context(id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Internship not found")
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM weekly_reports WHERE internship_id = ? ORDER BY week_number ASC", (id,))
    weeks = [dict(r) for r in cursor.fetchall()]
    cursor.execute("SELECT * FROM daily_logs WHERE internship_id = ? ORDER BY date ASC", (id,))
    logs = [dict(r) for r in cursor.fetchall()]
    conn.close()

    ctx["weeks"] = weeks
    ctx["logs"] = logs
    return ctx

# -------------------------------------------------------------
# 7. University / College Compliance Module & Gatekeeper Check
# -------------------------------------------------------------
class ComplianceUpdate(BaseModel):
    university_name: Optional[str] = ""
    department: Optional[str] = ""
    affiliation_ref: Optional[str] = ""
    faculty_coordinator: Optional[str] = ""
    faculty_designation: Optional[str] = ""
    approval_status: str  # PENDING, APPROVED, NOT_REQUIRED, REJECTED
    approval_ref: Optional[str] = ""
    approval_date: Optional[str] = ""
    noc_document_url: Optional[str] = ""
    approval_letter_url: Optional[str] = ""
    mou_doc_url: Optional[str] = ""
    required_duration: Optional[str] = "6 Weeks"
    required_hours: int = 120
    required_attendance_pct: float = 75.0
    checklist_json: Optional[Dict[str, Any]] = {}

@app.put("/api/internships/{id}/compliance")
def update_compliance(id: int, req: ComplianceUpdate):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE compliance_records
    SET university_name = ?, department = ?, affiliation_ref = ?, faculty_coordinator = ?, faculty_designation = ?,
        approval_status = ?, approval_ref = ?, approval_date = ?, noc_document_url = ?, approval_letter_url = ?,
        mou_doc_url = ?, required_duration = ?, required_hours = ?, required_attendance_pct = ?, checklist_json = ?,
        updated_at = CURRENT_TIMESTAMP
    WHERE internship_id = ?
    """, (
        req.university_name, req.department, req.affiliation_ref, req.faculty_coordinator, req.faculty_designation,
        req.approval_status, req.approval_ref, req.approval_date, req.noc_document_url, req.approval_letter_url,
        req.mou_doc_url, req.required_duration, req.required_hours, req.required_attendance_pct, json.dumps(req.checklist_json), id
    ))
    conn.commit()
    conn.close()
    log_audit("COMPLIANCE_UPDATED", "INTERNSHIP", id, {"approval_status": req.approval_status})
    return {"success": True}

@app.get("/api/internships/{id}/compliance-check")
def run_compliance_check(id: int):
    ctx = pdf_service.get_base_context(id)
    it = ctx["internship"]
    s = ctx["settings"]
    stats = ctx["att_stats"]
    comp = ctx["compliance"]
    proj = ctx["project"]
    eval_rec = ctx["evaluation"]

    # 1. Attendance Check
    total_days = stats["total_days"] or it["total_days"]
    present = stats["present_days"] or 0
    actual_att_pct = (present / total_days * 100) if total_days > 0 else 0.0
    req_att_pct = comp.get("required_attendance_pct", 75.0) or 75.0
    pass_attendance = actual_att_pct >= req_att_pct

    # 2. Hours Check
    actual_hours = stats.get("total_hours_logged", 0) or 0
    req_hours = comp.get("required_hours", 120) or 120
    pass_hours = actual_hours >= req_hours

    # 3. Daily & Weekly Logs Check
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM daily_logs WHERE internship_id = ?", (id,))
    daily_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM weekly_reports WHERE internship_id = ?", (id,))
    weekly_count = cursor.fetchone()[0]
    conn.close()
    pass_logs = daily_count >= 10 and weekly_count >= 4

    # 4. Project Check
    pass_project = (proj.get("status") == "APPROVED") and bool(proj.get("project_title"))

    # 5. Mentor Evaluation Check
    pass_eval = bool(eval_rec) and eval_rec.get("overall_score", 0) >= 50

    # 6. University / College Compliance Check
    app_status = comp.get("approval_status", "PENDING")
    pass_compliance = app_status in ("APPROVED", "NOT_REQUIRED")

    # 7. Authorized Signatory Configured
    pass_signatory = bool(s.get("signatory_name") and s.get("signatory_designation"))

    all_passed = all([
        pass_attendance,
        pass_hours,
        pass_logs,
        pass_project,
        pass_eval,
        pass_compliance,
        pass_signatory
    ])

    checklist = [
        {"name": "Verified Attendance Requirement", "passed": pass_attendance, "detail": f"Actual: {actual_att_pct:.1f}% (Required: {req_att_pct:.1f}%)"},
        {"name": "Total Training Hours Completed", "passed": pass_hours, "detail": f"Logged: {actual_hours:.1f} hrs (Required: {req_hours} hrs)"},
        {"name": "Daily & Weekly Activity Logs", "passed": pass_logs, "detail": f"{daily_count} daily logs, {weekly_count} weekly reports verified"},
        {"name": "Capstone / Live Project Submission", "passed": pass_project, "detail": f"Status: {proj.get('status', 'PENDING')} — '{proj.get('project_title', 'Untitled')}'"},
        {"name": "Mentor Assessment & Rubric Score", "passed": pass_eval, "detail": f"Score: {eval_rec.get('overall_score', 0)}/100 (Passing: 50)"},
        {"name": "University/College Approval Compliance", "passed": pass_compliance, "detail": f"Status: {app_status} (Ref: {comp.get('approval_ref', 'N/A')})"},
        {"name": "Centre Authorized Signatory Configured", "passed": pass_signatory, "detail": f"{s['signatory_name']} ({s['signatory_designation']})"}
    ]

    return {
        "is_ready_for_finalization": all_passed,
        "badge_message": "DOCUMENTATION COMPLETE — READY FOR AUTHORIZED SIGNATURE & STAMP" if all_passed else "COMPLIANCE PENDING — RESOLVE INCOMPLETE REQUIREMENTS BEFORE FINALIZATION",
        "checklist": checklist,
        "is_locked": it.get("is_locked", 0) == 1,
        "certificate_number": it.get("certificate_number")
    }

# -------------------------------------------------------------
# 8. Certificate Finalization
# -------------------------------------------------------------
@app.post("/api/internships/{id}/finalize-certificate")
def finalize_certificate(id: int):
    check = run_compliance_check(id)
    if not check["is_ready_for_finalization"]:
        raise HTTPException(
            status_code=400,
            detail="Cannot finalize certificate: student compliance requirements are not yet completely fulfilled."
        )

    conn = get_db()
    cursor = conn.cursor()

    # Get internship & centre settings
    cursor.execute("SELECT * FROM centre_settings WHERE id = 1")
    s = dict(cursor.fetchone())
    cursor.execute("""
    SELECT i.*, c.code as course_code FROM internships i
    JOIN courses c ON i.course_id = c.id
    WHERE i.id = ?
    """, (id,))
    it = dict(cursor.fetchone())

    # Generate sequence certificate number if not present
    if not it.get("certificate_number"):
        cursor.execute("SELECT COUNT(*) FROM certificates")
        seq = cursor.fetchone()[0] + 1
        year = datetime.now().year
        cert_num = f"{s['cert_prefix']}-{it['course_code']}-{year}-{seq:04d}"
        ver_code = f"VER-{s['cert_prefix']}-{it['course_code']}-{datetime.now().strftime('%m%d')}{seq:03d}"
    else:
        cert_num = it["certificate_number"]
        ver_code = it["verification_code"]

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Build 100% Self-Contained QR JSON Payload
    cursor.execute("SELECT * FROM students WHERE id = ?", (it["student_id"],))
    student = dict(cursor.fetchone())
    cursor.execute("SELECT * FROM courses WHERE id = ?", (it["course_id"],))
    course = dict(cursor.fetchone())
    cursor.execute("SELECT * FROM projects WHERE internship_id = ?", (id,))
    p_row = cursor.fetchone()
    project = dict(p_row) if p_row else {}

    import urllib.parse
    base_url = s.get("verification_base_url") or "http://192.168.0.103:8000"
    base_url = base_url.rstrip("/")
    params = urllib.parse.urlencode({
        "cert": cert_num,
        "name": student['full_name'],
        "course": course['name'],
        "sem": f"{deg_text} ({sem_text})",
        "college": student['college_name'],
        "ver_id": ver_code,
        "date": now_str[:10]
    })
    qr_payload_json = f"{base_url}/verify?{params}"

    # Update internship record with QR payload
    cursor.execute("""
    UPDATE internships
    SET certificate_number = ?, verification_code = ?, qr_payload_json = ?, status = 'CERTIFIED', is_locked = 1, finalized_at = ?
    WHERE id = ?
    """, (cert_num, ver_code, qr_payload_json, now_str, id))

    # Insert or update Certificate record
    cursor.execute("DELETE FROM certificates WHERE internship_id = ? AND cert_type = 'COMPLETION'", (id,))
    cursor.execute("""
    INSERT INTO certificates (internship_id, cert_type, certificate_number, verification_code, qr_payload_json, issue_date, is_finalized, finalized_by)
    VALUES (?, 'COMPLETION', ?, ?, ?, ?, 1, ?)
    """, (id, cert_num, ver_code, qr_payload_json, now_str[:10], s["signatory_name"]))

    conn.commit()
    conn.close()

    log_audit("CERTIFICATE_FINALIZED", "CERTIFICATE", id, {
        "certificate_number": cert_num,
        "verification_code": ver_code,
        "finalized_by": s["signatory_name"]
    })

    return {
        "success": True,
        "certificate_number": cert_num,
        "verification_code": ver_code,
        "finalized_at": now_str,
        "badge_message": "DOCUMENTATION COMPLETE — READY FOR AUTHORIZED SIGNATURE & STAMP"
    }

# -------------------------------------------------------------
# 9. Attendance CRUD
# -------------------------------------------------------------
class AttendanceItem(BaseModel):
    date: str
    day_of_week: str
    start_time: str = "10:00 AM"
    end_time: str = "01:30 PM"
    total_hours: float = 3.5
    topic_covered: Optional[str] = ""
    status: str = "PRESENT"  # PRESENT, ABSENT, LEAVE, HOLIDAY
    remarks: Optional[str] = ""

@app.get("/api/internships/{id}/attendance")
def get_attendance(id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM attendance WHERE internship_id = ? ORDER BY date ASC", (id,))
    records = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return records

@app.post("/api/internships/{id}/attendance")
def save_attendance(id: int, item: AttendanceItem):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO attendance (internship_id, date, day_of_week, start_time, end_time, total_hours, topic_covered, status, student_signed, mentor_signed, remarks)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, 1, ?)
    ON CONFLICT(internship_id, date) DO UPDATE SET
        start_time=excluded.start_time, end_time=excluded.end_time, total_hours=excluded.total_hours,
        topic_covered=excluded.topic_covered, status=excluded.status, remarks=excluded.remarks
    """, (id, item.date, item.day_of_week, item.start_time, item.end_time, item.total_hours, item.topic_covered, item.status, item.remarks))
    conn.commit()
    conn.close()
    return {"success": True}

# -------------------------------------------------------------
# 10. Daily Logs CRUD
# -------------------------------------------------------------
class DailyLogItem(BaseModel):
    date: str
    day_of_week: str
    module_name: str
    topic: str
    work_performed: str
    practical_activity: str
    tools_used: str
    learning_outcome: str
    hours: float = 3.5
    mentor_remarks: Optional[str] = "Completed satisfactorily."

@app.get("/api/internships/{id}/logs")
def get_daily_logs(id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM daily_logs WHERE internship_id = ? ORDER BY date ASC", (id,))
    records = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return records

@app.post("/api/internships/{id}/logs")
def save_daily_log(id: int, item: DailyLogItem):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO daily_logs (internship_id, date, day_of_week, module_name, topic, work_performed, practical_activity, tools_used, learning_outcome, hours, mentor_remarks, student_signed, mentor_signed)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, 1)
    ON CONFLICT(internship_id, date) DO UPDATE SET
        module_name=excluded.module_name, topic=excluded.topic, work_performed=excluded.work_performed,
        practical_activity=excluded.practical_activity, tools_used=excluded.tools_used,
        learning_outcome=excluded.learning_outcome, hours=excluded.hours, mentor_remarks=excluded.mentor_remarks
    """, (id, item.date, item.day_of_week, item.module_name, item.topic, item.work_performed, item.practical_activity, item.tools_used, item.learning_outcome, item.hours, item.mentor_remarks))
    conn.commit()
    conn.close()
    return {"success": True}

# -------------------------------------------------------------
# 11. Project CRUD
# -------------------------------------------------------------
class ProjectSaveRequest(BaseModel):
    project_title: str
    fields: Dict[str, Any]
    status: Optional[str] = "SUBMITTED"

@app.get("/api/internships/{id}/project")
def get_project(id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM projects WHERE internship_id = ?", (id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return {"project_title": "", "fields": {}, "status": "IN_PROGRESS"}
    res = dict(row)
    res["fields"] = json.loads(res.get("fields_json", "{}"))
    return res

@app.put("/api/internships/{id}/project")
def save_project(id: int, req: ProjectSaveRequest):
    conn = get_db()
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    fields = dict(req.fields or {})
    fields["project_title"] = req.project_title
    cursor.execute("""
    INSERT INTO projects (internship_id, project_title, fields_json, status, submitted_at, approved_at)
    VALUES (?, ?, ?, ?, ?, ?)
    ON CONFLICT(internship_id) DO UPDATE SET
        project_title=excluded.project_title, fields_json=excluded.fields_json,
        status=excluded.status, submitted_at=excluded.submitted_at, approved_at=excluded.approved_at
    """, (id, req.project_title, json.dumps(fields), req.status, now_str, now_str if req.status == "APPROVED" else None))
    conn.commit()
    conn.close()
    return {"success": True}

# -------------------------------------------------------------
# 12. Mentor Evaluation CRUD
# -------------------------------------------------------------
class EvaluationSaveRequest(BaseModel):
    mentor_id: int
    criteria_scores: Dict[str, Any]
    overall_score: int
    final_remark: str

@app.get("/api/internships/{id}/evaluation")
def get_evaluation(id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM evaluations WHERE internship_id = ?", (id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return {"criteria_scores": {}, "overall_score": 0, "final_remark": ""}
    res = dict(row)
    res["criteria_scores"] = json.loads(res.get("criteria_scores_json", "{}"))
    return res

@app.post("/api/internships/{id}/evaluation")
def save_evaluation(id: int, req: EvaluationSaveRequest):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO evaluations (internship_id, mentor_id, criteria_scores_json, overall_score, final_remark, mentor_signed)
    VALUES (?, ?, ?, ?, ?, 1)
    ON CONFLICT(internship_id) DO UPDATE SET
        mentor_id=excluded.mentor_id, criteria_scores_json=excluded.criteria_scores_json,
        overall_score=excluded.overall_score, final_remark=excluded.final_remark, evaluated_at=CURRENT_TIMESTAMP
    """, (id, req.mentor_id, json.dumps(req.criteria_scores), req.overall_score, req.final_remark))
    conn.commit()
    conn.close()
    return {"success": True}

# -------------------------------------------------------------
# 13. PDF & ZIP Document Generation Endpoints
# -------------------------------------------------------------
@app.get("/api/documents/{internship_id}/{doc_type}/pdf")
def download_document_pdf(internship_id: int, doc_type: str):
    generators = {
        "offer": pdf_service.generate_offer_letter,
        "joining": pdf_service.generate_joining_letter,
        "schedule": pdf_service.generate_training_schedule,
        "attendance_sheet": pdf_service.generate_attendance_sheet,
        "attendance_summary": pdf_service.generate_attendance_summary,
        "daily_log": pdf_service.generate_daily_logbook,
        "weekly_report": pdf_service.generate_weekly_report,
        "project_assignment": pdf_service.generate_project_assignment,
        "project_report": pdf_service.generate_project_report,
        "evaluation": pdf_service.generate_mentor_evaluation,
        "performance": pdf_service.generate_performance_report,
        "feedback": pdf_service.generate_student_feedback,
        "certificate": pdf_service.generate_completion_certificate,
        "experience": pdf_service.generate_experience_certificate,
        "consolidated": pdf_service.generate_consolidated_report
    }

    if doc_type == "syllabus":
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT course_id FROM internships WHERE id = ?", (internship_id,))
        row = cursor.fetchone()
        conn.close()
        if not row:
            raise HTTPException(status_code=404, detail="Internship not found")
        filepath = pdf_service.generate_course_syllabus(row["course_id"])
    elif doc_type in generators:
        filepath = generators[doc_type](internship_id)
    else:
        raise HTTPException(status_code=400, detail=f"Invalid document type: {doc_type}")

    return FileResponse(filepath, media_type="application/pdf", filename=os.path.basename(filepath))

@app.get("/api/documents/{internship_id}/package-zip")
def download_complete_package_zip(internship_id: int):
    try:
        zip_path = pdf_service.generate_complete_package_zip(internship_id)
        return FileResponse(zip_path, media_type="application/zip", filename=os.path.basename(zip_path))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate ZIP package: {str(e)}")

# -------------------------------------------------------------
# 14. Internal Certificate QR Payload & Details (Strictly Local)
# -------------------------------------------------------------
@app.get("/api/certificates/{internship_id}/qr-data")
def get_certificate_qr_data(internship_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT qr_payload_json, certificate_number, verification_code, issue_date FROM certificates WHERE internship_id = ? AND is_finalized = 1", (internship_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Finalized certificate not found")
    res = dict(row)
    raw_payload = res.get("qr_payload_json", "")
    try:
        payload = json.loads(raw_payload)
    except Exception:
        payload = {"formatted_text": raw_payload}
    return {
        "certificate_number": res["certificate_number"],
        "verification_code": res["verification_code"],
        "issue_date": res["issue_date"],
        "qr_text": raw_payload,
        "payload": payload
    }

@app.get("/api/certificates/verify/{query_code}")
def verify_certificate_endpoint(query_code: str, sig: Optional[str] = None):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT c.*, i.start_date, i.end_date, i.total_training_hours,
           s.full_name as student_name, s.college_name, s.degree, s.branch, s.semester_year,
           cr.name as course_name, cr.title as course_title,
           m.name as mentor_name
    FROM certificates c
    JOIN internships i ON c.internship_id = i.id
    JOIN students s ON i.student_id = s.id
    LEFT JOIN courses cr ON i.course_id = cr.id
    LEFT JOIN mentors m ON i.mentor_id = m.id
    WHERE (c.certificate_number = ? OR c.verification_code = ?)
    """, (query_code.strip(), query_code.strip()))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Certificate not found or pending finalization")
    res = dict(row)
    expected_sig = pdf_service.compute_certificate_signature(
        res["certificate_number"], res["student_name"], res["course_name"], res["issue_date"]
    )
    sig_valid = (not sig or sig.strip().lower() == expected_sig.lower())
    return {
        "valid": True,
        "signature_valid": sig_valid,
        "signature": expected_sig,
        "certificate_number": res["certificate_number"],
        "verification_code": res["verification_code"],
        "issue_date": res["issue_date"],
        "student_name": res["student_name"],
        "college_name": res["college_name"],
        "course_name": res["course_name"],
        "course_title": res["course_title"],
        "program": f"{res['degree']} ({res['branch']})",
        "semester_year": res["semester_year"] or "6th Semester",
        "internship_duration": f"{res.get('duration_weeks', 6)} Weeks ({res['total_training_hours']} Training Hours)",
        "mentor_name": res["mentor_name"],
        "internship_id": res["internship_id"],
        "pdf_download_url": f"/api/documents/{res['internship_id']}/certificate/pdf",
        "status": "AUTHENTIC & OFFICIALLY ISSUED"
    }

@app.get("/api/certificates/verify-signature")
def verify_signature_endpoint(cert: str, name: str, course: str, date: str, sig: str):
    expected_sig = pdf_service.compute_certificate_signature(cert, name, course, date)
    is_valid = (expected_sig.lower() == sig.strip().lower())
    return {
        "valid": is_valid,
        "expected_sig": expected_sig,
        "provided_sig": sig
    }

@app.get("/api/certificates/batch-print")
@app.post("/api/certificates/batch-print")
def batch_print_certificates(ids: Optional[str] = None):
    conn = get_db()
    cursor = conn.cursor()
    if ids and ids.strip():
        id_list = [int(x.strip()) for x in ids.split(",") if x.strip().isdigit()]
        if not id_list:
            raise HTTPException(status_code=400, detail="Invalid internship IDs provided")
        placeholders = ",".join("?" for _ in id_list)
        cursor.execute(f"""
        SELECT i.id, s.full_name 
        FROM internships i 
        JOIN students s ON i.student_id = s.id 
        WHERE i.id IN ({placeholders})
        ORDER BY i.id ASC
        """, tuple(id_list))
    else:
        cursor.execute("""
        SELECT i.id, s.full_name 
        FROM internships i 
        JOIN students s ON i.student_id = s.id 
        ORDER BY i.id ASC
        """)
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        raise HTTPException(status_code=404, detail="No certificate records found for batch print")

    merged_doc = fitz.open()
    for row in rows:
        internship_id = row[0]
        try:
            pdf_path = pdf_service.generate_completion_certificate(internship_id)
            doc = fitz.open(pdf_path)
            merged_doc.insert_pdf(doc)
        except Exception as e:
            print(f"Error generating certificate for internship {internship_id}: {e}")

    if len(merged_doc) == 0:
        raise HTTPException(status_code=500, detail="Could not generate any certificates for batch printing")

    out_path = os.path.join(pdf_service.GENERATED_DIR, "TechnoGlobe_Batch_Certificates_Print_Ready.pdf")
    merged_doc.save(out_path)
    merged_doc.close()

    return FileResponse(
        out_path,
        media_type="application/pdf",
        headers={"Content-Disposition": "inline; filename=TechnoGlobe_Batch_Certificates_Print_Ready.pdf"}
    )

# -------------------------------------------------------------
# 14b. Backup & Restore Endpoints
# -------------------------------------------------------------
DB_PATH = os.path.join(os.path.dirname(__file__), "technoglobe.db")

@app.get("/api/backup/database")
def download_database_backup():
    if not os.path.exists(DB_PATH):
        raise HTTPException(status_code=404, detail="Database file not found")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return FileResponse(
        DB_PATH,
        media_type="application/x-sqlite3",
        filename=f"technoglobe_backup_{timestamp}.db"
    )

@app.post("/api/backup/restore")
async def restore_database(file: UploadFile = File(...)):
    temp_path = os.path.join(UPLOAD_DIR, f"temp_restore_{datetime.now().strftime('%Y%m%d%H%M%S')}.db")
    try:
        content = await file.read()
        with open(temp_path, "wb") as f:
            f.write(content)

        # Validate SQLite integrity
        test_conn = sqlite3.connect(temp_path)
        test_cur = test_conn.cursor()
        test_cur.execute("PRAGMA integrity_check;")
        check = test_cur.fetchone()
        if not check or check[0] != "ok":
            test_conn.close()
            os.remove(temp_path)
            raise HTTPException(status_code=400, detail="Uploaded file failed SQLite integrity check.")

        test_cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('centre_settings', 'students', 'internships')")
        tables = [r[0] for r in test_cur.fetchall()]
        test_conn.close()
        if len(tables) < 3:
            os.remove(temp_path)
            raise HTTPException(status_code=400, detail="Uploaded database lacks essential TechnoGlobe tables.")

        import shutil
        backup_curr = DB_PATH + f".pre_restore_{datetime.now().strftime('%Y%m%d%H%M%S')}.bak"
        if os.path.exists(DB_PATH):
            shutil.copy2(DB_PATH, backup_curr)

        shutil.copy2(temp_path, DB_PATH)
        os.remove(temp_path)

        log_audit("DATABASE_RESTORED", "DATABASE", 1, {"restored_from": file.filename})
        return {"success": True, "message": "Database successfully restored from backup."}
    except HTTPException:
        raise
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise HTTPException(status_code=500, detail=f"Failed to restore database: {str(e)}")

@app.get("/api/backup/export-json")
def export_all_data_json():
    conn = get_db()
    cursor = conn.cursor()
    tables = [
        "centre_settings", "courses", "course_modules", "mentors", "batches",
        "students", "internships", "compliance_records", "attendance",
        "daily_logs", "weekly_reports", "projects", "evaluations",
        "feedback", "certificates", "document_templates", "audit_logs"
    ]
    export_data = {"exported_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "tables": {}}
    for tbl in tables:
        try:
            cursor.execute(f"SELECT * FROM {tbl}")
            rows = [dict(r) for r in cursor.fetchall()]
            export_data["tables"][tbl] = rows
        except Exception:
            export_data["tables"][tbl] = []
    conn.close()
    return export_data

@app.post("/api/admin/demo/reset")
def reset_demo_data_endpoint():
    try:
        from seed_data import reset_demo_data
        reset_demo_data()
        log_audit("DEMO_DATA_RESET", "SYSTEM", 1, {"message": "Demo data reset to 2 demo records"})
        return {"success": True, "message": "Demo data reset successfully with exactly 1 Data Analytics and 1 Digital Marketing student."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reset demo data: {str(e)}")

@app.post("/api/admin/demo/delete")
def delete_demo_data_endpoint():
    try:
        from seed_data import delete_demo_data
        delete_demo_data()
        log_audit("DEMO_DATA_DELETED", "SYSTEM", 1, {"message": "Demo records removed"})
        return {"success": True, "message": "Demo records deleted successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete demo data: {str(e)}")

# -------------------------------------------------------------
# 14c. Document Templates Visual Block Customizer
# -------------------------------------------------------------
@app.get("/api/templates")
def list_document_templates():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM document_templates ORDER BY id ASC")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    for r in rows:
        r["blocks"] = json.loads(r.get("blocks_json", "[]"))
    return rows

@app.get("/api/templates/{template_key}")
def get_document_template(template_key: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM document_templates WHERE template_key = ?", (template_key,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Template not found")
    res = dict(row)
    res["blocks"] = json.loads(res.get("blocks_json", "[]"))
    return res

class TemplateUpdateRequest(BaseModel):
    title: str
    blocks: List[Dict[str, Any]]

@app.put("/api/templates/{template_key}")
def update_document_template(template_key: str, req: TemplateUpdateRequest):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE document_templates
    SET title = ?, blocks_json = ?, updated_at = CURRENT_TIMESTAMP
    WHERE template_key = ?
    """, (req.title, json.dumps(req.blocks), template_key))
    conn.commit()
    conn.close()
    log_audit("TEMPLATE_UPDATED", "DOCUMENT_TEMPLATE", 1, {"template_key": template_key})
    return {"success": True}

# -------------------------------------------------------------
# 14d. Attendance Bulk Update & Planner Operations
# -------------------------------------------------------------
class BulkAttendanceRequest(BaseModel):
    dates: List[str]
    status: str = "PRESENT"
    topic_covered: Optional[str] = None
    start_time: str = "10:00 AM"
    end_time: str = "01:30 PM"
    total_hours: float = 3.5

@app.post("/api/internships/{id}/attendance/bulk")
def bulk_update_attendance(id: int, req: BulkAttendanceRequest):
    conn = get_db()
    cursor = conn.cursor()
    for d_str in req.dates:
        try:
            dt = datetime.strptime(d_str, "%Y-%m-%d")
            day_name = dt.strftime("%A")
        except Exception:
            day_name = "Weekday"
        cursor.execute("""
        INSERT INTO attendance (internship_id, date, day_of_week, start_time, end_time, total_hours, topic_covered, status, student_signed, mentor_signed)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, 1)
        ON CONFLICT(internship_id, date) DO UPDATE SET
            status=excluded.status,
            start_time=excluded.start_time,
            end_time=excluded.end_time,
            total_hours=excluded.total_hours,
            topic_covered=COALESCE(excluded.topic_covered, attendance.topic_covered)
        """, (id, d_str, day_name, req.start_time, req.end_time, req.total_hours, req.topic_covered or "Curriculum Module Task", req.status))
    conn.commit()
    conn.close()
    return {"success": True, "updated_count": len(req.dates)}

@app.post("/api/internships/{id}/attendance/clear")
def clear_attendance(id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM attendance WHERE internship_id = ?", (id,))
    conn.commit()
    conn.close()
    return {"success": True, "message": "Attendance records cleared"}

# -------------------------------------------------------------
# 14e. Guided Quick-Generate Wizard API
# -------------------------------------------------------------
class QuickGenerateRequest(BaseModel):
    # Step 1: Student Information
    full_name: str
    father_mother_name: str
    dob: str = "2004-05-15"
    gender: str = "Male"
    mobile: str = "9829012345"
    email: Optional[str] = None
    address: str = "Poddar College Campus, Bharatpur"
    city: str = "Bharatpur"
    state: str = "Rajasthan"
    college_name: str = "Poddar College, Bharatpur"
    degree: str = "BCA"
    branch: str = "Computer Science"
    semester_year: str = "6th Semester"
    academic_session: str = "2025-2026"

    # Step 2: Course & Track Selection
    course_track: str = "DA"  # "DA" or "DM"
    start_date: str = "2026-06-01"
    end_date: str = "2026-07-12"
    custom_project_title: Optional[str] = None

    # Step 3: Attendance & Logbook Configuration
    attendance_preset: str = "100"  # "100", "95", "90", "85"

    # Step 4: Mentor Evaluation & Compliance
    evaluation_score: int = 94
    mentor_remarks: str = "Demonstrated exemplary technical aptitude, consistency, and professional work ethic throughout the 6-week internship."

@app.post("/api/wizard/quick-generate")
def quick_generate_internship(req: QuickGenerateRequest):
    conn = get_db()
    cursor = conn.cursor()

    # 1. Centre Settings
    cursor.execute("SELECT * FROM centre_settings WHERE id = 1")
    s = dict(cursor.fetchone())

    # 2. Student Email & Record
    student_email = req.email.strip() if req.email and req.email.strip() else f"{req.full_name.lower().replace(' ', '.')}@example.com"
    cursor.execute("""
    INSERT INTO students (
        full_name, father_mother_name, dob, gender, mobile, email, address, city, state,
        college_name, degree, branch, semester_year, academic_session, is_demo
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
    """, (
        req.full_name.strip(), req.father_mother_name.strip(), req.dob, req.gender,
        req.mobile.strip(), student_email, req.address, req.city, req.state,
        req.college_name, req.degree, req.branch, req.semester_year, req.academic_session
    ))
    student_id = cursor.lastrowid

    # 3. Course Track Resolution
    track = req.course_track.upper()
    if track not in ("DA", "DM"):
        track = "DA"
    
    cursor.execute("SELECT * FROM courses WHERE code = ?", (track,))
    course = cursor.fetchone()
    if not course:
        cursor.execute("SELECT * FROM courses ORDER BY id ASC LIMIT 1")
        course = cursor.fetchone()
    course = dict(course)
    course_id = course["id"]
    mentor_id = 1 if track == "DA" else 2

    # 4. Internship Record
    cursor.execute("""
    INSERT INTO internships (
        student_id, course_id, batch_id, mentor_id, internship_title, internship_type,
        start_date, end_date, total_days, total_training_hours, mode, status, is_locked
    ) VALUES (?, ?, 1, ?, ?, 'Course-Based Internship', ?, ?, 36, 126, 'Offline', 'IN_PROGRESS', 0)
    """, (student_id, course_id, mentor_id, course["title"], req.start_date, req.end_date))
    internship_id = cursor.lastrowid

    # 5. Compliance Record (Approved)
    cursor.execute("""
    INSERT INTO compliance_records (
        internship_id, university_name, department, faculty_coordinator, faculty_designation,
        approval_status, approval_ref, approval_date, required_duration, required_hours, required_attendance_pct,
        affiliation_ref
    ) VALUES (?, ?, ?, 'Prof. Anjali Mathur', 'Internship Coordinator', 'APPROVED', 'PC/INT/2026/042', '2026-05-28', '6 Weeks', 120, 75.0, 'BTER/TPO/2026/019')
    """, (internship_id, req.college_name, f"Department of {req.branch}"))

    # 6. 36 Working Days Attendance & Logbook Entries
    leave_set = set()
    if req.attendance_preset == "95":
        leave_set = {14, 28}
    elif req.attendance_preset == "90":
        leave_set = {7, 15, 23, 31}
    elif req.attendance_preset == "85":
        leave_set = {5, 11, 17, 23, 29}

    start_dt = datetime.strptime(req.start_date, "%Y-%m-%d")
    current_dt = start_dt
    day_count = 0
    total_hours = 0.0
    present_count = 0

    da_topics = [
        "Advanced Excel Formulae & Logical Functions", "VLOOKUP, XLOOKUP & Nested Logic", "Pivot Tables & Dynamic Aggregations",
        "Conditional Formatting & Error Trapping", "Advanced Financial & Statistical Modeling", "Relational Database Concepts & Schema Design",
        "SQL Query Syntax: SELECT, WHERE, ORDER BY", "SQL Aggregations: GROUP BY, HAVING, COUNT", "SQL Joins: INNER, LEFT, RIGHT, FULL",
        "SQL Subqueries & Common Table Expressions", "SQL Window Functions: ROW_NUMBER, RANK", "Python Environment Setup & Jupyter Notebooks",
        "Python Data Types, Loops & Control Structures", "NumPy Numerical Operations & Arrays", "Pandas Series, DataFrames & Indexing",
        "Pandas Data Ingestion (CSV, Excel, SQL)", "Handling Missing Values & Outliers in Pandas", "Data Transformation & Lambda Functions",
        "Merging, Joining & Concatenating Datasets", "Matplotlib & Seaborn Visualizations", "Exploratory Data Analysis (EDA) Workflows",
        "Power BI Interface, Architecture & Setup", "Connecting Power BI to Diverse Data Sources", "Power Query ETL & Data Modeling",
        "Star Schema vs Snowflake Schema Design", "DAX Calculated Columns vs DAX Measures", "Time Intelligence Functions in DAX",
        "Building Interactive KPI Cards & Matrix Reports", "Drill-Through, Tooltips & Bookmarks in Power BI", "Descriptive Statistics (Mean, Median, StdDev)",
        "Variance, Correlation & Covariance Analysis", "Statistical Hypothesis Testing & KPIs", "Capstone Problem Formulation & Data Audit",
        "Data Cleaning & Feature Engineering", "Power BI Executive Dashboard Finalization", "Capstone Report Documentation & Presentation"
    ]

    dm_topics = [
        "Digital Marketing Fundamentals & Ecosystem", "Digital Channels Overview & Touchpoint Mapping", "Customer Journey & Funnel (TOFU, MOFU, BOFU)",
        "Search Engine Crawling, Indexing & Algorithms", "Keyword Research & Search Intent Mapping", "On-Page SEO: Meta Tags, Headings, Content",
        "Off-Page SEO, Domain Authority & Backlinks", "Technical SEO: Sitemaps, Robots.txt & Speed", "Local SEO & Google Business Profile Optimization",
        "Comprehensive Website SEO Audit & Roadmap", "Social Media Strategy: Instagram, Facebook, LinkedIn", "Content Strategy Themes & Content Buckets",
        "Social Media Editorial Calendar Design", "Social Media Engagement & Community Growth", "Persuasive Copywriting: AIDA & PAS Frameworks",
        "Blogging, Pillar Posts & Content Distribution", "Creative Visual Content Design & Carousel Briefs", "AI Tools in Content Workflows & Prompting",
        "Google Ads Architecture & Account Hierarchy", "Search Ad Campaigns, Match Types & Quality Score", "Display Advertising & Remarketing Audiences",
        "Negative Keywords & Cost-Per-Click Optimization", "Search Ad Copywriting & Asset Extensions", "Email Marketing Fundamentals & List Hygiene",
        "Automated Email Sequences & Drip Campaigns", "Audience Segmentation & Email Personalization", "Web Analytics (GA4) Architecture & Data Streams",
        "Traffic Sources & Acquisition Channels Analysis", "Conversion Event Tracking & Funnel Exploration", "UTM Tagging Conventions & Campaign Measurement",
        "Performance Marketing Metrics: CPC, CPM, CTR, ROAS", "Customer Acquisition Cost (CAC) & Unit Economics", "Meta Ads Campaign Mockup & Creative Variations",
        "A/B Testing Methodologies for Paid Campaigns", "Capstone Campaign Blueprint & Budget Allocation", "Digital Marketing Strategy Dossier Finalization"
    ]

    topics_list = da_topics if track == "DA" else dm_topics
    tools_label = "Python / SQL / Power BI / Excel" if track == "DA" else "Meta Ads / GA4 / SEO Tools / Canva"

    while day_count < 36:
        if current_dt.weekday() != 6:  # Skip Sundays
            date_str = current_dt.strftime("%Y-%m-%d")
            day_name = current_dt.strftime("%A")
            is_leave = day_count in leave_set

            if is_leave:
                cursor.execute("""
                INSERT INTO attendance (internship_id, date, day_of_week, start_time, end_time, total_hours, topic_covered, status, student_signed, mentor_signed, remarks)
                VALUES (?, ?, ?, '10:00 AM', '01:30 PM', 0.0, ?, 'AUTHORIZED LEAVE', 1, 1, 'Approved College/Medical Leave')
                """, (internship_id, date_str, day_name, f"Module Session {day_count + 1} (Approved Leave)"))
            else:
                total_hours += 3.5
                present_count += 1
                topic = topics_list[day_count] if day_count < len(topics_list) else f"Practical Implementation {day_count + 1}"
                cursor.execute("""
                INSERT INTO attendance (internship_id, date, day_of_week, start_time, end_time, total_hours, topic_covered, status, student_signed, mentor_signed)
                VALUES (?, ?, ?, '10:00 AM', '01:30 PM', 3.5, ?, 'PRESENT', 1, 1)
                """, (internship_id, date_str, day_name, topic))

                cursor.execute("""
                INSERT INTO daily_logs (internship_id, date, day_of_week, module_name, topic, work_performed, practical_activity, tools_used, learning_outcome, hours, mentor_remarks, student_signed, mentor_signed)
                VALUES (?, ?, ?, 'Core Curriculum Track', ?, 'Completed structured exercises and hands-on laboratory implementation.', 'Executed practical lab assignments and data exercises.', ?, 'Attained verified technical competency and applied problem solving.', 3.5, 'Satisfactory progress and active participation demonstrated.', 1, 1)
                """, (internship_id, date_str, day_name, topic, tools_label))

            day_count += 1
        current_dt += timedelta(days=1)

    # 7. 6 Weekly Reports
    for w in range(1, 7):
        cursor.execute("""
        INSERT INTO weekly_reports (internship_id, week_number, start_date, end_date, topics_covered, practical_work, project_progress, skills_learned, hours_completed, mentor_remarks, student_signed, mentor_signed)
        VALUES (?, ?, ?, ?, 'Structured Curriculum & Practical Review', 'Hands-on laboratory implementation', 'Milestone deliverables submitted and verified', 'Technical competencies mastered according to syllabus', 21.0, 'Consistent progress and disciplined execution shown.', 1, 1)
        """, (internship_id, w, f"2026-06-0{w}" if w < 10 else f"2026-06-{w}", f"2026-06-{w+5}"))

    # 8. Capstone Project
    da_title = req.custom_project_title or "Retail Sales Performance & Customer Churn Analytics Dashboard"
    dm_title = req.custom_project_title or "Omnichannel Lead Generation & SEO Growth Campaign for Local Healthcare Clinic"
    proj_title = da_title if track == "DA" else dm_title

    if track == "DA":
        proj_data = {
            "project_title": proj_title,
            "problem_statement": "An omnichannel retail chain operating across North India faced a 14% year-over-year dip in customer repeat purchase rate. The management lacked a consolidated real-time dashboard to track store performance and customer churn.",
            "dataset": "Relational retail database comprising 65,000+ orders, 12,000 customer profiles, and 3 years of transactional records.",
            "tools": "Microsoft Excel 365, PostgreSQL, Python (Pandas, NumPy), Power BI Desktop, DAX.",
            "objectives": "1. Build automated data ingestion pipeline.\n2. Design Star Schema in Power BI.\n3. Segment churn risk via RFM analysis.\n4. Deliver executive dashboards.",
            "findings": "Top 20% loyal customers drove 64% of total revenue. Customers inactive for 45 days had 82% churn likelihood.",
            "recommendations": "Deploy automated Day-30 SMS/Email re-engagement triggers to recover estimated Rs. 42 Lakhs annually.",
            "conclusion": "Delivered robust BI solution reducing reporting turnaround from 5 days to real-time."
        }
    else:
        proj_data = {
            "project_title": proj_title,
            "brand_business": "Aarogyam Multi-Speciality Clinic & Diagnostic Centre, Bharatpur",
            "campaign_objective": "Increase verified patient appointment bookings by 40% in 90 days and dominate local search results.",
            "target_audience": "Families, working professionals, and seniors aged 25–60 in Bharatpur district.",
            "seo_strategy": "Verified Google Business Profile and built 45 consistent local NAP citations across directories.",
            "content_strategy": "Weekly doctor-vetted social carousels and preventative health guides.",
            "advertising_strategy": "Google Search Ads targeting high-intent medical queries paired with geo-fenced Meta awareness ads.",
            "kpis": "Target CPL < Rs. 180, Search Ad CTR > 5.5%, Local 3-Pack ranking for 8 primary keywords.",
            "results": "Simulated media plan projects 220 monthly inquiries at a blended CPL of Rs. 142, yielding 4.8x ROAS.",
            "recommendations": "Implement automated WhatsApp appointment confirmations to eliminate no-shows.",
            "conclusion": "Commercial digital growth roadmap perfectly tailored for regional healthcare businesses."
        }

    cursor.execute("""
    INSERT INTO projects (internship_id, project_title, project_type, project_description, objectives, fields_json, status, submitted_at, approved_at)
    VALUES (?, ?, 'Capstone Project', ?, ?, ?, 'APPROVED', '2026-07-11 16:00:00', '2026-07-12 11:00:00')
    """, (internship_id, proj_title, proj_data.get("problem_statement", proj_data.get("brand_business", "")), proj_data.get("objectives", proj_data.get("campaign_objective", "")), json.dumps(proj_data)))

    # 9. Mentor Evaluation Rubric
    total_eval = req.evaluation_score
    criteria_scores = {
        "attendance_discipline": {"score": 11, "max": 11, "rating": "Exemplary"},
        "technical_knowledge": {"score": 11, "max": 11, "rating": "Exemplary"},
        "practical_skills": {"score": 11, "max": 11, "rating": "Exemplary"},
        "communication": {"score": 10, "max": 10, "rating": "Excellent"},
        "teamwork": {"score": 10, "max": 10, "rating": "Excellent"},
        "problem_solving": {"score": 11, "max": 11, "rating": "Exemplary"},
        "project_work": {"score": 11, "max": 11, "rating": "Exemplary"},
        "professional_behaviour": {"score": 10, "max": 10, "rating": "Excellent"},
        "learning_ability": {"score": 10, "max": 10, "rating": "Excellent"}
    }
    cursor.execute("""
    INSERT INTO evaluations (internship_id, mentor_id, criteria_scores_json, overall_score, final_remark, evaluated_at, mentor_signed)
    VALUES (?, ?, ?, ?, ?, '2026-07-12 15:00:00', 1)
    """, (internship_id, mentor_id, json.dumps(criteria_scores), total_eval, req.mentor_remarks))

    # 10. Finalize & Lock Certificate
    cursor.execute("SELECT COUNT(*) FROM certificates")
    seq = cursor.fetchone()[0] + 1
    year = datetime.now().year
    cert_num = f"{s['cert_prefix']}-{track}-{year}-{seq:04d}"
    ver_code = f"VER-{s['cert_prefix']}-{track}-{datetime.now().strftime('%m%d')}{seq:03d}"
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    import urllib.parse
    base_url = s.get("verification_base_url") or "http://192.168.0.103:8000"
    base_url = base_url.rstrip("/")
    params = urllib.parse.urlencode({
        "cert": cert_num,
        "name": req.full_name.strip(),
        "course": course['name'],
        "sem": f"{deg_text} ({sem_text})",
        "college": req.college_name,
        "ver_id": ver_code,
        "date": now_str[:10]
    })
    qr_payload_json = f"{base_url}/verify?{params}"

    cursor.execute("""
    UPDATE internships
    SET certificate_number = ?, verification_code = ?, qr_payload_json = ?, status = 'CERTIFIED', is_locked = 1, finalized_at = ?, total_training_hours = ?
    WHERE id = ?
    """, (cert_num, ver_code, qr_payload_json, now_str, total_hours, internship_id))

    cursor.execute("""
    INSERT INTO certificates (internship_id, cert_type, certificate_number, verification_code, qr_payload_json, issue_date, is_finalized, finalized_by)
    VALUES (?, 'COMPLETION', ?, ?, ?, ?, 1, ?)
    """, (internship_id, cert_num, ver_code, qr_payload_json, now_str[:10], s["signatory_name"]))

    conn.commit()
    conn.close()

    log_audit("WIZARD_GENERATE", "INTERNSHIP", internship_id, {
        "student": req.full_name,
        "certificate_number": cert_num,
        "course": track
    })

    # Pre-generate complete package ZIP
    try:
        pdf_service.generate_complete_package_zip(internship_id)
    except Exception as e:
        print(f"Warning: could not pre-generate ZIP: {e}")

    return {
        "success": True,
        "student_id": student_id,
        "internship_id": internship_id,
        "student_name": req.full_name.strip(),
        "course_name": course["name"],
        "certificate_number": cert_num,
        "verification_code": ver_code,
        "qr_payload": qr_payload_json,
        "attendance_pct": round(present_count / 36 * 100, 1),
        "total_hours": total_hours,
        "zip_url": f"/api/documents/{internship_id}/package-zip",
        "cert_pdf_url": f"/api/documents/{internship_id}/certificate/pdf",
        "report_pdf_url": f"/api/documents/{internship_id}/consolidated/pdf"
    }

# -------------------------------------------------------------
# 15. Centre Settings & Asset Uploads
# -------------------------------------------------------------
class SettingsUpdate(BaseModel):
    org_name: str
    centre_name: str
    centre_code: str
    address: str
    phone: str
    email: str
    website: str
    auth_ref: Optional[str] = ""
    signatory_name: str
    signatory_designation: str
    show_digital_signature: int = 0
    show_digital_stamp: int = 0
    cert_prefix: str = "TG-BPT"
    doc_prefix: str = "TG/BPT"
    verification_base_url: Optional[str] = "http://192.168.0.103:8000"

@app.get("/api/settings")
def get_settings():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM centre_settings WHERE id = 1")
    s = dict(cursor.fetchone())
    conn.close()
    return s

@app.put("/api/settings")
def update_settings(req: SettingsUpdate):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE centre_settings
    SET org_name = ?, centre_name = ?, centre_code = ?, address = ?, phone = ?, email = ?,
        website = ?, auth_ref = ?, signatory_name = ?, signatory_designation = ?,
        show_digital_signature = ?, show_digital_stamp = ?, cert_prefix = ?, doc_prefix = ?,
        verification_base_url = ?, updated_at = CURRENT_TIMESTAMP
    WHERE id = 1
    """, (
        req.org_name, req.centre_name, req.centre_code, req.address, req.phone, req.email,
        req.website, req.auth_ref, req.signatory_name, req.signatory_designation,
        req.show_digital_signature, req.show_digital_stamp, req.cert_prefix, req.doc_prefix,
        req.verification_base_url or "http://192.168.0.103:8000"
    ))
    conn.commit()
    conn.close()
    log_audit("SETTINGS_UPDATED", "CENTRE_SETTINGS", 1, {"centre_name": req.centre_name})
    return {"success": True}

@app.post("/api/settings/upload-asset")
async def upload_asset(asset_type: str = Form(...), file: UploadFile = File(...)):
    filename = f"{asset_type}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    with open(filepath, "wb") as f:
        content = await file.read()
        f.write(content)

    url_path = f"/uploads/{filename}"
    conn = get_db()
    cursor = conn.cursor()
    field_map = {
        "logo": "logo_url",
        "signature": "signature_url",
        "stamp": "stamp_url"
    }
    if asset_type in field_map:
        cursor.execute(f"UPDATE centre_settings SET {field_map[asset_type]} = ? WHERE id = 1", (url_path,))
        conn.commit()
    conn.close()

    return {"success": True, "url": url_path}

# -------------------------------------------------------------
# 16. Audit Logs
# -------------------------------------------------------------
@app.get("/api/audit-logs")
def get_audit_logs():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM audit_logs ORDER BY id DESC LIMIT 50")
    logs = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return logs

# -------------------------------------------------------------
# 17. Frontend SPA Static Serving
# -------------------------------------------------------------
CLIENT_DIST = os.path.join(os.path.dirname(os.path.dirname(__file__)), "client", "dist")
if os.path.exists(CLIENT_DIST):
    app.mount("/assets", StaticFiles(directory=os.path.join(CLIENT_DIST, "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # Allow /api and /uploads to bypass
        if full_path.startswith("api/") or full_path.startswith("uploads/"):
            raise HTTPException(status_code=404, detail="Not found")
        file_path = os.path.join(CLIENT_DIST, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        index_file = os.path.join(CLIENT_DIST, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        return JSONResponse({"detail": "Frontend not found"}, status_code=404)

if __name__ == "__main__":
    import uvicorn
    init_db()
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

