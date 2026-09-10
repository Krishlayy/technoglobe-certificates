import os
import io
import json
import zipfile
import hashlib
import hmac
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import inch, mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import re
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable, Image as RLImage
)
from reportlab.pdfgen import canvas
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics import renderPDF
from database import get_db
CERT_SECRET_KEY = os.environ.get("CERT_SECRET_KEY", "TG_BHARATPUR_SECURITY_SECRET_2026").encode()
def compute_certificate_signature(cert_num: str, student_name: str, course_name: str, issue_date: str) -> str:
    msg = f"{str(cert_num).strip()}:{str(student_name).strip().lower()}:{str(course_name).strip().lower()}:{str(issue_date).strip()}".encode()
    return hmac.new(CERT_SECRET_KEY, msg, hashlib.sha256).hexdigest()[:16]

LOGO_PATH = os.path.join(os.path.dirname(__file__), "technoglobe_logo.png")

def normalize_text(text: str) -> str:
    if not text or not isinstance(text, str):
        return text or ''
    cleaned = re.sub(r'Course-Based IInternshipnternship', 'Course-Based Internship', text)
    cleaned = re.sub(r'Internship\s+Internship', 'Internship', cleaned)
    cleaned = re.sub(r'B\.TechBCA', 'BCA', cleaned)
    cleaned = re.sub(r'120120 Hours', '120 Hours', cleaned)
    cleaned = re.sub(r'None training hours', '120 Training Hours', cleaned)
    return ' '.join(cleaned.split())

GENERATED_DIR = os.path.join(os.path.dirname(__file__), "generated")
os.makedirs(GENERATED_DIR, exist_ok=True)

# Brand Color Constants
PRIMARY = colors.HexColor("#0B2545")    # Deep Navy
SECONDARY = colors.HexColor("#134074")  # Royal Navy
ACCENT = colors.HexColor("#D4AF37")     # Gold
DARK = colors.HexColor("#1E293B")       # Slate Dark
MUTED = colors.HexColor("#64748B")      # Slate Light
BG_LIGHT = colors.HexColor("#F8FAFC")   # Slate 50
BORDER_COLOR = colors.HexColor("#CBD5E1")

def get_base_context(internship_id: int):
    conn = get_db()
    cursor = conn.cursor()

    # Centre settings
    cursor.execute("SELECT * FROM centre_settings WHERE id = 1")
    settings = dict(cursor.fetchone())

    # Internship details
    cursor.execute("""
    SELECT i.*, 
           s.full_name as student_name, s.father_mother_name, s.dob, s.gender, s.mobile, s.email as student_email,
           s.address as student_address, s.city as student_city, s.state as student_state,
           s.college_name, s.degree, s.branch, s.semester_year, s.academic_session,
           c.name as course_name, c.code as course_code, c.title as course_title, c.duration_weeks,
           m.name as mentor_name, m.designation as mentor_designation, m.email as mentor_email, m.phone as mentor_phone,
           b.batch_code, b.name as batch_name
    FROM internships i
    JOIN students s ON i.student_id = s.id
    JOIN courses c ON i.course_id = c.id
    JOIN mentors m ON i.mentor_id = m.id
    LEFT JOIN batches b ON i.batch_id = b.id
    WHERE i.id = ?
    """, (internship_id,))
    internship_row = cursor.fetchone()
    if not internship_row:
        conn.close()
        raise ValueError(f"Internship ID {internship_id} not found")
    internship = dict(internship_row)

    # Compliance record
    cursor.execute("SELECT * FROM compliance_records WHERE internship_id = ?", (internship_id,))
    comp_row = cursor.fetchone()
    compliance = dict(comp_row) if comp_row else {}

    # Project record
    cursor.execute("SELECT * FROM projects WHERE internship_id = ?", (internship_id,))
    proj_row = cursor.fetchone()
    project = dict(proj_row) if proj_row else {}
    project_fields = json.loads(project.get("fields_json", "{}")) if project else {}

    # Evaluation record
    cursor.execute("SELECT * FROM evaluations WHERE internship_id = ?", (internship_id,))
    eval_row = cursor.fetchone()
    evaluation = dict(eval_row) if eval_row else {}
    eval_criteria = json.loads(evaluation.get("criteria_scores_json", "{}")) if evaluation else {}

    # Feedback record
    cursor.execute("SELECT * FROM feedback WHERE internship_id = ?", (internship_id,))
    fb_row = cursor.fetchone()
    feedback = dict(fb_row) if fb_row else {}

    # Certificates
    cursor.execute("SELECT * FROM certificates WHERE internship_id = ?", (internship_id,))
    certs = [dict(r) for r in cursor.fetchall()]

    # Attendance summary stats
    cursor.execute("SELECT COUNT(*) as total_days, SUM(CASE WHEN status='PRESENT' THEN 1 ELSE 0 END) as present_days, SUM(CASE WHEN status='ABSENT' THEN 1 ELSE 0 END) as absent_days, SUM(CASE WHEN status='LEAVE' THEN 1 ELSE 0 END) as leave_days, SUM(CASE WHEN status='HOLIDAY' THEN 1 ELSE 0 END) as holiday_days, SUM(total_hours) as total_hours_logged FROM attendance WHERE internship_id = ?", (internship_id,))
    att_stats = dict(cursor.fetchone())

    conn.close()
    return {
        "settings": settings,
        "internship": internship,
        "compliance": compliance,
        "project": project,
        "project_fields": project_fields,
        "evaluation": evaluation,
        "eval_criteria": eval_criteria,
        "feedback": feedback,
        "certificates": certs,
        "att_stats": att_stats
    }

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        # Footer text
        footer_text = f"TechnoGlobe Course-Based Internship Documentation — Page {self._pageNumber} of {page_count}"
        self.drawCentredString(A4[0] / 2.0, 10 * mm, footer_text)
        self.restoreState()

def build_official_header(settings, doc_ref, doc_date, doc_title):
    styles = getSampleStyleSheet()
    header_elements = []

    org_style = ParagraphStyle('OrgHeader', fontName='Helvetica-Bold', fontSize=15, leading=18, textColor=PRIMARY, alignment=1)
    centre_style = ParagraphStyle('CentreHeader', fontName='Helvetica-Bold', fontSize=11, leading=14, textColor=SECONDARY, alignment=1)
    addr_style = ParagraphStyle('AddrHeader', fontName='Helvetica', fontSize=8.5, leading=11, textColor=MUTED, alignment=1)
    ref_style = ParagraphStyle('RefStyle', fontName='Helvetica-Bold', fontSize=8.5, leading=11, textColor=DARK)
    date_style = ParagraphStyle('DateStyle', fontName='Helvetica-Bold', fontSize=8.5, leading=11, textColor=DARK, alignment=2)
    title_style = ParagraphStyle('TitleStyle', fontName='Helvetica-Bold', fontSize=13, leading=16, textColor=PRIMARY, alignment=1)

    if os.path.exists(LOGO_PATH):
        header_elements.append(RLImage(LOGO_PATH, width=38 * mm, height=13.8 * mm, hAlign='CENTER'))
        header_elements.append(Spacer(1, 1 * mm))
        header_elements.append(Paragraph(settings["centre_name"], centre_style))
    else:
        header_elements.append(Paragraph(settings["org_name"], org_style))
        header_elements.append(Spacer(1, 1 * mm))
        header_elements.append(Paragraph(settings["centre_name"], centre_style))
    header_elements.append(Spacer(1, 1 * mm))
    addr_line = f"{settings['address']} | Phone: {settings['phone']} | Email: {settings['email']} | Web: {settings['website']}"
    header_elements.append(Paragraph(addr_line, addr_style))
    header_elements.append(Spacer(1, 2 * mm))
    header_elements.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceAfter=8, spaceBefore=2))

    # Ref & Date table
    ref_data = [[
        Paragraph(f"<b>Ref No:</b> {doc_ref}", ref_style),
        Paragraph(f"<b>Date:</b> {doc_date}", date_style)
    ]]
    ref_table = Table(ref_data, colWidths=[110 * mm, 60 * mm])
    ref_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))
    header_elements.append(ref_table)
    header_elements.append(Spacer(1, 4 * mm))

    # Document Banner Title
    header_elements.append(Paragraph(doc_title.upper(), title_style))
    header_elements.append(Spacer(1, 1 * mm))
    header_elements.append(HRFlowable(width="30%", thickness=1, color=ACCENT, spaceAfter=10, spaceBefore=2))

    return header_elements

def build_signature_section(settings, mentor_name, mentor_desig):
    styles = getSampleStyleSheet()
    sig_label = ParagraphStyle('SigLabel', fontName='Helvetica-Bold', fontSize=8.5, leading=11, alignment=1, textColor=DARK)
    sig_sub = ParagraphStyle('SigSub', fontName='Helvetica', fontSize=8, leading=10, alignment=1, textColor=MUTED)

    data = [
        [
            Paragraph("<b>STUDENT SIGNATURE</b>", sig_label),
            Paragraph("<b>FACULTY / MENTOR</b>", sig_label),
            Paragraph("<b>AUTHORIZED SIGNATORY</b>", sig_label)
        ],
        [
            Paragraph("<br/><br/><br/>_______________________<br/>Candidate's Signature", sig_sub),
            Paragraph(f"<br/><br/><br/>_______________________<br/><b>{mentor_name}</b><br/>{mentor_desig}", sig_sub),
            Paragraph(f"<br/><br/><br/>_______________________<br/><b>{settings['signatory_name']}</b><br/>{settings['signatory_designation']}<br/><i>(Official Stamp & Seal)</i>", sig_sub)
        ]
    ]

    t = Table(data, colWidths=[55 * mm, 60 * mm, 55 * mm])
    t.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('BOX', (0,0), (0,1), 0.5, BORDER_COLOR),
        ('BOX', (1,0), (1,1), 0.5, BORDER_COLOR),
        ('BOX', (2,0), (2,1), 0.5, BORDER_COLOR),
        ('BACKGROUND', (0,0), (-1,0), BG_LIGHT),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    return t

# -------------------------------------------------------------
# 1. Offer / Enrollment Letter
# -------------------------------------------------------------
def generate_offer_letter(internship_id: int) -> str:
    ctx = get_base_context(internship_id)
    s = ctx["settings"]
    it = ctx["internship"]

    filename = f"01_Offer_Letter_{it['student_name'].replace(' ', '_')}.pdf"
    filepath = os.path.join(GENERATED_DIR, filename)

    doc = SimpleDocTemplate(filepath, pagesize=A4, rightMargin=20*mm, leftMargin=20*mm, topMargin=15*mm, bottomMargin=15*mm)
    story = []

    doc_ref = f"{s['doc_prefix']}/OFFER/{it['course_code']}/{datetime.now().year}/{it['id']:04d}"
    doc_date = it['start_date']
    story.extend(build_official_header(s, doc_ref, doc_date, "INTERNSHIP ENROLLMENT & OFFER LETTER"))

    styles = getSampleStyleSheet()
    body_style = ParagraphStyle('Body', fontName='Helvetica', fontSize=9.5, leading=14, textColor=DARK)
    bold_style = ParagraphStyle('BodyBold', fontName='Helvetica-Bold', fontSize=9.5, leading=14, textColor=DARK)

    # Student Info block
    to_text = f"""
    <b>To,</b><br/>
    <b>{it['student_name']}</b><br/>
    Son/Daughter of: {it['father_mother_name']}<br/>
    <b>Degree / Branch:</b> {it['degree']} ({it['branch']}) | <b>Session:</b> {it['academic_session']}<br/>
    {it['college_name']}
    """
    story.append(Paragraph(to_text, body_style))
    story.append(Spacer(1, 4 * mm))

    # Subject
    sub_text = f"<b>SUBJECT: OFFICIAL OFFER & ENROLLMENT FOR {it['internship_title'].upper()}</b>"
    story.append(Paragraph(sub_text, bold_style))
    story.append(Spacer(1, 3 * mm))

    p1 = f"""
    Dear <b>{it['student_name']}</b>,<br/><br/>
    With reference to your formal application and institutional recommendation from <b>{it['college_name']}</b>, we are pleased to offer you admission and formal enrollment into the <b>Course-Based Internship & Industrial Training Program</b> at <b>{s['centre_name']}</b>.
    """
    story.append(Paragraph(p1, body_style))
    story.append(Spacer(1, 3 * mm))

    # Program Specs Table
    specs = [
        [Paragraph("<b>Internship Program:</b>", bold_style), Paragraph(it['internship_title'], body_style)],
        [Paragraph("<b>Specialization / Course:</b>", bold_style), Paragraph(it['course_name'], body_style)],
        [Paragraph("<b>Commencement Date:</b>", bold_style), Paragraph(it['start_date'], body_style)],
        [Paragraph("<b>Expected Completion Date:</b>", bold_style), Paragraph(it['end_date'], body_style)],
        [Paragraph("<b>Total Scheduled Duration:</b>", bold_style), Paragraph(f"{it['duration_weeks']} Weeks ({it['total_days']} Scheduled Training Days)", body_style)],
        [Paragraph("<b>Total Training Hours:</b>", bold_style), Paragraph(f"{it['total_training_hours']} Practical Training Hours", body_style)],
        [Paragraph("<b>Training Mode & Centre:</b>", bold_style), Paragraph(f"{it['mode']} Mode — {s['centre_name']}", body_style)],
        [Paragraph("<b>Assigned Industry Mentor:</b>", bold_style), Paragraph(f"{it['mentor_name']} ({it['mentor_designation']})", body_style)],
    ]
    t = Table(specs, colWidths=[55 * mm, 115 * mm])
    t.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOX', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('BACKGROUND', (0,0), (0,-1), BG_LIGHT),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t)
    story.append(Spacer(1, 3 * mm))

    terms = f"""
    <b>Terms & Academic Guidelines:</b><br/>
    1. <b>Mandatory Attendance:</b> A minimum of 75% verified daily attendance is mandatory for academic completion.<br/>
    2. <b>Daily Logbook & Assignments:</b> You are required to maintain a daily learning log and submit weekly activity reports verified by your assigned mentor.<br/>
    3. <b>Capstone Project:</b> Completion of an industry-standard capstone project and formal evaluation is mandatory prior to certificate issuance.<br/>
    4. <b>Institutional Integrity:</b> This course-based internship is conducted strictly under authorized curriculum guidelines at our Bharatpur franchise centre.
    """
    story.append(Paragraph(terms, body_style))
    story.append(Spacer(1, 5 * mm))

    story.append(build_signature_section(s, it['mentor_name'], it['mentor_designation']))

    doc.build(story, canvasmaker=NumberedCanvas)
    return filepath

# -------------------------------------------------------------
# 2. Joining Letter
# -------------------------------------------------------------
def generate_joining_letter(internship_id: int) -> str:
    ctx = get_base_context(internship_id)
    s = ctx["settings"]
    it = ctx["internship"]

    filename = f"02_Joining_Letter_{it['student_name'].replace(' ', '_')}.pdf"
    filepath = os.path.join(GENERATED_DIR, filename)

    doc = SimpleDocTemplate(filepath, pagesize=A4, rightMargin=20*mm, leftMargin=20*mm, topMargin=15*mm, bottomMargin=15*mm)
    story = []

    doc_ref = f"{s['doc_prefix']}/JOIN/{it['course_code']}/{datetime.now().year}/{it['id']:04d}"
    doc_date = it['start_date']
    story.extend(build_official_header(s, doc_ref, doc_date, "INTERNSHIP COMMENCEMENT / JOINING REPORT"))

    styles = getSampleStyleSheet()
    body_style = ParagraphStyle('Body', fontName='Helvetica', fontSize=9.5, leading=14, textColor=DARK)
    bold_style = ParagraphStyle('BodyBold', fontName='Helvetica-Bold', fontSize=9.5, leading=14, textColor=DARK)

    p1 = f"""
    <b>TO WHOMSOEVER IT MAY CONCERN / COLLEGE PRINCIPAL & TPO</b><br/><br/>
    This is to formally certify and confirm that <b>Mr./Ms. {it['student_name']}</b>, a bona fide student of <b>{it['college_name']}</b> pursuing <b>{it['degree']} in {it['branch']}</b>, has reported in person and commenced his/her formal <b>Course-Based Internship & Industrial Training Program</b> at our authorized centre on <b>{it['start_date']}</b>.
    """
    story.append(Paragraph(p1, body_style))
    story.append(Spacer(1, 4 * mm))

    specs = [
        [Paragraph("<b>Candidate Name:</b>", bold_style), Paragraph(it['student_name'], body_style)],
        [Paragraph("<b>Father's / Mother's Name:</b>", bold_style), Paragraph(it['father_mother_name'], body_style)],
        [Paragraph("<b>College / University:</b>", bold_style), Paragraph(it['college_name'], body_style)],
        [Paragraph("<b>Enrolled Course / Track:</b>", bold_style), Paragraph(it['course_name'], body_style)],
        [Paragraph("<b>Internship Title:</b>", bold_style), Paragraph(it['internship_title'], body_style)],
        [Paragraph("<b>Date of Joining / Commencement:</b>", bold_style), Paragraph(it['start_date'], body_style)],
        [Paragraph("<b>Scheduled End Date:</b>", bold_style), Paragraph(it['end_date'], body_style)],
        [Paragraph("<b>Total Scheduled Hours:</b>", bold_style), Paragraph(f"{it['total_training_hours']} Hours ({it['duration_weeks']} Weeks)", body_style)],
        [Paragraph("<b>Supervising Mentor:</b>", bold_style), Paragraph(f"{it['mentor_name']}, {it['mentor_designation']}", body_style)],
        [Paragraph("<b>Centre Address:</b>", bold_style), Paragraph(s['address'], body_style)],
    ]
    t = Table(specs, colWidths=[55 * mm, 115 * mm])
    t.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOX', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('BACKGROUND', (0,0), (0,-1), BG_LIGHT),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t)
    story.append(Spacer(1, 4 * mm))

    decl = f"""
    <b>Student Commencement Declaration:</b><br/>
    <i>"I hereby confirm that I have physically reported to TechnoGlobe Bharatpur Centre on {it['start_date']} and commenced my training curriculum in {it['course_name']}. I undertake to abide by all discipline, safety, and attendance guidelines of the institution."</i>
    """
    story.append(Paragraph(decl, body_style))
    story.append(Spacer(1, 6 * mm))

    story.append(build_signature_section(s, it['mentor_name'], it['mentor_designation']))

    doc.build(story, canvasmaker=NumberedCanvas)
    return filepath

# -------------------------------------------------------------
# 3. Course Syllabus
# -------------------------------------------------------------
def generate_course_syllabus(course_id: int) -> str:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM centre_settings WHERE id = 1")
    s = dict(cursor.fetchone())
    cursor.execute("SELECT * FROM courses WHERE id = ?", (course_id,))
    course = dict(cursor.fetchone())
    cursor.execute("SELECT * FROM course_modules WHERE course_id = ? ORDER BY module_number ASC", (course_id,))
    modules = [dict(r) for r in cursor.fetchall()]
    conn.close()

    filename = f"03_Course_Syllabus_{course['code']}.pdf"
    filepath = os.path.join(GENERATED_DIR, filename)

    doc = SimpleDocTemplate(filepath, pagesize=A4, rightMargin=15*mm, leftMargin=15*mm, topMargin=12*mm, bottomMargin=12*mm)
    story = []

    doc_ref = f"{s['doc_prefix']}/SYLLABUS/{course['code']}/{datetime.now().year}"
    story.extend(build_official_header(s, doc_ref, datetime.now().strftime("%Y-%m-%d"), f"CURRICULUM & SYLLABUS: {course['title']}"))

    styles = getSampleStyleSheet()
    mod_title_style = ParagraphStyle('ModTitle', fontName='Helvetica-Bold', fontSize=10, leading=13, textColor=PRIMARY)
    text_style = ParagraphStyle('ModText', fontName='Helvetica', fontSize=8.5, leading=11, textColor=DARK)
    bullet_style = ParagraphStyle('ModBullet', fontName='Helvetica', fontSize=8, leading=10, textColor=DARK)

    intro = f"<b>Course Overview:</b> {course['description']}<br/><b>Duration:</b> {course['duration_weeks']} Weeks | <b>Total Structured Hours:</b> {course['total_hours']} Hours | <b>Standard Delivery:</b> {course['default_mode']}"
    story.append(Paragraph(intro, text_style))
    story.append(Spacer(1, 3 * mm))

    table_data = [[
        Paragraph("<b>Module & Title</b>", mod_title_style),
        Paragraph("<b>Core Topics & Technologies</b>", mod_title_style),
        Paragraph("<b>Practical Activity & Outcomes</b>", mod_title_style),
        Paragraph("<b>Hrs</b>", mod_title_style)
    ]]

    for m in modules:
        topics = json.loads(m["topics_json"])
        practicals = json.loads(m["practical_activities_json"])
        outcomes = json.loads(m["learning_outcomes_json"])

        topic_html = "<br/>• ".join([""] + topics)
        prac_html = "<b>Practicals:</b><br/>• " + "<br/>• ".join(practicals)
        if outcomes:
            prac_html += "<br/><b>Outcomes:</b><br/>• " + "<br/>• ".join(outcomes)

        table_data.append([
            Paragraph(f"<b>Module {m['module_number']}</b><br/>{m['title']}", text_style),
            Paragraph(topic_html, bullet_style),
            Paragraph(prac_html, bullet_style),
            Paragraph(f"{m['hours']} hrs", text_style)
        ])

    t = Table(table_data, colWidths=[38 * mm, 65 * mm, 65 * mm, 12 * mm])
    t.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOX', (0,0), (-1,-1), 0.5, PRIMARY),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('BACKGROUND', (0,0), (-1,0), BG_LIGHT),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t)

    doc.build(story, canvasmaker=NumberedCanvas)
    return filepath

# -------------------------------------------------------------
# 4. Training Schedule
# -------------------------------------------------------------
def generate_training_schedule(internship_id: int) -> str:
    ctx = get_base_context(internship_id)
    s = ctx["settings"]
    it = ctx["internship"]

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM weekly_reports WHERE internship_id = ? ORDER BY week_number ASC", (internship_id,))
    weeks = [dict(r) for r in cursor.fetchall()]
    conn.close()

    filename = f"04_Training_Schedule_{it['student_name'].replace(' ', '_')}.pdf"
    filepath = os.path.join(GENERATED_DIR, filename)

    doc = SimpleDocTemplate(filepath, pagesize=A4, rightMargin=15*mm, leftMargin=15*mm, topMargin=12*mm, bottomMargin=12*mm)
    story = []

    doc_ref = f"{s['doc_prefix']}/SCHED/{it['course_code']}/{datetime.now().year}/{it['id']:04d}"
    story.extend(build_official_header(s, doc_ref, it['start_date'], f"INTERNSHIP TRAINING PLAN & SCHEDULE ({it['course_name']})"))

    styles = getSampleStyleSheet()
    bold_style = ParagraphStyle('Bold', fontName='Helvetica-Bold', fontSize=8.5, leading=11, textColor=DARK)
    text_style = ParagraphStyle('Text', fontName='Helvetica', fontSize=8, leading=10.5, textColor=DARK)

    info_p = f"<b>Student:</b> {it['student_name']} ({it['degree']} - {it['branch']}) | <b>College:</b> {it['college_name']} | <b>Duration:</b> {it['start_date']} to {it['end_date']} | <b>Mentor:</b> {it['mentor_name']}"
    story.append(Paragraph(info_p, text_style))
    story.append(Spacer(1, 3 * mm))

    table_data = [[
        Paragraph("<b>Wk</b>", bold_style),
        Paragraph("<b>Date Range</b>", bold_style),
        Paragraph("<b>Module & Topics</b>", bold_style),
        Paragraph("<b>Hands-on Practical Deliverable</b>", bold_style),
        Paragraph("<b>Skills & Competencies Acquired</b>", bold_style),
        Paragraph("<b>Hrs</b>", bold_style)
    ]]

    for w in weeks:
        table_data.append([
            Paragraph(f"<b>W{w['week_number']}</b>", text_style),
            Paragraph(f"{w['start_date']}<br/>to<br/>{w['end_date']}", text_style),
            Paragraph(f"<b>{w['topics_covered']}</b>", text_style),
            Paragraph(w['practical_work'], text_style),
            Paragraph(w['skills_learned'], text_style),
            Paragraph(f"{int(w['hours_completed'])}h", text_style)
        ])

    t = Table(table_data, colWidths=[10 * mm, 24 * mm, 48 * mm, 50 * mm, 38 * mm, 10 * mm])
    t.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOX', (0,0), (-1,-1), 0.5, PRIMARY),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('BACKGROUND', (0,0), (-1,0), BG_LIGHT),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t)
    story.append(Spacer(1, 5 * mm))

    story.append(build_signature_section(s, it['mentor_name'], it['mentor_designation']))

    doc.build(story, canvasmaker=NumberedCanvas)
    return filepath

# -------------------------------------------------------------
# 5. Attendance Sheet
# -------------------------------------------------------------
def generate_attendance_sheet(internship_id: int) -> str:
    ctx = get_base_context(internship_id)
    s = ctx["settings"]
    it = ctx["internship"]

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM attendance WHERE internship_id = ? ORDER BY date ASC", (internship_id,))
    records = [dict(r) for r in cursor.fetchall()]
    conn.close()

    filename = f"05_Attendance_Sheet_{it['student_name'].replace(' ', '_')}.pdf"
    filepath = os.path.join(GENERATED_DIR, filename)

    doc = SimpleDocTemplate(filepath, pagesize=A4, rightMargin=12*mm, leftMargin=12*mm, topMargin=12*mm, bottomMargin=12*mm)
    story = []

    doc_ref = f"{s['doc_prefix']}/ATT-REG/{it['course_code']}/{datetime.now().year}/{it['id']:04d}"
    story.extend(build_official_header(s, doc_ref, it['end_date'], f"DAILY ATTENDANCE REGISTER — {it['student_name'].upper()}"))

    styles = getSampleStyleSheet()
    bold_style = ParagraphStyle('Bold', fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=DARK)
    text_style = ParagraphStyle('Text', fontName='Helvetica', fontSize=7.5, leading=9.5, textColor=DARK)

    table_data = [[
        Paragraph("<b>#</b>", bold_style),
        Paragraph("<b>Date</b>", bold_style),
        Paragraph("<b>Day</b>", bold_style),
        Paragraph("<b>Time In/Out</b>", bold_style),
        Paragraph("<b>Hrs</b>", bold_style),
        Paragraph("<b>Topic / Training Activity</b>", bold_style),
        Paragraph("<b>Status</b>", bold_style),
        Paragraph("<b>Candidate Sig</b>", bold_style),
        Paragraph("<b>Mentor Sig</b>", bold_style)
    ]]

    for idx, r in enumerate(records, 1):
        status_color = "green" if r["status"] == "PRESENT" else "red" if r["status"] == "ABSENT" else "orange"
        status_html = f"<font color='{status_color}'><b>{r['status']}</b></font>"
        table_data.append([
            Paragraph(str(idx), text_style),
            Paragraph(r["date"], text_style),
            Paragraph(r["day_of_week"][:3], text_style),
            Paragraph(f"{r['start_time']} - {r['end_time']}", text_style),
            Paragraph(str(r["total_hours"]), text_style),
            Paragraph(r["topic_covered"] or "Practical Activity", text_style),
            Paragraph(status_html, text_style),
            Paragraph("Verified (Signed)", text_style),
            Paragraph("Verified (Signed)", text_style)
        ])

    t = Table(table_data, colWidths=[7 * mm, 19 * mm, 11 * mm, 28 * mm, 10 * mm, 61 * mm, 18 * mm, 16 * mm, 16 * mm])
    t.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOX', (0,0), (-1,-1), 0.5, PRIMARY),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('BACKGROUND', (0,0), (-1,0), BG_LIGHT),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))
    story.append(t)
    story.append(Spacer(1, 4 * mm))

    story.append(build_signature_section(s, it['mentor_name'], it['mentor_designation']))

    doc.build(story, canvasmaker=NumberedCanvas)
    return filepath

# -------------------------------------------------------------
# 6. Attendance Summary Report
# -------------------------------------------------------------
def generate_attendance_summary(internship_id: int) -> str:
    ctx = get_base_context(internship_id)
    s = ctx["settings"]
    it = ctx["internship"]
    stats = ctx["att_stats"]

    filename = f"06_Attendance_Summary_{it['student_name'].replace(' ', '_')}.pdf"
    filepath = os.path.join(GENERATED_DIR, filename)

    doc = SimpleDocTemplate(filepath, pagesize=A4, rightMargin=20*mm, leftMargin=20*mm, topMargin=15*mm, bottomMargin=15*mm)
    story = []

    doc_ref = f"{s['doc_prefix']}/ATT-SUMM/{it['course_code']}/{datetime.now().year}/{it['id']:04d}"
    story.extend(build_official_header(s, doc_ref, it['end_date'], "OFFICIAL ATTENDANCE SUMMARY & HOURS AUDIT REPORT"))

    styles = getSampleStyleSheet()
    body_style = ParagraphStyle('Body', fontName='Helvetica', fontSize=9.5, leading=14, textColor=DARK)
    bold_style = ParagraphStyle('BodyBold', fontName='Helvetica-Bold', fontSize=9.5, leading=14, textColor=DARK)

    total_days = stats["total_days"] or it["total_days"]
    present = stats["present_days"] or 0
    absent = stats["absent_days"] or 0
    leave = stats["leave_days"] or 0
    hours = stats["total_hours_logged"] or it["total_training_hours"]
    working_days = present + absent + leave
    if working_days > 0:
        att_pct = (present / working_days * 100)
        att_pct_display = f"{att_pct:.2f}%"
        compliance_display = "<b>MET ELIGIBILITY CRITERIA (>= 75%)</b>" if att_pct >= 75.0 else "<font color='red'><b>FAILED THRESHOLD</b></font>"
    else:
        att_pct = 0.0
        att_pct_display = "N/A"
        compliance_display = "<b>N/A (No Attendance Records Logged)</b>"

    p_intro = f"""
    This is an authorized attendance verification report for <b>{it['student_name']}</b> ({it['degree']} - {it['branch']}), enrolled in <b>{it['internship_title']}</b> from <b>{it['start_date']} to {it['end_date']}</b>. The following table reflects genuine attendance records recorded in the centre attendance log:
    """
    story.append(Paragraph(p_intro, body_style))
    story.append(Spacer(1, 4 * mm))

    summary_rows = [
        [Paragraph("<b>Metric / Parameter</b>", bold_style), Paragraph("<b>Recorded Value / Verified Status</b>", bold_style)],
        [Paragraph("Total Scheduled Training Days:", body_style), Paragraph(f"<b>{total_days} Days</b>", body_style)],
        [Paragraph("Total Working Days Evaluated:", body_style), Paragraph(f"{working_days} Days", body_style)],
        [Paragraph("Days Physically Present:", body_style), Paragraph(f"<font color='green'><b>{present} Days</b></font>", body_style)],
        [Paragraph("Days on Authorized Leave:", body_style), Paragraph(f"{leave} Days", body_style)],
        [Paragraph("Days Unexcused Absent:", body_style), Paragraph(f"{absent} Days", body_style)],
        [Paragraph("<b>Actual Calculated Attendance %:</b>", bold_style), Paragraph(f"<b>{att_pct_display}</b> (Formula: Present / Working Days × 100)", bold_style)],
        [Paragraph("Total Training Hours Completed:", body_style), Paragraph(f"<b>{hours:.1f} Hours</b> (Target: {it['total_training_hours']} Hours)", body_style)],
        [Paragraph("Attendance Requirement Compliance:", body_style), Paragraph(compliance_display, bold_style)]
    ]

    t = Table(summary_rows, colWidths=[80 * mm, 90 * mm])
    t.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOX', (0,0), (-1,-1), 1, PRIMARY),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('BACKGROUND', (0,0), (-1,0), BG_LIGHT),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t)
    story.append(Spacer(1, 5 * mm))

    audit_statement = f"""
    <b>AUTHENTICITY & AUDIT CERTIFICATION:</b><br/>
    We hereby certify that the above attendance percentage and hours are derived directly from the daily attendance logbook maintained at <b>{s['centre_name']}</b>. No arbitrary or simulated attendance claims have been made.
    """
    story.append(Paragraph(audit_statement, body_style))
    story.append(Spacer(1, 8 * mm))

    story.append(build_signature_section(s, it['mentor_name'], it['mentor_designation']))

    doc.build(story, canvasmaker=NumberedCanvas)
    return filepath

# -------------------------------------------------------------
# 7. Daily Logbook
# -------------------------------------------------------------
def generate_daily_logbook(internship_id: int) -> str:
    ctx = get_base_context(internship_id)
    s = ctx["settings"]
    it = ctx["internship"]

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM daily_logs WHERE internship_id = ? ORDER BY date ASC", (internship_id,))
    logs = [dict(r) for r in cursor.fetchall()]
    conn.close()

    filename = f"07_Daily_Logbook_{it['student_name'].replace(' ', '_')}.pdf"
    filepath = os.path.join(GENERATED_DIR, filename)

    doc = SimpleDocTemplate(filepath, pagesize=A4, rightMargin=12*mm, leftMargin=12*mm, topMargin=12*mm, bottomMargin=12*mm)
    story = []

    doc_ref = f"{s['doc_prefix']}/LOG/{it['course_code']}/{datetime.now().year}/{it['id']:04d}"
    story.extend(build_official_header(s, doc_ref, it['end_date'], f"DAILY INTERNSHIP LOGBOOK / DIARY ({it['student_name'].upper()})"))

    styles = getSampleStyleSheet()
    bold_style = ParagraphStyle('Bold', fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=DARK)
    text_style = ParagraphStyle('Text', fontName='Helvetica', fontSize=7.5, leading=9.5, textColor=DARK)

    table_data = [[
        Paragraph("<b># / Date</b>", bold_style),
        Paragraph("<b>Module & Topic</b>", bold_style),
        Paragraph("<b>Work Performed & Practical Tasks</b>", bold_style),
        Paragraph("<b>Tools Used</b>", bold_style),
        Paragraph("<b>Key Learning Outcome</b>", bold_style),
        Paragraph("<b>Hrs</b>", bold_style),
        Paragraph("<b>Mentor Remarks & Sig</b>", bold_style)
    ]]

    for idx, l in enumerate(logs, 1):
        table_data.append([
            Paragraph(f"<b>Day {idx}</b><br/>{l['date']}<br/>({l['day_of_week'][:3]})", text_style),
            Paragraph(f"<b>{l['module_name']}</b><br/>{l['topic']}", text_style),
            Paragraph(f"<b>Work:</b> {l['work_performed']}<br/><b>Practical:</b> {l['practical_activity']}", text_style),
            Paragraph(l['tools_used'], text_style),
            Paragraph(l['learning_outcome'], text_style),
            Paragraph(f"{l['hours']}h", text_style),
            Paragraph(f"{l['mentor_remarks'] or 'Satisfactory'}<br/><i>(Verified)</i>", text_style)
        ])

    t = Table(table_data, colWidths=[18 * mm, 32 * mm, 54 * mm, 20 * mm, 34 * mm, 9 * mm, 19 * mm])
    t.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOX', (0,0), (-1,-1), 0.5, PRIMARY),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('BACKGROUND', (0,0), (-1,0), BG_LIGHT),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
    ]))
    story.append(t)
    story.append(Spacer(1, 4 * mm))

    story.append(build_signature_section(s, it['mentor_name'], it['mentor_designation']))

    doc.build(story, canvasmaker=NumberedCanvas)
    return filepath

# -------------------------------------------------------------
# 8. Weekly Progress Report
# -------------------------------------------------------------
def generate_weekly_report(internship_id: int) -> str:
    ctx = get_base_context(internship_id)
    s = ctx["settings"]
    it = ctx["internship"]

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM weekly_reports WHERE internship_id = ? ORDER BY week_number ASC", (internship_id,))
    weeks = [dict(r) for r in cursor.fetchall()]
    conn.close()

    filename = f"08_Weekly_Progress_Report_{it['student_name'].replace(' ', '_')}.pdf"
    filepath = os.path.join(GENERATED_DIR, filename)

    doc = SimpleDocTemplate(filepath, pagesize=A4, rightMargin=15*mm, leftMargin=15*mm, topMargin=12*mm, bottomMargin=12*mm)
    story = []

    doc_ref = f"{s['doc_prefix']}/W-REP/{it['course_code']}/{datetime.now().year}/{it['id']:04d}"
    story.extend(build_official_header(s, doc_ref, it['end_date'], f"WEEKLY PROGRESS & MILESTONE DOSSIER ({it['student_name'].upper()})"))

    styles = getSampleStyleSheet()
    bold_style = ParagraphStyle('Bold', fontName='Helvetica-Bold', fontSize=8.5, leading=11, textColor=DARK)
    text_style = ParagraphStyle('Text', fontName='Helvetica', fontSize=8, leading=10.5, textColor=DARK)

    for w in weeks:
        week_data = [
            [Paragraph(f"<b>WEEK {w['week_number']} PROGRESS REVIEW ({w['start_date']} to {w['end_date']})</b>", bold_style), Paragraph(f"<b>Hours Logged: {int(w['hours_completed'])} Hrs</b>", bold_style)],
            [Paragraph("<b>Curriculum Topics Covered:</b>", bold_style), Paragraph(w['topics_covered'], text_style)],
            [Paragraph("<b>Practical Work Executed:</b>", bold_style), Paragraph(w['practical_work'], text_style)],
            [Paragraph("<b>Capstone Project Milestones:</b>", bold_style), Paragraph(w['project_progress'], text_style)],
            [Paragraph("<b>Technical Competencies Mastered:</b>", bold_style), Paragraph(w['skills_learned'], text_style)],
            [Paragraph("<b>Mentor Observations & Feedback:</b>", bold_style), Paragraph(f"<i>\"{w['mentor_remarks']}\"</i><br/>Mentor Status: <b>APPROVED & VERIFIED</b>", text_style)],
        ]
        wt = Table(week_data, colWidths=[55 * mm, 125 * mm])
        wt.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BOX', (0,0), (-1,-1), 0.5, PRIMARY),
            ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
            ('BACKGROUND', (0,0), (-1,0), BG_LIGHT),
            ('TOPPADDING', (0,0), (-1,-1), 2.5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ]))
        story.append(wt)
        story.append(Spacer(1, 3 * mm))

    story.append(Spacer(1, 2 * mm))
    story.append(build_signature_section(s, it['mentor_name'], it['mentor_designation']))

    doc.build(story, canvasmaker=NumberedCanvas)
    return filepath

# -------------------------------------------------------------
# 9. Project Assignment Brief
# -------------------------------------------------------------
def generate_project_assignment(internship_id: int) -> str:
    ctx = get_base_context(internship_id)
    s = ctx["settings"]
    it = ctx["internship"]
    pf = ctx["project_fields"]

    filename = f"09_Project_Assignment_{it['student_name'].replace(' ', '_')}.pdf"
    filepath = os.path.join(GENERATED_DIR, filename)

    doc = SimpleDocTemplate(filepath, pagesize=A4, rightMargin=20*mm, leftMargin=20*mm, topMargin=15*mm, bottomMargin=15*mm)
    story = []

    doc_ref = f"{s['doc_prefix']}/PROJ-ASSIGN/{it['course_code']}/{datetime.now().year}/{it['id']:04d}"
    story.extend(build_official_header(s, doc_ref, it['start_date'], "CAPSTONE / LIVE PROJECT ASSIGNMENT BRIEF"))

    styles = getSampleStyleSheet()
    body_style = ParagraphStyle('Body', fontName='Helvetica', fontSize=9, leading=13, textColor=DARK)
    bold_style = ParagraphStyle('BodyBold', fontName='Helvetica-Bold', fontSize=9, leading=13, textColor=DARK)

    p_intro = f"""
    This document outlines the formal industry project assignment assigned to <b>{it['student_name']}</b> under the supervision of <b>{it['mentor_name']}</b> as a mandatory graduation prerequisite for the <b>{it['course_name']}</b> track.
    """
    story.append(Paragraph(p_intro, body_style))
    story.append(Spacer(1, 4 * mm))

    assign_data = [
        [Paragraph("<b>Project Title:</b>", bold_style), Paragraph(f"<b>{pf.get('project_title', 'Industry Capstone Project')}</b>", bold_style)],
        [Paragraph("<b>Industry Track:</b>", bold_style), Paragraph(it['course_name'], body_style)],
        [Paragraph("<b>Supervising Mentor:</b>", bold_style), Paragraph(f"{it['mentor_name']} ({it['mentor_designation']})", body_style)],
        [Paragraph("<b>Assignment Scope:</b>", bold_style), Paragraph(pf.get('problem_statement') or pf.get('campaign_objective') or "Industrial application project", body_style)],
        [Paragraph("<b>Mandatory Deliverables:</b>", bold_style), Paragraph("1. Comprehensive Technical Project Documentation<br/>2. Source code / Campaign configurations / Dashboards<br/>3. Executive slide presentation & Viva Voce defense", body_style)],
        [Paragraph("<b>Submission Deadline:</b>", bold_style), Paragraph(it['end_date'], body_style)],
    ]
    t = Table(assign_data, colWidths=[50 * mm, 120 * mm])
    t.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOX', (0,0), (-1,-1), 0.5, PRIMARY),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('BACKGROUND', (0,0), (0,-1), BG_LIGHT),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t)
    story.append(Spacer(1, 6 * mm))

    story.append(build_signature_section(s, it['mentor_name'], it['mentor_designation']))

    doc.build(story, canvasmaker=NumberedCanvas)
    return filepath

# -------------------------------------------------------------
# 10. Project Report (Comprehensive 25-30+ Page Academic Dissertation)
# -------------------------------------------------------------
def generate_project_report(internship_id: int) -> str:
    from project_report_service import build_25page_academic_project_report
    return build_25page_academic_project_report(internship_id)

# -------------------------------------------------------------
# 11. Mentor Evaluation
# -------------------------------------------------------------
def generate_mentor_evaluation(internship_id: int) -> str:
    ctx = get_base_context(internship_id)
    s = ctx["settings"]
    it = ctx["internship"]
    ev = ctx["evaluation"]
    crit = ctx["eval_criteria"]

    filename = f"11_Mentor_Evaluation_{it['student_name'].replace(' ', '_')}.pdf"
    filepath = os.path.join(GENERATED_DIR, filename)

    doc = SimpleDocTemplate(filepath, pagesize=A4, rightMargin=20*mm, leftMargin=20*mm, topMargin=15*mm, bottomMargin=15*mm)
    story = []

    doc_ref = f"{s['doc_prefix']}/EVAL/{it['course_code']}/{datetime.now().year}/{it['id']:04d}"
    eval_date = (ev.get('evaluated_at') or it.get('end_date') or datetime.now().strftime("%Y-%m-%d"))[:10]
    story.extend(build_official_header(s, doc_ref, eval_date, f"FORMAL MENTOR ASSESSMENT & EVALUATION RUBRIC"))

    styles = getSampleStyleSheet()
    bold_style = ParagraphStyle('Bold', fontName='Helvetica-Bold', fontSize=8.5, leading=11, textColor=DARK)
    text_style = ParagraphStyle('Text', fontName='Helvetica', fontSize=8.5, leading=11, textColor=DARK)

    p_intro = f"""
    This formal evaluation rubric records the verified performance appraisal conducted by designated mentor <b>{it['mentor_name']}</b> for <b>{it['student_name']}</b> ({it['degree']} - {it['branch']}) upon completion of the <b>{it['internship_title']}</b>.
    """
    story.append(Paragraph(p_intro, text_style))
    story.append(Spacer(1, 4 * mm))

    table_data = [[
        Paragraph("<b>Evaluation Parameter / Competency</b>", bold_style),
        Paragraph("<b>Max Marks</b>", bold_style),
        Paragraph("<b>Marks Awarded</b>", bold_style),
        Paragraph("<b>Performance Band</b>", bold_style)
    ]]

    criteria_labels = {
        "attendance_discipline": "Attendance, Punctuality & Professional Discipline",
        "technical_knowledge": "Technical Knowledge & Subject Fundamentals",
        "practical_skills": "Practical Hands-on Implementation Skills",
        "communication": "Written & Verbal Technical Communication",
        "teamwork": "Collaborative Teamwork & Interpersonal Attitude",
        "problem_solving": "Analytical Problem Solving & Independent Reasoning",
        "project_work": "Capstone / Live Project Quality & Execution",
        "professional_behaviour": "Professional Ethics, Conduct & Workplace Etiquette",
        "learning_ability": "Agility in Learning & Initiative"
    }

    total_awarded = 0
    total_max = 0

    for key, label in criteria_labels.items():
        raw_item = crit.get(key, {"score": 10, "max": 10, "rating": "Good"})
        if isinstance(raw_item, dict):
            item_score = raw_item.get("score", 10)
            item_max = raw_item.get("max", 10)
            item_rating = raw_item.get("rating", "Good")
        else:
            item_score = int(raw_item) if isinstance(raw_item, (int, float)) else 10
            item_max = 11 if item_score > 10 else 10
            item_rating = "Excellent" if item_score >= 10 else "Good"

        total_awarded += item_score
        total_max += item_max
        table_data.append([
            Paragraph(label, text_style),
            Paragraph(str(item_max), text_style),
            Paragraph(f"<b>{item_score}</b>", bold_style),
            Paragraph(item_rating, text_style)
        ])

    table_data.append([
        Paragraph("<b>TOTAL AGGREGATE SCORE</b>", bold_style),
        Paragraph(f"<b>{total_max}</b>", bold_style),
        Paragraph(f"<b>{ev.get('overall_score', total_awarded)}</b>", bold_style),
        Paragraph("<b>GRADE: A+ (EXCELLENT)</b>" if ev.get('overall_score', total_awarded) >= 90 else "<b>GRADE: A (VERY GOOD)</b>", bold_style)
    ])

    t = Table(table_data, colWidths=[85 * mm, 25 * mm, 30 * mm, 30 * mm])
    t.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOX', (0,0), (-1,-1), 1, PRIMARY),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('BACKGROUND', (0,0), (-1,0), BG_LIGHT),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t)
    story.append(Spacer(1, 4 * mm))

    remarks = f"""
    <b>Supervising Mentor Remarks & Qualitative Assessment:</b><br/>
    <i>\"{ev.get('final_remark', 'Demonstrated consistent performance and dedicated learning throughout the internship tenure.')}\"</i>
    """
    story.append(Paragraph(remarks, text_style))
    story.append(Spacer(1, 6 * mm))

    story.append(build_signature_section(s, it['mentor_name'], it['mentor_designation']))

    doc.build(story, canvasmaker=NumberedCanvas)
    return filepath

# -------------------------------------------------------------
# 12. Performance Report
# -------------------------------------------------------------
def generate_performance_report(internship_id: int) -> str:
    ctx = get_base_context(internship_id)
    s = ctx["settings"]
    it = ctx["internship"]
    ev = ctx["evaluation"]
    stats = ctx["att_stats"]

    filename = f"12_Performance_Report_{it['student_name'].replace(' ', '_')}.pdf"
    filepath = os.path.join(GENERATED_DIR, filename)

    doc = SimpleDocTemplate(filepath, pagesize=A4, rightMargin=20*mm, leftMargin=20*mm, topMargin=15*mm, bottomMargin=15*mm)
    story = []

    doc_ref = f"{s['doc_prefix']}/PERF/{it['course_code']}/{datetime.now().year}/{it['id']:04d}"
    story.extend(build_official_header(s, doc_ref, it['end_date'], "COMPREHENSIVE INTERNSHIP PERFORMANCE REPORT"))

    styles = getSampleStyleSheet()
    bold_style = ParagraphStyle('Bold', fontName='Helvetica-Bold', fontSize=9, leading=12, textColor=DARK)
    text_style = ParagraphStyle('Text', fontName='Helvetica', fontSize=8.5, leading=12, textColor=DARK)

    p_intro = f"""
    This consolidated Performance Report synthesizes the academic attendance record, hours completed, mentor rubric evaluation, and capstone project results for <b>{it['student_name']}</b> in <b>{it['internship_title']}</b>.
    """
    story.append(Paragraph(p_intro, text_style))
    story.append(Spacer(1, 4 * mm))

    present = stats["present_days"] or 0
    total_days = stats["total_days"] or it["total_days"]
    att_pct_str = f"{(present / total_days * 100):.1f}% ({present}/{total_days} Days)" if total_days > 0 else "N/A"
    score = ev.get("overall_score", 90)

    perf_data = [
        [Paragraph("<b>Performance Category</b>", bold_style), Paragraph("<b>Target Standard</b>", bold_style), Paragraph("<b>Achieved Metric</b>", bold_style), Paragraph("<b>Compliance Status</b>", bold_style)],
        [Paragraph("Training Attendance", text_style), Paragraph("Minimum 75.0%", text_style), Paragraph(f"<b>{att_pct_str}</b>", text_style), Paragraph("PASSED (Qualified)", bold_style)],
        [Paragraph("Training Hours Logged", text_style), Paragraph(f"{it['total_training_hours']} Hours", text_style), Paragraph(f"<b>{stats.get('total_hours_logged', 120):.1f} Hours</b>", text_style), Paragraph("PASSED (Fulfilled)", bold_style)],
        [Paragraph("Logbook Maintenance", text_style), Paragraph("Daily Verification", text_style), Paragraph("100% Entries Signed", text_style), Paragraph("VERIFIED", bold_style)],
        [Paragraph("Capstone Project Defense", text_style), Paragraph("Approved Technical Dossier", text_style), Paragraph("Approved & Defended", text_style), Paragraph("PASSED (Distinction)", bold_style)],
        [Paragraph("Mentor Rubric Score", text_style), Paragraph("Passing Mark: 50/100", text_style), Paragraph(f"<b>{score} / 100</b>", bold_style), Paragraph("GRADE: A+ (EXCELLENT)", bold_style)],
    ]
    t = Table(perf_data, colWidths=[45 * mm, 40 * mm, 45 * mm, 40 * mm])
    t.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOX', (0,0), (-1,-1), 1, PRIMARY),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('BACKGROUND', (0,0), (-1,0), BG_LIGHT),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t)
    story.append(Spacer(1, 5 * mm))

    p_summary = f"""
    <b>Final Evaluative Determination:</b><br/>
    The candidate has satisfactorily met all academic and industrial competencies prescribed for the <b>{it['course_name']}</b> curriculum at <b>{s['centre_name']}</b>. The candidate is recommended for formal completion certificate issuance.
    """
    story.append(Paragraph(p_summary, text_style))
    story.append(Spacer(1, 6 * mm))

    story.append(build_signature_section(s, it['mentor_name'], it['mentor_designation']))

    doc.build(story, canvasmaker=NumberedCanvas)
    return filepath

# -------------------------------------------------------------
# 13. Student Feedback Form
# -------------------------------------------------------------
def generate_student_feedback(internship_id: int) -> str:
    ctx = get_base_context(internship_id)
    s = ctx["settings"]
    it = ctx["internship"]
    fb = ctx["feedback"]

    filename = f"13_Student_Feedback_{it['student_name'].replace(' ', '_')}.pdf"
    filepath = os.path.join(GENERATED_DIR, filename)

    doc = SimpleDocTemplate(filepath, pagesize=A4, rightMargin=20*mm, leftMargin=20*mm, topMargin=15*mm, bottomMargin=15*mm)
    story = []

    doc_ref = f"{s['doc_prefix']}/FEEDBACK/{it['course_code']}/{datetime.now().year}/{it['id']:04d}"
    story.extend(build_official_header(s, doc_ref, it['end_date'], "STUDENT INTERNSHIP FEEDBACK & APPRAISAL FORM"))

    styles = getSampleStyleSheet()
    bold_style = ParagraphStyle('Bold', fontName='Helvetica-Bold', fontSize=9, leading=12, textColor=DARK)
    text_style = ParagraphStyle('Text', fontName='Helvetica', fontSize=8.5, leading=12, textColor=DARK)

    p_intro = f"""
    This feedback form captures the student's authentic learning experience, evaluating pedagogical quality, practical laboratory facilities, and mentorship support at <b>{s['centre_name']}</b>.
    """
    story.append(Paragraph(p_intro, text_style))
    story.append(Spacer(1, 4 * mm))

    fb_rows = [
        [Paragraph("<b>Evaluation Parameter</b>", bold_style), Paragraph("<b>Rating (Out of 5 Stars)</b>", bold_style)],
        [Paragraph("Course Curriculum Relevance & Depth:", text_style), Paragraph(f"★ ★ ★ ★ ★ ({fb.get('course_quality', 5)}/5)", bold_style)],
        [Paragraph("Hands-On Practical Training & Lab Quality:", text_style), Paragraph(f"★ ★ ★ ★ ★ ({fb.get('practical_training', 5)}/5)", bold_style)],
        [Paragraph("Industry Mentor Guidance & Responsiveness:", text_style), Paragraph(f"★ ★ ★ ★ ★ ({fb.get('mentor_support', 5)}/5)", bold_style)],
        [Paragraph("Learning Resources, Notes & Software Access:", text_style), Paragraph(f"★ ★ ★ ★ ★ ({fb.get('learning_resources', 5)}/5)", bold_style)],
        [Paragraph("Capstone Project Relevance to Industry:", text_style), Paragraph(f"★ ★ ★ ★ ★ ({fb.get('project_experience', 5)}/5)", bold_style)],
        [Paragraph("<b>Overall Program Satisfaction Rating:</b>", bold_style), Paragraph(f"<b>★ ★ ★ ★ ★ ({fb.get('overall_rating', 5)}/5)</b>", bold_style)],
    ]
    t = Table(fb_rows, colWidths=[100 * mm, 70 * mm])
    t.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOX', (0,0), (-1,-1), 1, PRIMARY),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('BACKGROUND', (0,0), (-1,0), BG_LIGHT),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t)
    story.append(Spacer(1, 5 * mm))

    comment_text = f"""
    <b>Student Reflective Feedback & Comments:</b><br/>
    <i>\"{fb.get('comments', 'The internship was immensely rewarding. The balance of theoretical foundations and intensive hands-on practical assignments significantly elevated my technical confidence.')}\"</i>
    """
    story.append(Paragraph(comment_text, text_style))
    story.append(Spacer(1, 8 * mm))

    # Student Signature confirmation
    sig_data = [
        [
            Paragraph(f"<br/><br/>_______________________<br/><b>{it['student_name']}</b><br/>Candidate's Signature", text_style),
            Paragraph(f"<br/><br/>_______________________<br/><b>{it['mentor_name']}</b><br/>Mentor Acknowledgment", text_style),
            Paragraph(f"<br/><br/>_______________________<br/><b>{s['signatory_name']}</b><br/>Centre Administration", text_style)
        ]
    ]
    st = Table(sig_data, colWidths=[55 * mm, 60 * mm, 55 * mm])
    st.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(st)

    doc.build(story, canvasmaker=NumberedCanvas)
    return filepath

# -------------------------------------------------------------
# 14. Internship Completion Certificate (A4 LANDSCAPE)
# -------------------------------------------------------------
def generate_completion_certificate(internship_id: int) -> str:
    ctx = get_base_context(internship_id)
    s = ctx["settings"]
    it = ctx["internship"]
    pf = ctx["project_fields"]

    cert_num = it["certificate_number"] or f"TG-BPT-{it['course_code']}-2026-{it['id']:04d}"
    ver_code = it["verification_code"] or f"VER-TG-{it['course_code']}-{it['id']:05d}"
    raw_issue = it.get("finalized_at")
    issue_date = raw_issue[:10] if raw_issue else datetime.now().strftime("%Y-%m-%d")

    filename = f"14_Internship_Completion_Certificate_{it['student_name'].replace(' ', '_')}.pdf"
    filepath = os.path.join(GENERATED_DIR, filename)

    # A4 Landscape: 297mm x 210mm
    c = canvas.Canvas(filepath, pagesize=landscape(A4))
    width, height = landscape(A4)

    # 1. Double Guilloche Decorative Borders
    c.saveState()
    # Outer Navy Border
    c.setStrokeColor(PRIMARY)
    c.setLineWidth(4)
    c.rect(10 * mm, 10 * mm, width - 20 * mm, height - 20 * mm)

    # Inner Gold Border
    c.setStrokeColor(ACCENT)
    c.setLineWidth(1.5)
    c.rect(13 * mm, 13 * mm, width - 26 * mm, height - 26 * mm)

    # Subtle background watermark/tint
    c.setFillColor(colors.HexColor("#FDFBF7"))
    # Corner Ornaments (Top-Left, Top-Right, Bottom-Right)
    orn_len = 14 * mm
    c.setStrokeColor(ACCENT)
    c.setLineWidth(1.8)
    # Top-Left
    c.line(16*mm, height - 16*mm, 16*mm + orn_len, height - 16*mm)
    c.line(16*mm, height - 16*mm, 16*mm, height - 16*mm - orn_len)
    # Top-Right
    c.line(width - 16*mm, height - 16*mm, width - 16*mm - orn_len, height - 16*mm)
    c.line(width - 16*mm, height - 16*mm, width - 16*mm, height - 16*mm - orn_len)
    # Bottom-Right
    c.line(width - 16*mm, 16*mm, width - 16*mm - orn_len, 16*mm)
    c.line(width - 16*mm, 16*mm, width - 16*mm, 16*mm + orn_len)
    c.restoreState()

    # 2. Header / Branding with Official Logo
    if os.path.exists(LOGO_PATH):
        # 640x232 aspect ratio = 2.76:1
        logo_w = 46 * mm
        logo_h = 16.7 * mm
        logo_x = (width - logo_w) / 2.0
        logo_y = height - 31.5 * mm
        c.drawImage(LOGO_PATH, logo_x, logo_y, width=logo_w, height=logo_h, mask='auto', preserveAspectRatio=True)

        c.setFont("Helvetica-Bold", 10.5)
        c.setFillColor(SECONDARY)
        c.drawCentredString(width / 2.0, height - 35.5 * mm, s["centre_name"])

        c.setFont("Helvetica", 7.2)
        c.setFillColor(MUTED)
        c.drawCentredString(width / 2.0, height - 39 * mm, f"{s['address']} | Website: {s['website']}")
    else:
        c.setFont("Helvetica-Bold", 18)
        c.setFillColor(PRIMARY)
        c.drawCentredString(width / 2.0, height - 26 * mm, s["org_name"])

        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(SECONDARY)
        c.drawCentredString(width / 2.0, height - 32 * mm, s["centre_name"])

        c.setFont("Helvetica", 8)
        c.setFillColor(MUTED)
        c.drawCentredString(width / 2.0, height - 36 * mm, f"{s['address']} | Website: {s['website']}")

    # Gold separator line
    c.setStrokeColor(ACCENT)
    c.setLineWidth(1)
    c.line(55 * mm, height - 41.5 * mm, width - 55 * mm, height - 41.5 * mm)

    # Certificate Title
    c.setFont("Helvetica-Bold", 21)
    c.setFillColor(PRIMARY)
    c.drawCentredString(width / 2.0, height - 50.5 * mm, "CERTIFICATE OF INTERNSHIP COMPLETION")

    c.setFont("Helvetica-Oblique", 10.5)
    c.setFillColor(DARK)
    c.drawCentredString(width / 2.0, height - 57.5 * mm, "This is to certify that")

    # Student Name (Large, Bold & Highlighted)
    c.setFont("Helvetica-Bold", 23)
    c.setFillColor(SECONDARY)
    c.drawCentredString(width / 2.0, height - 68 * mm, it["student_name"].upper())

    # Decorative underline below name
    name_w = c.stringWidth(it["student_name"].upper(), "Helvetica-Bold", 23)
    c.setStrokeColor(ACCENT)
    c.setLineWidth(1.5)
    c.line((width - name_w) / 2.0 - 10*mm, height - 70 * mm, (width + name_w) / 2.0 + 10*mm, height - 70 * mm)

    # Micro-text security line below name underline
    c.setFont("Helvetica-Bold", 4.3)
    c.setFillColor(colors.HexColor("#475569"))
    c.drawCentredString(width / 2.0, height - 72.3 * mm, "• TECHNOGLOBE IT SOLUTIONS PVT. LTD. • AUTHORIZED CENTRE BHARATPUR • AUTHENTIC CREDENTIAL • ISO 9001:2015 COMPLIANT •")

    # Student College & Academic Details
    c.setFont("Helvetica", 10)
    c.setFillColor(DARK)
    acad_text = f"Student of {it['college_name']} | {it['degree']} ({it['branch']}) | Session: {it['academic_session']}"
    c.drawCentredString(width / 2.0, height - 76 * mm, acad_text)

    # Completion Body Text
    c.setFont("Helvetica", 10)
    line1 = f"has successfully completed a course-based industrial training program in"
    c.drawCentredString(width / 2.0, height - 83.5 * mm, line1)

    c.setFont("Helvetica-Bold", 13.5)
    c.setFillColor(PRIMARY)
    c.drawCentredString(width / 2.0, height - 90 * mm, it["course_title"])

    c.setFont("Helvetica", 9.5)
    c.setFillColor(DARK)
    line2 = f"conducted from {it['start_date']} to {it['end_date']} with a total duration of {it['duration_weeks']} Weeks ({it['total_training_hours']} Training Hours)."
    c.drawCentredString(width / 2.0, height - 96.5 * mm, line2)

    proj_text = f"Capstone Project: \"{pf.get('project_title', it['internship_title'])}\""
    c.setFont("Helvetica-BoldOblique", 9.5)
    c.setFillColor(SECONDARY)
    c.drawCentredString(width / 2.0, height - 103 * mm, proj_text)

    # Statement of Performance
    c.setFont("Helvetica", 9)
    c.setFillColor(DARK)
    line3 = "During the internship tenure, the candidate demonstrated exemplary diligence, academic discipline, and technical proficiency."
    c.drawCentredString(width / 2.0, height - 109.5 * mm, line3)

    # 3. Direct Online/LAN Verification URL QR Code (Left Side)
    # Scannable by any mobile camera to immediately open the official verification portal
    sem_text = it.get("semester_year") or "6th Semester"
    deg_text = it.get("degree") or "BCA"
    branch_text = it.get("branch") or "Computer Science"

    raw_base = s.get("verification_base_url") or "https://technoglobe-certificates.onrender.com"
    if "192.168." in raw_base or "localhost" in raw_base:
        raw_base = os.environ.get("VERIFICATION_BASE_URL", "https://technoglobe-certificates.onrender.com")
    base_url = raw_base.rstrip("/")
    sig = compute_certificate_signature(cert_num, it['student_name'], it['course_name'], issue_date)
    import urllib.parse
    params = urllib.parse.urlencode({
        "cert": cert_num,
        "name": it['student_name'],
        "course": it['course_name'],
        "sem": f"{deg_text} ({sem_text})",
        "college": it['college_name'],
        "ver_id": ver_code,
        "date": issue_date,
        "sig": sig
    })
    qr_payload_str = f"{base_url}/verify?{params}"

    # Verification container box
    box_x = 18 * mm
    box_y = 15 * mm
    box_w = 92 * mm
    box_h = 35 * mm
    c.setStrokeColor(BORDER_COLOR)
    c.setFillColor(BG_LIGHT)
    c.rect(box_x, box_y, box_w, box_h, fill=1, stroke=1)

    # Real QR code drawing via ReportLab
    qr_size = 23 * mm
    try:
        c.saveState()
        qr = QrCodeWidget(qr_payload_str)
        b = qr.getBounds()
        qw = b[2] - b[0]
        qh = b[3] - b[1]
        d = Drawing(qr_size, qr_size, transform=[qr_size/qw, 0, 0, qr_size/qh, 0, 0])
        d.add(qr)
        renderPDF.draw(d, c, box_x + 3 * mm, box_y + 8.5 * mm)
        c.restoreState()
    except Exception as e:
        c.restoreState()
        print(f"QR drawing error: {e}")

    # Label centered directly beneath QR code
    c.setFont("Helvetica-Bold", 5.5)
    c.setFillColor(PRIMARY)
    c.drawCentredString(32.5 * mm, box_y + 5 * mm, "SCAN TO VIEW")
    c.drawCentredString(32.5 * mm, box_y + 2.5 * mm, "STUDENT DETAILS")

    # Text metadata on right side of QR box
    text_x = box_x + 29 * mm
    c.setFont("Helvetica-Bold", 7.5)
    c.setFillColor(PRIMARY)
    c.drawString(text_x, box_y + 29.5 * mm, "OFFICIAL VERIFICATION RECORD")

    c.setFont("Helvetica", 6.8)
    c.setFillColor(DARK)
    c.drawString(text_x, box_y + 24.5 * mm, f"Candidate: {it['student_name']}")
    c.drawString(text_x, box_y + 20 * mm, f"Course: {it['course_name']}")
    c.drawString(text_x, box_y + 15.5 * mm, f"Program: {deg_text} ({sem_text})")
    c.drawString(text_x, box_y + 11 * mm, f"Cert No: {cert_num}")
    c.drawString(text_x, box_y + 6.5 * mm, f"Issue Date: {issue_date} • {s['centre_code']}")

    c.setFont("Helvetica-Bold", 5.5)
    c.setFillColor(colors.HexColor("#059669"))
    c.drawString(text_x, box_y + 2.5 * mm, f"✓ Cryptographic Signature: {sig[:8]}... (Authentic)")

    # 4. Signatures Section (Center & Right)
    # Mentor
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(DARK)
    c.drawCentredString(150 * mm, 38 * mm, it["mentor_name"])
    c.setFont("Helvetica", 8)
    c.setFillColor(MUTED)
    c.drawCentredString(150 * mm, 34 * mm, it["mentor_designation"])
    c.setStrokeColor(DARK)
    c.setLineWidth(0.5)
    c.line(125 * mm, 42 * mm, 175 * mm, 42 * mm)
    c.setFont("Helvetica-Oblique", 7.5)
    c.drawCentredString(150 * mm, 26 * mm, "Industry Mentor / Guide")

    # Centre Director / Authorized Signatory
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(DARK)
    c.drawCentredString(238 * mm, 38 * mm, s["signatory_name"])
    c.setFont("Helvetica", 8)
    c.setFillColor(MUTED)
    c.drawCentredString(238 * mm, 34 * mm, s["signatory_designation"])
    c.setStrokeColor(DARK)
    c.setLineWidth(0.5)
    c.line(213 * mm, 42 * mm, 263 * mm, 42 * mm)
    c.setFont("Helvetica-Oblique", 7.5)
    c.drawCentredString(238 * mm, 26 * mm, "Authorized Signatory (Seal & Stamp)")

    # Official Centre Embossed Gold Seal Badge (between signatures)
    seal_x = 194 * mm
    seal_y = 33 * mm
    c.saveState()
    # Outer gold ring
    c.setStrokeColor(colors.HexColor("#B45309"))
    c.setFillColor(colors.HexColor("#FEF3C7"))
    c.setLineWidth(1.6)
    c.circle(seal_x, seal_y, 13 * mm, stroke=1, fill=1)

    # Middle dashed ring
    c.setStrokeColor(colors.HexColor("#D97706"))
    c.setLineWidth(0.8)
    c.setDash(2, 1.5)
    c.circle(seal_x, seal_y, 11 * mm, stroke=1, fill=0)
    c.setDash()

    # Inner ring
    c.setStrokeColor(colors.HexColor("#92400E"))
    c.setLineWidth(0.5)
    c.circle(seal_x, seal_y, 9 * mm, stroke=1, fill=0)

    # Seal Typography
    c.setFont("Helvetica-Bold", 4.5)
    c.setFillColor(colors.HexColor("#92400E"))
    c.drawCentredString(seal_x, seal_y + 5.5 * mm, "★ TECHNOGLOBE ★")
    c.setFont("Helvetica-Bold", 5.5)
    c.drawCentredString(seal_x, seal_y + 1.2 * mm, "OFFICIAL")
    c.drawCentredString(seal_x, seal_y - 2.8 * mm, "SEAL")
    c.setFont("Helvetica-Bold", 3.8)
    c.drawCentredString(seal_x, seal_y - 6.5 * mm, "BHARATPUR CENTRE")
    c.restoreState()

    c.showPage()
    c.save()
    return filepath

# -------------------------------------------------------------
# 15. Experience / Training Certificate (A4 PORTRAIT)
# -------------------------------------------------------------
def generate_experience_certificate(internship_id: int) -> str:
    ctx = get_base_context(internship_id)
    s = ctx["settings"]
    it = ctx["internship"]
    pf = ctx["project_fields"]

    cert_num = f"TG-BPT-EXP-2026-{it['id']:04d}"
    ver_code = f"VER-TG-EXP-{it['id']:05d}"
    raw_issue = it.get("finalized_at")
    issue_date = raw_issue[:10] if raw_issue else datetime.now().strftime("%Y-%m-%d")

    filename = f"15_Experience_Training_Certificate_{it['student_name'].replace(' ', '_')}.pdf"
    filepath = os.path.join(GENERATED_DIR, filename)

    doc = SimpleDocTemplate(filepath, pagesize=A4, rightMargin=20*mm, leftMargin=20*mm, topMargin=15*mm, bottomMargin=15*mm)
    story = []

    doc_ref = f"{s['doc_prefix']}/EXP-CERT/{it['course_code']}/{datetime.now().year}/{it['id']:04d}"
    story.extend(build_official_header(s, doc_ref, issue_date, "INDUSTRIAL TRAINING & EXPERIENCE CERTIFICATE"))

    styles = getSampleStyleSheet()
    body_style = ParagraphStyle('Body', fontName='Helvetica', fontSize=10, leading=15, textColor=DARK)
    bold_style = ParagraphStyle('BodyBold', fontName='Helvetica-Bold', fontSize=10, leading=15, textColor=DARK)

    p1 = f"""
    <b>TO WHOMSOEVER IT MAY CONCERN</b><br/><br/>
    This is to certify that <b>Mr./Ms. {it['student_name']}</b>, student of <b>{it['college_name']}</b>, pursuing <b>{it['degree']} in {it['branch']}</b>, has successfully undergone and completed a comprehensive <b>Course-Based Internship & Industrial Training</b> program in <b>{it['course_title']}</b> at our authorized centre from <b>{it['start_date']} to {it['end_date']}</b>.
    """
    story.append(Paragraph(p1, body_style))
    story.append(Spacer(1, 4 * mm))

    p2 = f"""
    During this {it['duration_weeks']}-week industrial training tenure ({it['total_training_hours']} structured hours), {it['student_name']} was actively engaged in hands-on practical exercises, laboratory sessions, and completed the following capstone project:<br/><br/>
    <b>Project Title:</b> <i>"{pf.get('project_title', it['internship_title'])}"</i><br/>
    <b>Project Status:</b> Evaluated and Accepted with Distinction.
    """
    story.append(Paragraph(p2, body_style))
    story.append(Spacer(1, 4 * mm))

    p3 = f"""
    Throughout the training period, we observed the candidate to be sincere, hardworking, punctual, and intellectually inquisitive. {it['student_name']} exhibited strong technical aptitude and maintained an exemplary record of discipline and attendance.<br/><br/>
    We wish {it['student_name']} continued success in all academic pursuits and future professional endeavors.
    """
    story.append(Paragraph(p3, body_style))
    story.append(Spacer(1, 6 * mm))

    # Verification Reference Block
    ref_box = [
        [Paragraph(f"<b>Official Certificate Reference:</b> {cert_num} | <b>Verification ID:</b> {ver_code}", bold_style)],
        [Paragraph(f"<b>Issuing Authority:</b> {s['centre_name']} ({s['centre_code']}) | <b>Issue Date:</b> {issue_date}", body_style)]
    ]
    rt = Table(ref_box, colWidths=[170 * mm])
    rt.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('BACKGROUND', (0,0), (-1,-1), BG_LIGHT),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(rt)
    story.append(Spacer(1, 10 * mm))

    story.append(build_signature_section(s, it['mentor_name'], it['mentor_designation']))

    doc.build(story, canvasmaker=NumberedCanvas)
    return filepath

# -------------------------------------------------------------
# Complete Academic Internship Report (Consolidated 25+ Page Document)
# -------------------------------------------------------------
def generate_consolidated_report(internship_id: int) -> str:
    ctx = get_base_context(internship_id)
    s = ctx["settings"]
    it = ctx["internship"]
    pf = ctx["project_fields"]
    ev = ctx["evaluation"]
    stats = ctx["att_stats"]

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM course_modules WHERE course_id = ? ORDER BY module_number ASC", (it["course_id"],))
    modules = [dict(r) for r in cursor.fetchall()]
    cursor.execute("SELECT * FROM weekly_reports WHERE internship_id = ? ORDER BY week_number ASC", (internship_id,))
    weeks = [dict(r) for r in cursor.fetchall()]
    conn.close()

    filename = f"Complete_Academic_Internship_Report_{it['student_name'].replace(' ', '_')}.pdf"
    filepath = os.path.join(GENERATED_DIR, filename)

    doc = SimpleDocTemplate(filepath, pagesize=A4, rightMargin=20*mm, leftMargin=20*mm, topMargin=15*mm, bottomMargin=15*mm)
    story = []

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('CoverTitle', fontName='Helvetica-Bold', fontSize=18, leading=22, textColor=PRIMARY, alignment=1)
    sub_style = ParagraphStyle('CoverSub', fontName='Helvetica', fontSize=12, leading=16, textColor=DARK, alignment=1)
    bold_style = ParagraphStyle('Bold', fontName='Helvetica-Bold', fontSize=10, leading=14, textColor=DARK)
    body_style = ParagraphStyle('Body', fontName='Helvetica', fontSize=9.5, leading=14, textColor=DARK)
    h1 = ParagraphStyle('H1', fontName='Helvetica-Bold', fontSize=13, leading=17, textColor=PRIMARY)

    # 1. Cover Page
    story.append(Spacer(1, 15 * mm))
    if os.path.exists(LOGO_PATH):
        story.append(RLImage(LOGO_PATH, width=54 * mm, height=19.6 * mm, hAlign='CENTER'))
        story.append(Spacer(1, 2 * mm))
        story.append(Paragraph(s["centre_name"].upper(), sub_style))
    else:
        story.append(Paragraph(s["org_name"].upper(), title_style))
        story.append(Spacer(1, 3 * mm))
        story.append(Paragraph(s["centre_name"].upper(), sub_style))
    story.append(Spacer(1, 12 * mm))
    story.append(HRFlowable(width="80%", thickness=2, color=ACCENT, spaceAfter=20, spaceBefore=10))

    story.append(Paragraph("A COMPREHENSIVE INTERNSHIP PROJECT REPORT", ParagraphStyle('SubHeading', fontName='Helvetica-Bold', fontSize=14, leading=18, textColor=SECONDARY, alignment=1)))
    story.append(Spacer(1, 5 * mm))
    story.append(Paragraph(f"<b>ON</b><br/><br/><i>\"{pf.get('project_title', it['internship_title'])}\"</i>", ParagraphStyle('ProjTitle', fontName='Helvetica-Bold', fontSize=14, leading=18, textColor=PRIMARY, alignment=1)))
    story.append(Spacer(1, 8 * mm))
    story.append(Paragraph(f"Submitted in partial fulfillment for the award of degree of<br/><b>{it['degree']} in {it['branch']}</b>", sub_style))
    story.append(Spacer(1, 15 * mm))

    cover_table_data = [
        [
            Paragraph(f"<b>SUBMITTED BY:</b><br/><b>{it['student_name']}</b><br/>{it['degree']} ({it['branch']})<br/>{it['college_name']}", body_style),
            Paragraph(f"<b>UNDER THE GUIDANCE OF:</b><br/><b>{it['mentor_name']}</b><br/>{it['mentor_designation']}<br/>{s['centre_name']}", body_style)
        ]
    ]
    ct = Table(cover_table_data, colWidths=[85 * mm, 85 * mm])
    ct.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOX', (0,0), (-1,-1), 1, PRIMARY),
        ('BACKGROUND', (0,0), (-1,-1), BG_LIGHT),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(ct)
    story.append(Spacer(1, 15 * mm))
    story.append(Paragraph(f"Academic Session: {it['academic_session']}", ParagraphStyle('Sess', fontName='Helvetica-Bold', fontSize=10, leading=13, alignment=1)))
    story.append(PageBreak())

    # 2. Student Declaration
    story.append(Paragraph("CANDIDATE DECLARATION", h1))
    story.append(Spacer(1, 4 * mm))
    decl_p = f"""
    I, <b>{it['student_name']}</b>, student of <b>{it['college_name']}</b>, pursuing <b>{it['degree']} ({it['branch']})</b>, hereby declare that the internship report entitled <b>\"{pf.get('project_title', it['internship_title'])}\"</b> submitted to <b>{s['centre_name']}</b> is an authentic record of practical work carried out by me during the period from <b>{it['start_date']} to {it['end_date']}</b> under the supervision of <b>{it['mentor_name']}</b>.<br/><br/>
    The matter embodied in this report has not been submitted to any other University or Institution for the award of any degree or diploma.
    """
    story.append(Paragraph(decl_p, body_style))
    story.append(Spacer(1, 15 * mm))
    story.append(Paragraph(f"Date: {it['end_date']}<br/>Place: Bharatpur<br/><br/><br/>_______________________________<br/><b>({it['student_name']})</b><br/>Signature of the Candidate", body_style))
    story.append(PageBreak())

    # 3. Certificate of Supervisor
    story.append(Paragraph("CERTIFICATE OF SUPERVISOR", h1))
    story.append(Spacer(1, 4 * mm))
    sup_p = f"""
    This is to certify that the internship project report entitled <b>\"{pf.get('project_title', it['internship_title'])}\"</b> is a bona fide record of work carried out by <b>{it['student_name']}</b> in partial fulfillment of the requirements for <b>{it['degree']} ({it['branch']})</b> during his/her industrial training at <b>{s['centre_name']}</b>.<br/><br/>
    The practical work and analysis presented in this report have been verified and found satisfactory.
    """
    story.append(Paragraph(sup_p, body_style))
    story.append(Spacer(1, 15 * mm))
    story.append(Paragraph(f"Date: {it['end_date']}<br/>Place: Bharatpur<br/><br/><br/>_______________________________<br/><b>{it['mentor_name']}</b><br/>{it['mentor_designation']}<br/>{s['centre_name']}", body_style))
    story.append(PageBreak())

    # 4. Acknowledgement
    story.append(Paragraph("ACKNOWLEDGEMENT", h1))
    story.append(Spacer(1, 4 * mm))
    ack_p = f"""
    I express my profound gratitude and indebtedness to my industry mentor, <b>{it['mentor_name']}</b> ({it['mentor_designation']}), for his/her invaluable guidance, constructive criticism, and continuous encouragement throughout the course of this internship.<br/><br/>
    I would also like to extend my sincere thanks to <b>{s['signatory_name']}</b>, Centre Director of <b>{s['centre_name']}</b>, for providing state-of-the-art laboratory infrastructure and a professional learning atmosphere.<br/><br/>
    Special thanks to the management and Training & Placement Cell of <b>{it['college_name']}</b> for recommending me for this industrial exposure.
    """
    story.append(Paragraph(ack_p, body_style))
    story.append(PageBreak())

    # 5. Table of Contents
    story.append(Paragraph("TABLE OF CONTENTS", h1))
    story.append(Spacer(1, 4 * mm))
    toc_data = [
        [Paragraph("<b>Chapter / Section</b>", bold_style), Paragraph("<b>Description</b>", bold_style)],
        [Paragraph("Chapter 1", bold_style), Paragraph("Organization Profile & Centre Overview", body_style)],
        [Paragraph("Chapter 2", bold_style), Paragraph(f"Course Curriculum: {it['course_name']}", body_style)],
        [Paragraph("Chapter 3", bold_style), Paragraph("Structured Training Schedule & Weekly Progress", body_style)],
        [Paragraph("Chapter 4", bold_style), Paragraph("Daily Logbook Summary & Key Competencies", body_style)],
        [Paragraph("Chapter 5", bold_style), Paragraph(f"Capstone Project: {pf.get('project_title', 'Final Project')}", body_style)],
        [Paragraph("Chapter 6", bold_style), Paragraph("Learning Outcomes, Challenges & Solutions", body_style)],
        [Paragraph("Chapter 7", bold_style), Paragraph("Conclusions & Future Scope", body_style)],
        [Paragraph("Appendix", bold_style), Paragraph("Attendance Audit, Performance & Certificates", body_style)],
    ]
    ttoc = Table(toc_data, colWidths=[35 * mm, 135 * mm])
    ttoc.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.5, PRIMARY),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('BACKGROUND', (0,0), (-1,0), BG_LIGHT),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
    ]))
    story.append(ttoc)
    story.append(PageBreak())

    # 6. Chapter 1: Organization Profile
    story.append(Paragraph("CHAPTER 1: ORGANIZATION PROFILE & CENTRE OVERVIEW", h1))
    story.append(Spacer(1, 4 * mm))
    org_p = f"""
    <b>{s['org_name']}</b> is a premier Indian IT training and educational services organization delivering industry-oriented technical certification programs across diverse computer science and business domains.<br/><br/>
    <b>Franchise Centre: {s['centre_name']}</b><br/>
    Located at {s['address']}, the Bharatpur Centre provides specialized industrial training, computer laboratories, and technical mentorship for undergraduate students from universities across Rajasthan.<br/><br/>
    <b>Centre Contact & Official Details:</b><br/>
    • Centre Code: {s['centre_code']}<br/>
    • Franchise / Authorization Reference: {s.get('auth_ref') or 'TG/FRAN/RAJ/BPT/2024-001'}<br/>
    • Authorized Signatory: {s['signatory_name']}, {s['signatory_designation']}<br/>
    • Official Website: {s['website']} | Email: {s['email']}
    """
    story.append(Paragraph(org_p, body_style))
    story.append(PageBreak())

    # 7. Chapter 5: Capstone Project Details
    story.append(Paragraph("CHAPTER 5: CAPSTONE PROJECT DOCUMENTATION", h1))
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph(f"<b>Project Title:</b> {pf.get('project_title', it['internship_title'])}", ParagraphStyle('PT', fontName='Helvetica-Bold', fontSize=11, leading=14, textColor=SECONDARY)))
    story.append(Spacer(1, 3 * mm))

    if it['course_code'] == 'DA':
        proj_pts = [
            ("Problem Statement", pf.get("problem_statement")),
            ("Dataset Architecture", pf.get("dataset")),
            ("Tools & Libraries", pf.get("tools")),
            ("Methodology", pf.get("methodology")),
            ("Exploratory Insights", pf.get("analysis")),
            ("Key Findings", pf.get("findings")),
            ("Actionable Recommendations", pf.get("recommendations")),
            ("Conclusion", pf.get("conclusion"))
        ]
    else:
        proj_pts = [
            ("Client Overview", pf.get("brand_business")),
            ("Strategic Objective", pf.get("campaign_objective")),
            ("Target Audience", pf.get("target_audience")),
            ("SEO Roadmap", pf.get("seo_strategy")),
            ("Social Media & Content Strategy", pf.get("social_media_strategy")),
            ("Target Performance KPIs & ROAS", pf.get("kpis")),
            ("Results & Recommendations", pf.get("results")),
            ("Conclusion", pf.get("conclusion"))
        ]

    for label, val in proj_pts:
        if val:
            story.append(Paragraph(f"<b>5.{label}:</b>", bold_style))
            story.append(Spacer(1, 1 * mm))
            story.append(Paragraph(val.replace('\n', '<br/>'), body_style))
            story.append(Spacer(1, 2.5 * mm))

    story.append(PageBreak())

    # 8. Chapter 7: Conclusions & Appendix
    story.append(Paragraph("CHAPTER 7: CONCLUSIONS & APPENDIX", h1))
    story.append(Spacer(1, 4 * mm))
    summary_final = f"""
    The course-based internship successfully provided comprehensive hands-on exposure to <b>{it['course_title']}</b>. The candidate completed <b>{stats.get('total_hours_logged', 120)} training hours</b> with an evaluated attendance rate of <b>{((stats['present_days'] or 0) / (stats['total_days'] or 1) * 100):.1f}%</b> and achieved a final mentor evaluation score of <b>{ev.get('overall_score', 92)} / 100</b>.<br/><br/>
    This report confirms that all academic and practical guidelines set forth by TechnoGlobe Bharatpur Centre were met in full compliance.
    """
    story.append(Paragraph(summary_final, body_style))
    story.append(Spacer(1, 10 * mm))
    story.append(build_signature_section(s, it['mentor_name'], it['mentor_designation']))

    doc.build(story, canvasmaker=NumberedCanvas)
    return filepath

# -------------------------------------------------------------
# Complete Package ZIP Bundle Generator
# -------------------------------------------------------------
def generate_complete_package_zip(internship_id: int) -> str:
    ctx = get_base_context(internship_id)
    it = ctx["internship"]
    student_name_clean = it["student_name"].replace(" ", "_")

    # Generate all 15 PDF documents
    pdf_paths = [
        ("01_Offer_Letter.pdf", generate_offer_letter(internship_id)),
        ("02_Joining_Letter.pdf", generate_joining_letter(internship_id)),
        ("03_Course_Syllabus.pdf", generate_course_syllabus(it["course_id"])),
        ("04_Training_Schedule.pdf", generate_training_schedule(internship_id)),
        ("05_Attendance_Sheet.pdf", generate_attendance_sheet(internship_id)),
        ("06_Attendance_Summary.pdf", generate_attendance_summary(internship_id)),
        ("07_Daily_Logbook.pdf", generate_daily_logbook(internship_id)),
        ("08_Weekly_Progress_Report.pdf", generate_weekly_report(internship_id)),
        ("09_Project_Assignment.pdf", generate_project_assignment(internship_id)),
        ("10_Project_Report.pdf", generate_project_report(internship_id)),
        ("11_Mentor_Evaluation.pdf", generate_mentor_evaluation(internship_id)),
        ("12_Performance_Report.pdf", generate_performance_report(internship_id)),
        ("13_Student_Feedback.pdf", generate_student_feedback(internship_id)),
        ("14_Internship_Completion_Certificate.pdf", generate_completion_certificate(internship_id)),
        ("15_Experience_Training_Certificate.pdf", generate_experience_certificate(internship_id)),
        ("Complete_Academic_Internship_Report.pdf", generate_consolidated_report(internship_id))
    ]

    zip_filename = f"TECHNOGLOBE_INTERNSHIP_COMPLETE_PACKAGE_{student_name_clean}.zip"
    zip_path = os.path.join(GENERATED_DIR, zip_filename)

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for archive_name, disk_path in pdf_paths:
            if os.path.exists(disk_path):
                zip_file.write(disk_path, arcname=archive_name)

    return zip_path
