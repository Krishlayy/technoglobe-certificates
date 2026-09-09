import sqlite3
import json
import hashlib
from datetime import datetime, timedelta
from database import get_db, init_db

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def normalize_text(text: str) -> str:
    if not text:
        return ""
    # Remove accidental repeated tokens
    import re
    cleaned = re.sub(r'Course-Based IInternshipnternship', 'Course-Based Internship', text)
    cleaned = re.sub(r'Internship\s+Internship', 'Internship', cleaned)
    cleaned = re.sub(r'B\.TechBCA', 'BCA', cleaned)
    cleaned = re.sub(r'120120 Hours', '120 Hours', cleaned)
    cleaned = re.sub(r'None training hours', '120 Training Hours', cleaned)
    return ' '.join(cleaned.split())

def _seed_base_data(cursor, conn):
    print("Seeding TechnoGlobe Bharatpur Centre Base Config & Courses...")

    # 1. Users
    users = [
        ("Centre Administrator", "admin@technoglobe.co.in", hash_password("admin123"), "CENTRE_ADMIN"),
        ("System Super Admin", "superadmin@technoglobe.co.in", hash_password("super123"), "SUPER_ADMIN"),
        ("Er. Vikas Agrawal (Mentor)", "vikas@technoglobe.co.in", hash_password("mentor123"), "MENTOR"),
        ("Staff Viewer", "viewer@technoglobe.co.in", hash_password("viewer123"), "VIEWER"),
        ("Nitin (Faculty Admin)", "nitin@pctm", hash_password("nitin321"), "SUPER_ADMIN"),
    ]
    cursor.executemany("INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?)", users)

    # 2. Centre Settings
    cursor.execute("""
    INSERT INTO centre_settings (
        id, org_name, centre_name, centre_code, default_college, address, phone, email, website, auth_ref,
        signatory_name, signatory_designation, logo_url, signature_url, stamp_url,
        show_digital_signature, show_digital_stamp, cert_prefix, doc_prefix,
        default_required_hours, default_required_attendance_pct
    ) VALUES (
        1,
        'TECHNOGLOBE IT SOLUTIONS PVT. LTD.',
        'TECHNOGLOBE – BHARATPUR CENTRE',
        'BPT-01',
        'Poddar College, Bharatpur',
        'Poddar College, Bharatpur, Near SP Office, Bharatpur, Rajasthan, India',
        '+91 98290 12345',
        'bharatpur@technoglobe.co.in',
        'https://www.technoglobe.co.in',
        'TG/FRAN/RAJ/BPT/2024-001',
        'Er. Rajesh Sharma',
        'Centre Director & Authorized Signatory',
        '', '', '',
        0, 0,
        'TG-BPT', 'TG/BPT',
        120, 75.0
    );
    """)

    # 3. Courses
    courses = [
        ('DA', 'Data Analytics', 'Course-Based Internship in Data Analytics & Business Intelligence',
         'Industry-aligned comprehensive internship covering Excel, SQL, Python, Power BI, Statistics and Capstone Analytics.',
         6, 120, 'Offline'),
        ('DM', 'Digital Marketing', 'Course-Based Internship in Digital Marketing & Growth Strategies',
         'Practical marketing program covering SEO, SMM, Google Ads, Content Marketing, Analytics, Performance Marketing and AI tools.',
         6, 120, 'Offline')
    ]
    cursor.executemany("""
    INSERT INTO courses (code, name, title, description, duration_weeks, total_hours, default_mode)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, courses)

    da_course_id = 1
    dm_course_id = 2

    # 4. Modules for Data Analytics (9 Modules as specified in Master Prompt)
    da_modules = [
        (da_course_id, 1, "Introduction to Data Analytics",
         "Data analytics fundamentals, types of data, analytics lifecycle, business problems and analytical thinking.",
         json.dumps(["Data Analytics Fundamentals", "Types of Data (Structured vs Unstructured)", "Data Analytics Lifecycle", "Business Problems & Analytical Thinking", "Metrics & KPIs"]),
         json.dumps(["Case study evaluation on real-world retail problems", "Mapping business questions to data metrics"]),
         json.dumps(["Understand analytics workflow", "Formulate clear business questions"]), 12),

        (da_course_id, 2, "Microsoft Excel",
         "Spreadsheet data cleaning, formatting, formulas, functions, lookup functions, pivot tables, dynamic dashboards, data validation, what-if analysis.",
         json.dumps(["Data Cleaning & Formatting", "Formulas & Mathematical Functions", "Lookup Functions (XLOOKUP, VLOOKUP, INDEX-MATCH)", "Pivot Tables & Pivot Charts", "Interactive Dashboards", "Data Validation & What-If Analysis"]),
         json.dumps(["Building a dynamic sales tracker in Excel", "Automated executive summary dashboard"]),
         json.dumps(["Proficiency in advanced Excel functions", "Create interactive business dashboards"]), 14),

        (da_course_id, 3, "SQL",
         "Database fundamentals, tables and relationships, SELECT, WHERE, GROUP BY, ORDER BY, JOINs, aggregations, subqueries, CTEs, practical SQL exercises.",
         json.dumps(["Database Architecture & RDBMS", "SELECT, WHERE, ORDER BY, GROUP BY", "JOINs (INNER, LEFT, RIGHT, FULL)", "Aggregations & HAVING", "Subqueries & Common Table Expressions (CTEs)", "Practical SQL Exercises"]),
         json.dumps(["Writing SQL queries on multi-table e-commerce database", "Customer RFM segmentation in SQL"]),
         json.dumps(["Design and query relational schemas", "Extract business insights using SQL"]), 16),

        (da_course_id, 4, "Python for Data Analytics",
         "Python fundamentals, variables and data types, lists, tuples, sets, dictionaries, functions, NumPy, Pandas, data exploration.",
         json.dumps(["Python Fundamentals & Syntax", "Variables, Data Types, Collections", "Functions & Functional Logic", "NumPy Arrays & Mathematical Operations", "Pandas DataFrames & Series", "Exploratory Data Analysis"]),
         json.dumps(["Exploratory data analysis of 50,000+ transaction rows", "Automated data transformation pipeline"]),
         json.dumps(["Clean and reshape raw data with Pandas", "Execute thorough exploratory data analysis"]), 18),

        (da_course_id, 5, "Data Cleaning & Transformation",
         "Advanced data wrangling, missing data imputation, anomaly detection, categorical encoding, and feature transformation.",
         json.dumps(["Missing Value Imputation Strategies", "Outlier Detection & Capping", "Data Type Conversions & Date Parsing", "Feature Encoding & Scaling", "Data Quality Auditing"]),
         json.dumps(["Cleaning real messy multi-source datasets", "Building reusable data sanitization functions"]),
         json.dumps(["Clean and transform messy data reliably", "Ensure statistical integrity of sanitized datasets"]), 12),

        (da_course_id, 6, "Data Visualization",
         "Visualization principles, chart selection, dashboard design, business storytelling with data.",
         json.dumps(["Visualization Principles & Visual Perception", "Chart Selection Matrix", "Color Theory & Aesthetic Layouts", "Dashboard Design Thinking", "Business Storytelling with Data"]),
         json.dumps(["Creating publication-ready charts", "Visual audit of cluttered charts and redesigning"]),
         json.dumps(["Apply professional data visualization standards", "Communicate insights persuasively to leadership"]), 10),

        (da_course_id, 7, "Power BI",
         "Data import, Power Query, data transformation, data modeling, relationships, DAX fundamentals, measures, KPIs, interactive dashboards, publishing/exporting reports.",
         json.dumps(["Data Import & Power Query ETL", "Data Transformation", "Data Modeling & Relationships", "DAX Fundamentals & Calculated Columns", "Key Performance Indicators (KPIs)", "Interactive Dashboards & Publishing"]),
         json.dumps(["End-to-end interactive Power BI dashboard with drill-through", "Custom KPI card suite with DAX"]),
         json.dumps(["Build end-to-end Power BI solutions", "Write core DAX business metrics"]), 18),

        (da_course_id, 8, "Statistics & Business Intelligence",
         "Descriptive statistics, mean, median, mode, variance, standard deviation, correlation, business KPIs.",
         json.dumps(["Descriptive Statistics (Mean, Median, Mode)", "Variance & Standard Deviation", "Correlation vs Causation", "Normal Distribution & Outliers", "Enterprise Business KPIs"]),
         json.dumps(["Statistical hypothesis testing on promotional data", "Outlier detection and resolution"]),
         json.dumps(["Apply statistical thinking to business metrics", "Interpret variance and correlation safely"]), 10),

        (da_course_id, 9, "Capstone Project",
         "Student creates a real analytical project using an industry dataset.",
         json.dumps(["Problem Formulation & Dataset Acquisition", "Data Cleaning & Preparation", "SQL Querying & Python Transformation", "Power BI Interactive Dashboard", "Executive Findings & Actionable Recommendations"]),
         json.dumps(["Complete end-to-end Capstone Project Report and presentation"]),
         json.dumps(["Deliver complete industry-standard analytical portfolio project"]), 10)
    ]
    cursor.executemany("""
    INSERT INTO course_modules (course_id, module_number, title, description, topics_json, practical_activities_json, learning_outcomes_json, hours)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, da_modules)

    # 5. Modules for Digital Marketing (10 Modules as specified in Master Prompt)
    dm_modules = [
        (dm_course_id, 1, "Introduction to Digital Marketing",
         "Digital marketing fundamentals, digital channels, customer journey, marketing funnel.",
         json.dumps(["Digital Marketing Fundamentals", "Digital Channels Overview", "Customer Journey & Touchpoints", "Marketing Funnel (TOFU, MOFU, BOFU)"]),
         json.dumps(["Digital presence audit of a regional business", "Mapping omnichannel customer touchpoints"]),
         json.dumps(["Understand digital ecosystem dynamics", "Map customer purchase journeys"]), 10),

        (dm_course_id, 2, "SEO",
         "Search engines, keyword research, on-page SEO, off-page SEO, technical SEO, local SEO, SEO audit.",
         json.dumps(["Search Engine Crawling & Indexing", "Keyword Research & Search Intent", "On-Page SEO (Meta tags, headings, content)", "Off-Page SEO & Backlinks", "Technical SEO (Sitemaps, robots.txt)", "Local SEO & Google Business Profile", "SEO Audit"]),
         json.dumps(["Keyword research sheet for a regional service business", "Live SEO audit of website"]),
         json.dumps(["Execute full on-page and local SEO audit", "Optimize content for organic search ranking"]), 16),

        (dm_course_id, 3, "Social Media Marketing",
         "Instagram, Facebook, LinkedIn, YouTube, content strategy, social media calendar, engagement.",
         json.dumps(["Platform Strategies (Instagram, Facebook, LinkedIn, YouTube)", "Content Strategy & Themes", "Social Media Calendar Creation", "Engagement & Growth Tactics"]),
         json.dumps(["30-day multi-platform social media calendar", "Creation of engaging carousel and video briefs"]),
         json.dumps(["Design cohesive social media calendar", "Drive organic engagement"]), 14),

        (dm_course_id, 4, "Content Marketing",
         "Content strategy, copywriting, blogging, creative content, AI-assisted content workflows.",
         json.dumps(["Content Strategy Framework", "Persuasive Copywriting (AIDA, PAS)", "Blogging & Editorial Workflows", "Creative Visual Content", "AI-Assisted Content Workflows"]),
         json.dumps(["Writing landing page copy using AIDA framework", "Publishing an SEO-optimized pillar blog post"]),
         json.dumps(["Draft persuasive marketing copy", "Create multi-format content strategies"]), 12),

        (dm_course_id, 5, "Google Ads / Paid Advertising",
         "Campaign structure, search campaigns, display advertising, targeting, keywords, ad copy, budgeting, campaign analysis.",
         json.dumps(["Campaign Structure & Account Architecture", "Search Campaigns & Match Types", "Display Advertising & Remarketing", "Audience Targeting", "Keywords & Negative Keywords", "Ad Copywriting & Extensions", "Budgeting & Campaign Analysis"]),
         json.dumps(["Designing a complete Google Search Ads campaign structure", "Ad copy A/B test variations"]),
         json.dumps(["Set up search ad campaigns with positive ROI", "Optimize quality score and CPC"]), 16),

        (dm_course_id, 6, "Email Marketing",
         "Email campaigns, lists, segmentation, subject lines, campaign performance.",
         json.dumps(["Email Marketing Fundamentals", "Email Campaigns & Automation", "List Building & Hygiene", "Audience Segmentation", "Subject Lines & Deliverability", "Campaign Performance Metrics"]),
         json.dumps(["Designing an automated email nurture sequence", "Email template design and copywriting"]),
         json.dumps(["Build automated email marketing funnels", "Improve deliverability and engagement"]), 10),

        (dm_course_id, 7, "Web Analytics",
         "Traffic, users, sessions, conversion tracking, campaign measurement, KPIs.",
         json.dumps(["Traffic Sources & Acquisition Channels", "Users & Sessions Analysis", "Conversion Tracking Architecture", "Campaign Measurement & UTMs", "Web Analytics KPIs (GA4)"]),
         json.dumps(["Configuring custom GA4 exploration reports", "Building standard UTM tagging convention sheet"]),
         json.dumps(["Track visitor behavior and conversions accurately", "Analyze web traffic channels"]), 12),

        (dm_course_id, 8, "Performance Marketing",
         "CPC, CPM, CTR, CPL, CPA, ROAS, campaign optimization.",
         json.dumps(["Performance Marketing KPIs (CPC, CPM, CTR, CPL, CPA)", "Return on Ad Spend (ROAS) Calculation", "Customer Acquisition Cost (CAC)", "Campaign Optimization Protocols", "Scaling Winning Ad Sets"]),
         json.dumps(["Budget scenario planning and ROAS calculation model", "Meta Ads campaign mockup with creative variations"]),
         json.dumps(["Calculate unit economics and ROAS accurately", "Optimize paid campaigns based on metrics"]), 12),

        (dm_course_id, 9, "AI Tools for Digital Marketing",
         "AI content workflows, research, creative ideation, marketing automation, responsible AI usage.",
         json.dumps(["AI Content Workflows & Prompting", "AI in Market Research & Personas", "Creative Ideation & Visual Briefing", "Marketing Automation", "Responsible AI Usage"]),
         json.dumps(["Developing an AI-assisted marketing workflow for daily content generation"]),
         json.dumps(["Incorporate AI tools safely to accelerate output", "Maintain brand voice and factual accuracy"]), 8),

        (dm_course_id, 10, "Capstone Project",
         "Student creates and documents a real digital marketing campaign/project.",
         json.dumps(["Brand Selection & Market Diagnosis", "Omnichannel Growth Strategy Formulation", "SEO, Content & Social Media Blueprint", "Paid Advertising Plan & Budgeting", "Performance Tracking, KPIs & Expected ROAS", "Executive Project Report"]),
         json.dumps(["Complete comprehensive Digital Marketing Project Dossier and campaign roadmap"]),
         json.dumps(["Deliver professional digital marketing strategy dossier ready for commercial execution"]), 10)
    ]
    cursor.executemany("""
    INSERT INTO course_modules (course_id, module_number, title, description, topics_json, practical_activities_json, learning_outcomes_json, hours)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, dm_modules)

    # 6. Mentors
    mentors = [
        ("Er. Vikas Agrawal", "Senior Data Analyst & Technical Lead", "vikas.agrawal@technoglobe.co.in", "+91 98290 88771", "Over 8 years experience in Business Intelligence, SQL, Python, and enterprise Power BI reporting.", 1),
        ("Ms. Neha Singhal", "Digital Marketing Strategist & Campaign Lead", "neha.singhal@technoglobe.co.in", "+91 94140 33221", "Google Ads certified professional with 7 years expertise in Performance Marketing, SEO, and Brand Growth.", 1)
    ]
    cursor.executemany("INSERT INTO mentors (name, designation, email, phone, bio, is_active) VALUES (?, ?, ?, ?, ?, ?)", mentors)

    # 7. Batches
    batches = [
        (da_course_id, "DA-2026-B1", "Summer Internship 2026 - Data Analytics", "2026-06-01", "2026-07-12", 1, 30),
        (dm_course_id, "DM-2026-B1", "Summer Internship 2026 - Digital Marketing", "2026-06-01", "2026-07-12", 2, 30)
    ]
    cursor.executemany("INSERT INTO batches (course_id, batch_code, name, start_date, end_date, mentor_id, max_students) VALUES (?, ?, ?, ?, ?, ?, ?)", batches)

    # 8. Document Templates (Visual Block Customizer)
    templates = [
        ("offer_letter", "Internship Enrollment & Offer Letter", json.dumps([
            {"id": "header", "label": "Franchise Header & Logo", "enabled": True},
            {"id": "doc_ref", "label": "Document Reference & Date", "enabled": True},
            {"id": "recipient", "label": "Student Academic Information", "enabled": True},
            {"id": "subject", "label": "Offer Letter Subject", "enabled": True},
            {"id": "body", "label": "Terms & Training Conditions", "enabled": True},
            {"id": "signatures", "label": "Authorized Signatures", "enabled": True}
        ])),
        ("joining_report", "Internship Commencement / Joining Report", json.dumps([
            {"id": "header", "label": "Franchise Header & Logo", "enabled": True},
            {"id": "doc_ref", "label": "Document Reference & Date", "enabled": True},
            {"id": "candidate_details", "label": "Candidate & Program Particulars", "enabled": True},
            {"id": "signatures", "label": "Student & Mentor Verification Signatures", "enabled": True}
        ])),
        ("attendance_summary", "Official Attendance Summary & Audit Report", json.dumps([
            {"id": "header", "label": "Franchise Header & Logo", "enabled": True},
            {"id": "audit_table", "label": "Metric / Parameter Audit Table", "enabled": True},
            {"id": "compliance_statement", "label": "Academic Attendance Certification", "enabled": True},
            {"id": "signatures", "label": "Mentor & Director Signatures", "enabled": True}
        ])),
        ("daily_logbook", "Daily Internship Activity Logbook", json.dumps([
            {"id": "header", "label": "Franchise Header & Logo", "enabled": True},
            {"id": "log_table", "label": "Daily Activity & Practical Entries", "enabled": True},
            {"id": "signatures", "label": "Signatures & Daily Stamp", "enabled": True}
        ])),
        ("mentor_evaluation", "Formal Mentor Assessment & Rubric", json.dumps([
            {"id": "header", "label": "Franchise Header & Logo", "enabled": True},
            {"id": "rubric_table", "label": "Competency Evaluation Rubric", "enabled": True},
            {"id": "remarks", "label": "Mentor Overall Appraisal & Grade", "enabled": True},
            {"id": "signatures", "label": "Mentor Signature", "enabled": True}
        ])),
        ("completion_certificate", "Certificate of Internship Completion", json.dumps([
            {"id": "border", "label": "Guilloche Navy & Gold Border", "enabled": True},
            {"id": "header", "label": "TechnoGlobe Franchise Branding", "enabled": True},
            {"id": "candidate_name", "label": "Candidate Name & College", "enabled": True},
            {"id": "course_details", "label": "Course Title, Dates & Project", "enabled": True},
            {"id": "qr_verification", "label": "Self-Contained QR Verification Block", "enabled": True},
            {"id": "signatures", "label": "Mentor & Director Signatures", "enabled": True},
            {"id": "seal", "label": "Official Centre Seal Box", "enabled": True}
        ])),
        ("experience_certificate", "Industrial Training & Experience Certificate", json.dumps([
            {"id": "header", "label": "Franchise Header & Logo", "enabled": True},
            {"id": "body", "label": "Experience Certification Statement", "enabled": True},
            {"id": "ref_block", "label": "Verification Reference Block", "enabled": True},
            {"id": "signatures", "label": "Authorized Signatory", "enabled": True}
        ])),
        ("consolidated_report", "Complete Academic Internship Report", json.dumps([
            {"id": "cover_page", "label": "Academic Report Cover Page", "enabled": True},
            {"id": "candidate_decl", "label": "Candidate Declaration", "enabled": True},
            {"id": "supervisor_cert", "label": "Supervisor Certificate", "enabled": True},
            {"id": "acknowledgements", "label": "Acknowledgements", "enabled": True},
            {"id": "executive_summary", "label": "Executive Summary", "enabled": True},
            {"id": "company_profile", "label": "Company Profile & Centre Overview", "enabled": True},
            {"id": "curriculum_details", "label": "Training Modules & Syllabus", "enabled": True},
            {"id": "capstone_project", "label": "Capstone Project Technical Dossier", "enabled": True},
            {"id": "conclusions", "label": "Conclusions & Signatures", "enabled": True}
        ]))
    ]
    cursor.executemany("INSERT OR IGNORE INTO document_templates (template_key, title, blocks_json) VALUES (?, ?, ?)", templates)

def seed_demo_students(cursor, conn):
    print("Seeding exactly 1 Data Analytics demo student and 1 Digital Marketing demo student...")
    da_course_id = 1
    dm_course_id = 2

    # Demo Student 1: Aarav Sharma (Data Analytics) - Poddar College, Bharatpur
    # Demo Student 1: Aarav Sharma (Data Analytics) - Poddar College, Bharatpur
    cursor.execute("""
    INSERT INTO students (
        full_name, father_mother_name, dob, gender, mobile, email, address, city, state,
        college_name, degree, branch, semester_year, academic_session, is_demo
    ) VALUES (
        'Aarav Sharma', 'Sh. Rakesh Sharma', '2004-08-14', 'Male', '+91 98765 43210',
        'aarav.sharma@example.com', '142, Subhash Nagar, Near Jawahar Park', 'Bharatpur', 'Rajasthan',
        'Poddar College, Bharatpur', 'BCA', 'Computer Science', '6th Semester', '2025-2026', 1
    );
    """)
    s1_id = cursor.lastrowid

    # Demo Student 2: Priya Verma (Digital Marketing) - Poddar College, Bharatpur
    cursor.execute("""
    INSERT INTO students (
        full_name, father_mother_name, dob, gender, mobile, email, address, city, state,
        college_name, degree, branch, semester_year, academic_session, is_demo
    ) VALUES (
        'Priya Verma', 'Sh. Mahendra Verma', '2004-11-20', 'Female', '+91 97851 23456',
        'priya.verma@example.com', '78, Civil Lines, Opposite Circuit House', 'Bharatpur', 'Rajasthan',
        'Poddar College, Bharatpur', 'B.Sc (Bio)', 'Biology', '4th Semester', '2025-2026', 1
    );
    """)
    s2_id = cursor.lastrowid

    # Internships with Self-Contained Human-Readable Plain Text QR Payloads
    qr_payload_da = """TECHNOGLOBE INTERNSHIP CERTIFICATE
Candidate: Aarav Sharma
College: Poddar College, Bharatpur
Course: Data Analytics
Program: BCA - Computer Science (6th Semester)
Cert No: TG-BPT-DA-2026-0001
Ver ID: VER-TG-DA-98214
Duration: 6 Weeks (120 Hours)
Status: Officially Verified & Authentic"""

    qr_payload_dm = """TECHNOGLOBE INTERNSHIP CERTIFICATE
Candidate: Priya Verma
College: Poddar College, Bharatpur
Course: Digital Marketing
Program: B.Sc (Bio) - Biology (6th Semester)
Cert No: TG-BPT-DM-2026-0002
Ver ID: VER-TG-DM-44129
Duration: 6 Weeks (120 Hours)
Status: Officially Verified & Authentic"""

    cursor.execute("""
    INSERT INTO internships (
        student_id, course_id, batch_id, mentor_id, internship_title, internship_type,
        start_date, end_date, total_days, total_training_hours, mode, status,
        certificate_number, verification_code, qr_payload_json, is_locked, finalized_at
    ) VALUES (
        ?, ?, 1, 1,
        'Course-Based Internship in Data Analytics & Business Intelligence',
        'Course-Based Internship',
        '2026-06-01', '2026-07-12', 36, 120, 'Offline', 'CERTIFIED',
        'TG-BPT-DA-2026-0001', 'VER-TG-DA-98214', ?, 1, '2026-07-14 11:30:00'
    );
    """, (s1_id, da_course_id, qr_payload_da))
    int1_id = cursor.lastrowid

    cursor.execute("""
    INSERT INTO internships (
        student_id, course_id, batch_id, mentor_id, internship_title, internship_type,
        start_date, end_date, total_days, total_training_hours, mode, status,
        certificate_number, verification_code, qr_payload_json, is_locked, finalized_at
    ) VALUES (
        ?, ?, 2, 2,
        'Course-Based Internship in Digital Marketing & Growth Strategies',
        'Course-Based Internship',
        '2026-06-01', '2026-07-12', 36, 120, 'Offline', 'CERTIFIED',
        'TG-BPT-DM-2026-0002', 'VER-TG-DM-44129', ?, 1, '2026-07-14 11:45:00'
    );
    """, (s2_id, dm_course_id, qr_payload_dm))
    int2_id = cursor.lastrowid

    # Compliance records
    cursor.execute("""
    INSERT INTO compliance_records (
        internship_id, university_name, department, faculty_coordinator, faculty_designation,
        approval_status, approval_ref, approval_date, required_duration, required_hours, required_attendance_pct
    ) VALUES (?, 'Poddar College, Bharatpur', 'Department of Computer Science', 'Dr. S. K. Gupta', 'HOD Computer Science', 'APPROVED', 'PC/INT/2026/041', '2026-05-25', '6 Weeks', 120, 75.0)
    """, (int1_id,))

    cursor.execute("""
    INSERT INTO compliance_records (
        internship_id, university_name, department, faculty_coordinator, faculty_designation,
        approval_status, approval_ref, approval_date, required_duration, required_hours, required_attendance_pct
    ) VALUES (?, 'Poddar College, Bharatpur', 'Department of Management Studies', 'Prof. Anjali Mathur', 'Internship Coordinator', 'APPROVED', 'PC/INT/2026/042', '2026-05-28', '6 Weeks', 120, 75.0)
    """, (int2_id,))

    # Seed 36 attendance records and daily logs for each demo student
    start_dt = datetime.strptime("2026-06-01", "%Y-%m-%d")
    current_dt = start_dt
    day_count = 0

    while day_count < 36:
        if current_dt.weekday() != 6:  # Skip Sunday
            date_str = current_dt.strftime("%Y-%m-%d")
            day_name = current_dt.strftime("%A")

            # Student 1 (100% attendance)
            cursor.execute("""
            INSERT INTO attendance (internship_id, date, day_of_week, start_time, end_time, total_hours, topic_covered, status, student_signed, mentor_signed)
            VALUES (?, ?, ?, '10:00 AM', '01:30 PM', 3.5, ?, 'PRESENT', 1, 1)
            """, (int1_id, date_str, day_name, f"Practical Module Task {day_count + 1}"))

            cursor.execute("""
            INSERT INTO daily_logs (internship_id, date, day_of_week, module_name, topic, work_performed, practical_activity, tools_used, learning_outcome, hours, mentor_remarks, student_signed, mentor_signed)
            VALUES (?, ?, ?, 'Core Module Track', ?, 'Completed structured laboratory exercises and data modeling', 'Executed hands-on practical implementation', 'Python / Power BI / SQL', 'Acquired practical technical competency', 3.5, 'Satisfactory progress demonstrated.', 1, 1)
            """, (int1_id, date_str, day_name, f"Technical Topic {day_count + 1}"))

            # Student 2 (34 Present, 2 Leave)
            st2_status = 'AUTHORIZED LEAVE' if day_count in (13, 27) else 'PRESENT'
            st2_hours = 0.0 if st2_status == 'AUTHORIZED LEAVE' else 3.5
            cursor.execute("""
            INSERT INTO attendance (internship_id, date, day_of_week, start_time, end_time, total_hours, topic_covered, status, student_signed, mentor_signed, remarks)
            VALUES (?, ?, ?, '10:00 AM', '01:30 PM', ?, ?, ?, 1, 1, ?)
            """, (int2_id, date_str, day_name, st2_hours, f"Digital Marketing Practical {day_count + 1}", st2_status, 'Approved Leave' if st2_status == 'AUTHORIZED LEAVE' else None))

            if st2_status == 'PRESENT':
                cursor.execute("""
                INSERT INTO daily_logs (internship_id, date, day_of_week, module_name, topic, work_performed, practical_activity, tools_used, learning_outcome, hours, mentor_remarks, student_signed, mentor_signed)
                VALUES (?, ?, ?, 'Marketing Track', ?, 'Executed marketing campaign design and analytical tracking', 'Developed campaign briefs and creative variations', 'Meta Ads / GA4 / SEO Tools', 'Mastered performance marketing principles', 3.5, 'Great creative and analytical initiative.', 1, 1)
                """, (int2_id, date_str, day_name, f"Marketing Topic {day_count + 1}"))

            day_count += 1
        current_dt += timedelta(days=1)

    # 6 Weekly Reports for each student
    for w in range(1, 7):
        cursor.execute("""
        INSERT INTO weekly_reports (internship_id, week_number, start_date, end_date, topics_covered, practical_work, project_progress, skills_learned, hours_completed, mentor_remarks, student_signed, mentor_signed)
        VALUES (?, ?, ?, ?, 'Technical & Practical Curriculum Review', 'Hands-on laboratory implementation', 'Milestone deliverables submitted', 'Technical competencies mastered', 21.0, 'Demonstrated excellent learning pace.', 1, 1)
        """, (int1_id, w, f"2026-06-0{w}" if w < 10 else f"2026-06-{w}", f"2026-06-{w+5}"))

        cursor.execute("""
        INSERT INTO weekly_reports (internship_id, week_number, start_date, end_date, topics_covered, practical_work, project_progress, skills_learned, hours_completed, mentor_remarks, student_signed, mentor_signed)
        VALUES (?, ?, ?, ?, 'Marketing Strategy & Analytics Review', 'Campaign creation & audit execution', 'Milestones achieved on schedule', 'Campaign optimization skills', 21.0, 'Consistent execution and diligence.', 1, 1)
        """, (int2_id, w, f"2026-06-0{w}" if w < 10 else f"2026-06-{w}", f"2026-06-{w+5}"))

    # Projects
    da_proj = {
        "project_title": "Retail Sales Performance & Customer Churn Analytics Dashboard",
        "problem_statement": "An omnichannel retail chain operating across North India faced a 14% year-over-year dip in customer repeat purchase rate. The management lacked a consolidated real-time dashboard to track store performance and customer churn.",
        "dataset": "Relational retail database comprising 65,000+ orders, 12,000 customer profiles, and 3 years of transactional records.",
        "tools": "Microsoft Excel 365, PostgreSQL, Python (Pandas, NumPy), Power BI Desktop, DAX.",
        "objectives": "1. Build automated data ingestion pipeline.\n2. Design Star Schema in Power BI.\n3. Segment churn risk via RFM analysis.\n4. Deliver executive dashboards.",
        "findings": "Top 20% loyal customers drove 64% of total revenue. Customers inactive for 45 days had 82% churn likelihood.",
        "recommendations": "Deploy automated Day-30 SMS/Email re-engagement triggers to recover estimated Rs. 42 Lakhs annually.",
        "conclusion": "Delivered robust BI solution reducing reporting turnaround from 5 days to real-time."
    }
    cursor.execute("""
    INSERT INTO projects (internship_id, project_title, project_type, project_description, objectives, fields_json, status, submitted_at, approved_at)
    VALUES (?, ?, 'Capstone Project', ?, ?, ?, 'APPROVED', '2026-07-11 16:00:00', '2026-07-12 11:00:00')
    """, (int1_id, da_proj["project_title"], da_proj["problem_statement"], da_proj["objectives"], json.dumps(da_proj)))

    dm_proj = {
        "project_title": "Omnichannel Lead Generation & SEO Growth Campaign for Local Healthcare Clinic",
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
    VALUES (?, ?, 'Live Campaign Project', ?, ?, ?, 'APPROVED', '2026-07-11 16:30:00', '2026-07-12 11:30:00')
    """, (int2_id, dm_proj["project_title"], dm_proj["brand_business"], dm_proj["campaign_objective"], json.dumps(dm_proj)))

    # Evaluations
    cursor.execute("""
    INSERT INTO evaluations (internship_id, mentor_id, criteria_scores_json, overall_score, final_remark, evaluated_at, mentor_signed)
    VALUES (?, 1, '{}', 94, 'Aarav demonstrated exemplary analytical thinking, disciplined attendance, and mastery of Power BI and Python.', '2026-07-13 14:00:00', 1)
    """, (int1_id,))

    cursor.execute("""
    INSERT INTO evaluations (internship_id, mentor_id, criteria_scores_json, overall_score, final_remark, evaluated_at, mentor_signed)
    VALUES (?, 2, '{}', 93, 'Priya demonstrated outstanding creativity, strong grasp of digital marketing funnels, and excellent presentation skills.', '2026-07-13 14:30:00', 1)
    """, (int2_id,))

    # Certificates in internal registry
    cursor.execute("""
    INSERT INTO certificates (internship_id, cert_type, certificate_number, verification_code, qr_payload_json, issue_date, is_finalized, finalized_by)
    VALUES (?, 'COMPLETION', 'TG-BPT-DA-2026-0001', 'VER-TG-DA-98214', ?, '2026-07-14', 1, 'Er. Rajesh Sharma (Centre Director)')
    """, (int1_id, qr_payload_da))

    cursor.execute("""
    INSERT INTO certificates (internship_id, cert_type, certificate_number, verification_code, qr_payload_json, issue_date, is_finalized, finalized_by)
    VALUES (?, 'COMPLETION', 'TG-BPT-DM-2026-0002', 'VER-TG-DM-44129', ?, '2026-07-14', 1, 'Er. Rajesh Sharma (Centre Director)')
    """, (int2_id, qr_payload_dm))

    # Audit Logs
    cursor.execute("""
    INSERT INTO audit_logs (user_id, user_name, action, entity_type, entity_id, details_json)
    VALUES (1, 'Centre Administrator', 'SYSTEM_INITIALIZATION', 'SYSTEM', 1, '{"message": "TechnoGlobe Bharatpur Internal System initialized with exactly 2 demo records"}')
    """)

    print("Demo students seeded successfully.")

def seed():
    init_db()
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM centre_settings")
    if cursor.fetchone()[0] == 0:
        _seed_base_data(cursor, conn)

    cursor.execute("SELECT COUNT(*) FROM students")
    if cursor.fetchone()[0] == 0:
        seed_demo_students(cursor, conn)

    conn.commit()
    conn.close()
    print("Database seeding check complete.")

def delete_demo_data():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM students WHERE is_demo = 1")
    demo_student_ids = [r[0] for r in cursor.fetchall()]
    for s_id in demo_student_ids:
        cursor.execute("SELECT id FROM internships WHERE student_id = ?", (s_id,))
        for i_row in cursor.fetchall():
            int_id = i_row[0]
            cursor.execute("DELETE FROM attendance WHERE internship_id = ?", (int_id,))
            cursor.execute("DELETE FROM daily_logs WHERE internship_id = ?", (int_id,))
            cursor.execute("DELETE FROM weekly_reports WHERE internship_id = ?", (int_id,))
            cursor.execute("DELETE FROM projects WHERE internship_id = ?", (int_id,))
            cursor.execute("DELETE FROM evaluations WHERE internship_id = ?", (int_id,))
            cursor.execute("DELETE FROM feedback WHERE internship_id = ?", (int_id,))
            cursor.execute("DELETE FROM certificates WHERE internship_id = ?", (int_id,))
            cursor.execute("DELETE FROM compliance_records WHERE internship_id = ?", (int_id,))
            cursor.execute("DELETE FROM internships WHERE id = ?", (int_id,))
        cursor.execute("DELETE FROM students WHERE id = ?", (s_id,))
    cursor.execute("""
    INSERT INTO audit_logs (user_id, user_name, action, entity_type, entity_id, details_json)
    VALUES (1, 'Centre Administrator', 'DEMO_DATA_DELETED', 'SYSTEM', 0, '{"message": "Demo data deleted successfully"}')
    """)
    conn.commit()
    conn.close()
    print("Demo data deleted successfully.")

def reset_demo_data():
    delete_demo_data()
    conn = get_db()
    cursor = conn.cursor()
    seed_demo_students(cursor, conn)
    cursor.execute("""
    INSERT INTO audit_logs (user_id, user_name, action, entity_type, entity_id, details_json)
    VALUES (1, 'Centre Administrator', 'DEMO_DATA_RESET', 'SYSTEM', 0, '{"message": "Demo data reset successfully with 2 students"}')
    """)
    conn.commit()
    conn.close()
    print("Demo data reset successfully.")

if __name__ == "__main__":
    seed()
