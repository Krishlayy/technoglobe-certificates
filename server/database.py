import sqlite3
import os
import json
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "technoglobe.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # 1. Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'CENTRE_ADMIN', -- SUPER_ADMIN, CENTRE_ADMIN, MENTOR, VIEWER
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 2. Centre Settings
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS centre_settings (
        id INTEGER PRIMARY KEY CHECK (id = 1),
        org_name TEXT NOT NULL,
        centre_name TEXT NOT NULL,
        centre_code TEXT NOT NULL,
        default_college TEXT NOT NULL DEFAULT 'Poddar College, Bharatpur',
        address TEXT NOT NULL,
        phone TEXT NOT NULL,
        email TEXT NOT NULL,
        website TEXT NOT NULL,
        auth_ref TEXT,
        signatory_name TEXT NOT NULL,
        signatory_designation TEXT NOT NULL,
        logo_url TEXT,
        signature_url TEXT,
        stamp_url TEXT,
        show_digital_signature INTEGER DEFAULT 0,
        show_digital_stamp INTEGER DEFAULT 0,
        cert_prefix TEXT DEFAULT 'TG-BPT',
        doc_prefix TEXT DEFAULT 'TG/BPT',
        default_required_hours INTEGER DEFAULT 120,
        default_required_attendance_pct REAL DEFAULT 75.0,
        verification_base_url TEXT DEFAULT 'http://192.168.0.103:8000',
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 3. Courses
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS courses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE NOT NULL, -- DA, DM, etc.
        name TEXT NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        duration_weeks INTEGER NOT NULL DEFAULT 6,
        total_hours INTEGER NOT NULL DEFAULT 120,
        default_mode TEXT NOT NULL DEFAULT 'Offline', -- Offline, Online, Hybrid
        is_active INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 4. Course Modules
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS course_modules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_id INTEGER NOT NULL,
        module_number INTEGER NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        topics_json TEXT NOT NULL DEFAULT '[]',
        practical_activities_json TEXT NOT NULL DEFAULT '[]',
        learning_outcomes_json TEXT NOT NULL DEFAULT '[]',
        hours INTEGER NOT NULL DEFAULT 12,
        FOREIGN KEY (course_id) REFERENCES courses (id) ON DELETE CASCADE
    );
    """)

    # 5. Mentors
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS mentors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        designation TEXT NOT NULL,
        email TEXT,
        phone TEXT,
        bio TEXT,
        is_active INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 6. Batches
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS batches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_id INTEGER NOT NULL,
        batch_code TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        start_date TEXT NOT NULL,
        end_date TEXT NOT NULL,
        mentor_id INTEGER,
        max_students INTEGER DEFAULT 30,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (course_id) REFERENCES courses (id) ON DELETE RESTRICT,
        FOREIGN KEY (mentor_id) REFERENCES mentors (id) ON DELETE SET NULL
    );
    """)

    # 7. Students (SIMPLIFIED: PRN and Roll Number completely removed; College is Poddar College, Bharatpur)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        father_mother_name TEXT,
        dob TEXT,
        gender TEXT DEFAULT 'Male',
        mobile TEXT,
        email TEXT,
        address TEXT,
        city TEXT DEFAULT 'Bharatpur',
        state TEXT DEFAULT 'Rajasthan',
        college_name TEXT NOT NULL DEFAULT 'Poddar College, Bharatpur',
        degree TEXT NOT NULL,
        branch TEXT NOT NULL,
        semester_year TEXT DEFAULT '6th Semester',
        academic_session TEXT DEFAULT '2025-2026',
        is_demo INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 8. Internships
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS internships (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        course_id INTEGER NOT NULL,
        batch_id INTEGER,
        mentor_id INTEGER NOT NULL,
        internship_title TEXT NOT NULL,
        internship_type TEXT NOT NULL DEFAULT 'Course-Based Internship',
        start_date TEXT NOT NULL,
        end_date TEXT NOT NULL,
        total_days INTEGER NOT NULL DEFAULT 36,
        total_training_hours INTEGER NOT NULL DEFAULT 120,
        mode TEXT NOT NULL DEFAULT 'Offline', -- Offline, Online, Hybrid
        status TEXT NOT NULL DEFAULT 'REGISTERED', -- REGISTERED, TRAINING, PROJECT_SUBMITTED, EVALUATED, COMPLETED, CERTIFIED
        certificate_number TEXT UNIQUE,
        verification_code TEXT UNIQUE,
        qr_payload_json TEXT,
        is_locked INTEGER DEFAULT 0,
        finalized_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (student_id) REFERENCES students (id) ON DELETE CASCADE,
        FOREIGN KEY (course_id) REFERENCES courses (id) ON DELETE RESTRICT,
        FOREIGN KEY (batch_id) REFERENCES batches (id) ON DELETE SET NULL,
        FOREIGN KEY (mentor_id) REFERENCES mentors (id) ON DELETE RESTRICT
    );
    """)

    # 9. University / College Compliance Records (Internal Only)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS compliance_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        internship_id INTEGER UNIQUE NOT NULL,
        university_name TEXT DEFAULT 'Poddar College, Bharatpur',
        department TEXT,
        affiliation_ref TEXT,
        faculty_coordinator TEXT,
        faculty_designation TEXT,
        approval_status TEXT NOT NULL DEFAULT 'APPROVED', -- PENDING, APPROVED, NOT_REQUIRED, REJECTED
        approval_ref TEXT,
        approval_date TEXT,
        noc_document_url TEXT,
        approval_letter_url TEXT,
        mou_doc_url TEXT,
        supporting_doc_url TEXT,
        required_duration TEXT DEFAULT '6 Weeks',
        required_hours INTEGER DEFAULT 120,
        required_attendance_pct REAL DEFAULT 75.0,
        checklist_json TEXT DEFAULT '{}',
        notes TEXT,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (internship_id) REFERENCES internships (id) ON DELETE CASCADE
    );
    """)

    # 10. Attendance
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        internship_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        day_of_week TEXT NOT NULL,
        start_time TEXT NOT NULL DEFAULT '10:00 AM',
        end_time TEXT NOT NULL DEFAULT '01:30 PM',
        total_hours REAL NOT NULL DEFAULT 3.5,
        topic_covered TEXT,
        status TEXT NOT NULL DEFAULT 'PRESENT', -- PRESENT, ABSENT, AUTHORIZED LEAVE, HOLIDAY, WEEK OFF
        student_signed INTEGER DEFAULT 1,
        mentor_signed INTEGER DEFAULT 1,
        remarks TEXT,
        FOREIGN KEY (internship_id) REFERENCES internships (id) ON DELETE CASCADE,
        UNIQUE(internship_id, date)
    );
    """)

    # 11. Daily Logs / Logbook
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS daily_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        internship_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        day_of_week TEXT NOT NULL,
        module_name TEXT NOT NULL,
        topic TEXT NOT NULL,
        work_performed TEXT NOT NULL,
        practical_activity TEXT NOT NULL,
        tools_used TEXT NOT NULL,
        learning_outcome TEXT NOT NULL,
        hours REAL NOT NULL DEFAULT 3.5,
        mentor_remarks TEXT,
        student_signed INTEGER DEFAULT 1,
        mentor_signed INTEGER DEFAULT 1,
        FOREIGN KEY (internship_id) REFERENCES internships (id) ON DELETE CASCADE,
        UNIQUE(internship_id, date)
    );
    """)

    # 12. Weekly Reports
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS weekly_reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        internship_id INTEGER NOT NULL,
        week_number INTEGER NOT NULL,
        start_date TEXT NOT NULL,
        end_date TEXT NOT NULL,
        topics_covered TEXT NOT NULL,
        practical_work TEXT NOT NULL,
        project_progress TEXT NOT NULL,
        skills_learned TEXT NOT NULL,
        hours_completed REAL NOT NULL DEFAULT 21.0,
        mentor_remarks TEXT,
        student_signed INTEGER DEFAULT 1,
        mentor_signed INTEGER DEFAULT 1,
        FOREIGN KEY (internship_id) REFERENCES internships (id) ON DELETE CASCADE,
        UNIQUE(internship_id, week_number)
    );
    """)

    # 13. Projects
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        internship_id INTEGER UNIQUE NOT NULL,
        project_title TEXT NOT NULL,
        project_type TEXT DEFAULT 'Capstone Project',
        project_description TEXT,
        objectives TEXT,
        fields_json TEXT NOT NULL DEFAULT '{}',
        file_attachments_json TEXT NOT NULL DEFAULT '[]',
        status TEXT NOT NULL DEFAULT 'IN_PROGRESS', -- IN_PROGRESS, SUBMITTED, APPROVED
        submitted_at TIMESTAMP,
        approved_at TIMESTAMP,
        FOREIGN KEY (internship_id) REFERENCES internships (id) ON DELETE CASCADE
    );
    """)

    # 14. Mentor Evaluations
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS evaluations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        internship_id INTEGER UNIQUE NOT NULL,
        mentor_id INTEGER NOT NULL,
        criteria_scores_json TEXT NOT NULL DEFAULT '{}',
        overall_score INTEGER NOT NULL DEFAULT 0, -- out of 100
        final_remark TEXT,
        evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        mentor_signed INTEGER DEFAULT 1,
        FOREIGN KEY (internship_id) REFERENCES internships (id) ON DELETE CASCADE,
        FOREIGN KEY (mentor_id) REFERENCES mentors (id) ON DELETE RESTRICT
    );
    """)

    # 15. Student Feedback
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        internship_id INTEGER UNIQUE NOT NULL,
        course_quality INTEGER DEFAULT 5,
        practical_training INTEGER DEFAULT 5,
        mentor_support INTEGER DEFAULT 5,
        learning_resources INTEGER DEFAULT 5,
        project_experience INTEGER DEFAULT 5,
        overall_rating INTEGER DEFAULT 5,
        comments TEXT,
        submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (internship_id) REFERENCES internships (id) ON DELETE CASCADE
    );
    """)

    # 16. Certificates (Internal Registry)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS certificates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        internship_id INTEGER NOT NULL,
        cert_type TEXT NOT NULL DEFAULT 'COMPLETION', -- COMPLETION, EXPERIENCE
        certificate_number TEXT UNIQUE NOT NULL,
        verification_code TEXT UNIQUE NOT NULL,
        qr_payload_json TEXT NOT NULL DEFAULT '{}',
        issue_date TEXT NOT NULL,
        is_finalized INTEGER DEFAULT 1,
        finalized_by TEXT,
        version INTEGER DEFAULT 1,
        pdf_path TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (internship_id) REFERENCES internships (id) ON DELETE CASCADE
    );
    """)

    # 17. Document Templates (Visual Block Customizer)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS document_templates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        template_key TEXT UNIQUE NOT NULL,
        title TEXT NOT NULL,
        blocks_json TEXT NOT NULL DEFAULT '[]',
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 18. Audit Logs
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        user_name TEXT,
        action TEXT NOT NULL,
        entity_type TEXT NOT NULL,
        entity_id INTEGER,
        details_json TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Performance indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_internships_student_id ON internships(student_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_internships_course_id ON internships(course_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_internships_mentor_id ON internships(mentor_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_internships_status ON internships(status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_certificates_internship_id ON certificates(internship_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_course_modules_course_id ON course_modules(course_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_attendance_internship_id ON attendance(internship_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_daily_logs_internship_id ON daily_logs(internship_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_students_email ON students(email)")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database schema updated successfully!")
