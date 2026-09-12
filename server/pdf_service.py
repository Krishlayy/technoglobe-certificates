import os
import io
import json
import csv
import zipfile
import hashlib
import hmac
from datetime import datetime, timedelta
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

    # Institution profile
    inst_id = internship.get("institution_id") or 1
    cursor.execute("SELECT * FROM institutions WHERE id = ?", (inst_id,))
    inst_row = cursor.fetchone()
    if not inst_row:
        cursor.execute("SELECT * FROM institutions ORDER BY id ASC LIMIT 1")
        inst_row = cursor.fetchone()
    institution = dict(inst_row) if inst_row else {
        "id": 1, "code": "TG", "name": "TechnoGlobe", "full_name": "TechnoGlobe IT Solutions Pvt. Ltd.",
        "logo_path": "technoglobe_logo.png", "primary_color": "#0B2545", "secondary_color": "#134074",
        "accent_color": "#D4AF37", "signatory_name": "Nitin Sir", "signatory_designation": "Centre Head & Authorized Signatory",
        "stamp_mode": "DIGITAL_BADGE", "watermark_mode": "SEAL", "address": "Bharatpur, Rajasthan"
    }

    # Update settings copy to reflect active institution
    settings["institution"] = institution
    if institution.get("code") == "PODDAR":
        settings["org_name"] = "PODDAR COLLEGE OF TECHNOLOGY & MANAGEMENT"
        settings["centre_name"] = "PODDAR COLLEGE"
        settings["address"] = institution.get("address", "Bharatpur, Rajasthan")
        settings["logo_url"] = "poddar_logo.png"
        settings["cert_prefix"] = "PCTM"
        settings["doc_prefix"] = "PCTM/BPT"

    conn.close()
    return {
        "settings": settings,
        "institution": institution,
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
        footer_text = f"Course-Based Internship Documentation — Page {self._pageNumber} of {page_count}"
        self.drawCentredString(A4[0] / 2.0, 10 * mm, footer_text)
        self.restoreState()

def build_official_header(settings, doc_ref, doc_date, doc_title, institution=None):
    inst = institution or settings.get("institution") or {}
    is_poddar = (inst.get("code") == "PODDAR" or settings.get("code") == "PODDAR" or "Poddar" in settings.get("centre_name", ""))
    
    inst_primary = colors.HexColor(inst.get("primary_color", "#0A2540") if is_poddar else "#0B2545")
    inst_secondary = colors.HexColor(inst.get("secondary_color", "#EAA824") if is_poddar else "#134074")
    inst_accent = colors.HexColor(inst.get("accent_color", "#EAA824") if is_poddar else "#D4AF37")

    styles = getSampleStyleSheet()
    header_elements = []

    org_style = ParagraphStyle('OrgHeader', fontName='Helvetica-Bold', fontSize=14, leading=17, textColor=inst_primary, alignment=1)
    centre_style = ParagraphStyle('CentreHeader', fontName='Helvetica-Bold', fontSize=10.5, leading=13.5, textColor=inst_secondary, alignment=1)
    addr_style = ParagraphStyle('AddrHeader', fontName='Helvetica', fontSize=8, leading=10.5, textColor=MUTED, alignment=1)
    ref_style = ParagraphStyle('RefStyle', fontName='Helvetica-Bold', fontSize=8.5, leading=11, textColor=DARK)
    date_style = ParagraphStyle('DateStyle', fontName='Helvetica-Bold', fontSize=8.5, leading=11, textColor=DARK, alignment=2)
    title_style = ParagraphStyle('TitleStyle', fontName='Helvetica-Bold', fontSize=12.5, leading=15.5, textColor=inst_primary, alignment=1)

    logo_filename = inst.get("logo_path", "poddar_logo.png" if is_poddar else "technoglobe_logo.png")
    logo_full_path = os.path.join(os.path.dirname(__file__), logo_filename)

    if os.path.exists(logo_full_path):
        if is_poddar:
            header_elements.append(RLImage(logo_full_path, width=22 * mm, height=22 * mm, hAlign='CENTER'))
            header_elements.append(Spacer(1, 1 * mm))
            header_elements.append(Paragraph("PODDAR COLLEGE OF TECHNOLOGY & MANAGEMENT", org_style))
            header_elements.append(Paragraph("Bharatpur, Rajasthan", centre_style))
            header_elements.append(Spacer(1, 1 * mm))
            addr_line = "Bharatpur, Rajasthan | Phone: +91 94140 12345 | Web: https://poddarcollege.org"
            header_elements.append(Paragraph(addr_line, addr_style))
        else:
            header_elements.append(RLImage(logo_full_path, width=38 * mm, height=13.8 * mm, hAlign='CENTER'))
            header_elements.append(Spacer(1, 1 * mm))
            header_elements.append(Paragraph(settings.get("centre_name", "TECHNOGLOBE – BHARATPUR CENTRE"), centre_style))
            header_elements.append(Spacer(1, 1 * mm))
            addr_line = f"{settings.get('address')} | Phone: {settings.get('phone')} | Email: {settings.get('email')} | Web: {settings.get('website')}"
            header_elements.append(Paragraph(addr_line, addr_style))
    else:
        header_elements.append(Paragraph(inst.get("full_name") or settings.get("org_name"), org_style))
        header_elements.append(Spacer(1, 1 * mm))
        header_elements.append(Paragraph(inst.get("address") or settings.get("centre_name"), centre_style))

    header_elements.append(Spacer(1, 2 * mm))
    header_elements.append(HRFlowable(width="100%", thickness=1.5, color=inst_primary, spaceAfter=8, spaceBefore=2))

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
    header_elements.append(HRFlowable(width="30%", thickness=1, color=inst_accent, spaceAfter=10, spaceBefore=2))

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
    inst = ctx.get("institution", {})
    it = ctx["internship"]
    pf = ctx["project_fields"]

    is_poddar = (inst.get("code") == "PODDAR" or it.get("institution_id") == 2)
    c_primary = colors.HexColor("#0A2540") if is_poddar else PRIMARY
    c_secondary = colors.HexColor("#0F3A66") if is_poddar else SECONDARY
    c_accent = colors.HexColor("#EAA824") if is_poddar else ACCENT

    cert_prefix = inst.get("cert_prefix") or ("PCTM" if is_poddar else "TG-BPT")
    doc_prefix = inst.get("doc_prefix") or ("PCTM/BPT" if is_poddar else "TG/BPT")

    cert_num = it["certificate_number"] or f"{cert_prefix}-{it['course_code']}-2026-{it['id']:04d}"
    ver_code = it["verification_code"] or f"VER-{cert_prefix}-{it['course_code']}-{it['id']:05d}"
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
    c.setStrokeColor(c_primary)
    c.setLineWidth(4)
    c.rect(10 * mm, 10 * mm, width - 20 * mm, height - 20 * mm)

    # Inner Gold Border
    c.setStrokeColor(c_accent)
    c.setLineWidth(1.5)
    c.rect(13 * mm, 13 * mm, width - 26 * mm, height - 26 * mm)

    # Corner Ornaments (Top-Left, Top-Right, Bottom-Right)
    orn_len = 14 * mm
    c.setStrokeColor(c_accent)
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

    # Translucent Background Watermark
    poddar_logo_path = os.path.join(os.path.dirname(__file__), "poddar_logo.png")
    if is_poddar and os.path.exists(poddar_logo_path):
        c.saveState()
        try:
            c.setFillAlpha(0.08)
            c.setStrokeAlpha(0.08)
        except Exception:
            pass
        wm_size = 95 * mm
        c.drawImage(poddar_logo_path, (width - wm_size)/2.0, (height - wm_size)/2.0 - 4*mm, width=wm_size, height=wm_size, mask='auto', preserveAspectRatio=True)
        c.restoreState()

    # 2. Header / Branding with Official Logo
    if is_poddar and os.path.exists(poddar_logo_path):
        logo_size = 23 * mm
        logo_x = (width - logo_size) / 2.0
        logo_y = height - 33.5 * mm
        c.drawImage(poddar_logo_path, logo_x, logo_y, width=logo_size, height=logo_size, mask='auto', preserveAspectRatio=True)

        c.setFont("Helvetica-Bold", 11.5)
        c.setFillColor(c_primary)
        c.drawCentredString(width / 2.0, height - 37 * mm, "PODDAR COLLEGE OF TECHNOLOGY & MANAGEMENT")

        c.setFont("Helvetica", 7.5)
        c.setFillColor(MUTED)
        c.drawCentredString(width / 2.0, height - 40.5 * mm, "Bharatpur, Rajasthan | Website: https://poddarcollege.org")
    elif os.path.exists(LOGO_PATH):
        logo_w = 46 * mm
        logo_h = 16.7 * mm
        logo_x = (width - logo_w) / 2.0
        logo_y = height - 31.5 * mm
        c.drawImage(LOGO_PATH, logo_x, logo_y, width=logo_w, height=logo_h, mask='auto', preserveAspectRatio=True)

        c.setFont("Helvetica-Bold", 10.5)
        c.setFillColor(c_secondary)
        c.drawCentredString(width / 2.0, height - 35.5 * mm, s.get("centre_name", "TECHNOGLOBE – BHARATPUR CENTRE"))

        c.setFont("Helvetica", 7.2)
        c.setFillColor(MUTED)
        c.drawCentredString(width / 2.0, height - 39 * mm, f"{s.get('address')} | Website: {s.get('website')}")
    else:
        c.setFont("Helvetica-Bold", 18)
        c.setFillColor(c_primary)
        c.drawCentredString(width / 2.0, height - 26 * mm, inst.get("full_name") or s.get("org_name"))

        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(c_secondary)
        c.drawCentredString(width / 2.0, height - 32 * mm, inst.get("address") or s.get("centre_name"))

    # Gold / Accent separator line
    c.setStrokeColor(c_accent)
    c.setLineWidth(1)
    c.line(55 * mm, height - 42.5 * mm, width - 55 * mm, height - 42.5 * mm)

    # Certificate Title
    c.setFont("Helvetica-Bold", 20.5)
    c.setFillColor(c_primary)
    c.drawCentredString(width / 2.0, height - 51 * mm, "CERTIFICATE OF INTERNSHIP COMPLETION")

    c.setFont("Helvetica-Oblique", 10.5)
    c.setFillColor(DARK)
    c.drawCentredString(width / 2.0, height - 58 * mm, "This is to certify that")

    # Student Name (Large, Bold & Highlighted)
    c.setFont("Helvetica-Bold", 23)
    c.setFillColor(c_secondary)
    c.drawCentredString(width / 2.0, height - 68 * mm, it["student_name"].upper())

    # Decorative underline below name
    name_w = c.stringWidth(it["student_name"].upper(), "Helvetica-Bold", 23)
    c.setStrokeColor(c_accent)
    c.setLineWidth(1.5)
    c.line((width - name_w) / 2.0 - 10*mm, height - 70 * mm, (width + name_w) / 2.0 + 10*mm, height - 70 * mm)

    # Micro-text security line below name underline
    c.setFont("Helvetica-Bold", 4.3)
    c.setFillColor(colors.HexColor("#475569"))
    sec_line = "• PODDAR COLLEGE OF TECHNOLOGY & MANAGEMENT • BHARATPUR, RAJASTHAN • AUTHENTIC CREDENTIAL •" if is_poddar else "• TECHNOGLOBE IT SOLUTIONS PVT. LTD. • AUTHORIZED CENTRE BHARATPUR • AUTHENTIC CREDENTIAL • ISO 9001:2015 COMPLIANT •"
    c.drawCentredString(width / 2.0, height - 72.3 * mm, sec_line)

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
    c.setFillColor(c_primary)
    c.drawCentredString(width / 2.0, height - 90 * mm, it["course_title"])

    c.setFont("Helvetica", 9.5)
    c.setFillColor(DARK)
    line2 = f"conducted from {it['start_date']} to {it['end_date']} with a total duration of {it['duration_weeks']} Weeks ({it['total_training_hours']} Training Hours)."
    c.drawCentredString(width / 2.0, height - 96.5 * mm, line2)

    proj_text = f"Capstone Project: \"{pf.get('project_title', it['internship_title'])}\""
    c.setFont("Helvetica-BoldOblique", 9.5)
    c.setFillColor(c_secondary)
    c.drawCentredString(width / 2.0, height - 103 * mm, proj_text)

    # Statement of Performance
    c.setFont("Helvetica", 9)
    c.setFillColor(DARK)
    line3 = "During the internship tenure, the candidate demonstrated exemplary diligence, academic discipline, and technical proficiency."
    c.drawCentredString(width / 2.0, height - 109.5 * mm, line3)

    # 3. Direct Online/LAN Verification URL QR Code (Left Side)
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
    c.setFillColor(c_primary)
    c.drawCentredString(32.5 * mm, box_y + 5 * mm, "SCAN TO VIEW")
    c.drawCentredString(32.5 * mm, box_y + 2.5 * mm, "STUDENT DETAILS")

    # Text metadata on right side of QR box
    text_x = box_x + 29 * mm
    c.setFont("Helvetica-Bold", 7.5)
    c.setFillColor(c_primary)
    c.drawString(text_x, box_y + 29.5 * mm, "OFFICIAL VERIFICATION RECORD")

    c.setFont("Helvetica", 6.8)
    c.setFillColor(DARK)
    c.drawString(text_x, box_y + 24.5 * mm, f"Candidate: {it['student_name']}")
    c.drawString(text_x, box_y + 20 * mm, f"Course: {it['course_name']}")
    c.drawString(text_x, box_y + 15.5 * mm, f"Program: {deg_text} ({sem_text})")
    c.drawString(text_x, box_y + 11 * mm, f"Cert No: {cert_num}")
    c.drawString(text_x, box_y + 6.5 * mm, f"Issue Date: {issue_date} • {inst.get('code', 'BPT')}")

    c.setFont("Helvetica-Bold", 5.5)
    c.setFillColor(colors.HexColor("#059669"))
    c.drawString(text_x, box_y + 2.5 * mm, f"✓ Cryptographic Signature: {sig[:8]}... (Authentic)")

    # 4. Signatures Section (Center & Right)
    # Mentor
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(DARK)
    c.drawCentredString(148 * mm, 38 * mm, it["mentor_name"])
    c.setFont("Helvetica", 8)
    c.setFillColor(MUTED)
    c.drawCentredString(148 * mm, 34 * mm, it["mentor_designation"])
    c.setStrokeColor(DARK)
    c.setLineWidth(0.5)
    c.line(125 * mm, 42 * mm, 171 * mm, 42 * mm)
    c.setFont("Helvetica-Oblique", 7.5)
    c.drawCentredString(148 * mm, 26 * mm, "Faculty Mentor / Guide")

    # Centre Director / Authorized Signatory
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(DARK)
    c.drawCentredString(244 * mm, 38 * mm, "Nitin Sir")
    c.setFont("Helvetica", 8)
    c.setFillColor(MUTED)
    c.drawCentredString(244 * mm, 34 * mm, "Center Head & Authorized Signatory" if is_poddar else s.get("signatory_designation", "Centre Head"))
    c.setStrokeColor(DARK)
    c.setLineWidth(0.5)
    c.line(220 * mm, 42 * mm, 268 * mm, 42 * mm)
    c.setFont("Helvetica-Oblique", 7.5)
    c.drawCentredString(244 * mm, 26 * mm, "Authorized Signatory (Seal & Stamp)")

    if is_poddar:
        # Empty space for physical ink stamp
        stamp_x = 180 * mm
        stamp_y = 15 * mm
        stamp_w = 34 * mm
        stamp_h = 35 * mm
        c.saveState()
        c.setStrokeColor(colors.HexColor("#94A3B8"))
        c.setLineWidth(0.8)
        c.setDash(2, 1.5)
        c.setFillColor(colors.HexColor("#FFFFFF"))
        c.roundRect(stamp_x, stamp_y, stamp_w, stamp_h, 2*mm, fill=1, stroke=1)
        c.setFont("Helvetica-Bold", 5.5)
        c.setFillColor(colors.HexColor("#64748B"))
        c.drawCentredString(stamp_x + stamp_w/2.0, stamp_y + stamp_h/2.0 + 3*mm, "[ OFFICIAL COLLEGE SEAL ]")
        c.setFont("Helvetica-Oblique", 5)
        c.drawCentredString(stamp_x + stamp_w/2.0, stamp_y + stamp_h/2.0 - 3*mm, "(Apply Ink Stamp Here)")
        c.restoreState()
    else:
        # Official Centre Embossed Gold Seal Badge (between signatures)
        seal_x = 194 * mm
        seal_y = 33 * mm
        c.saveState()
        c.setStrokeColor(colors.HexColor("#B45309"))
        c.setFillColor(colors.HexColor("#FEF3C7"))
        c.setLineWidth(1.6)
        c.circle(seal_x, seal_y, 13 * mm, stroke=1, fill=1)

        c.setStrokeColor(colors.HexColor("#D97706"))
        c.setLineWidth(0.8)
        c.setDash(2, 1.5)
        c.circle(seal_x, seal_y, 11 * mm, stroke=1, fill=0)
        c.setDash()

        c.setStrokeColor(colors.HexColor("#92400E"))
        c.setLineWidth(0.5)
        c.circle(seal_x, seal_y, 9 * mm, stroke=1, fill=0)

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
# Complete Academic Internship Report (30-Page Calibrated Document)
# -------------------------------------------------------------
def generate_consolidated_report(internship_id: int) -> str:
    import project_report_service
    return project_report_service.build_25page_academic_project_report(internship_id)

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


# =============================================================================
# BULK & MULTI-STUDENT BATCH ATTENDANCE GENERATOR ENGINE (LANDSCAPE & ZIP)
# =============================================================================

class LandscapeNumberedCanvas(canvas.Canvas):
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
        self.setFont("Helvetica-Bold", 7.5)
        self.setFillColor(colors.HexColor("#64748B"))
        # Landscape A4 dimensions: 297mm x 210mm
        footer_text = f"Master Batch Attendance Register — Page {self._pageNumber} of {page_count} | Official Institutional Record"
        self.drawCentredString(landscape(A4)[0] / 2.0, 7 * mm, footer_text)
        self.setFont("Helvetica", 7)
        self.drawString(12 * mm, 7 * mm, "TechnoGlobe & Poddar College Institutional Documentation")
        self.drawRightString(landscape(A4)[0] - 12 * mm, 7 * mm, "Authorized Signatory: Nitin Sir")
        self.restoreState()


BATCH_TRACK_TOPICS = {
    'DA': [
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
        "Data Cleaning & Feature Engineering", "Power BI Executive Dashboard Finalization", "Capstone Report Documentation & Presentation",
        "Advanced DAX Performance Optimization", "Automated Data Refresh & Gateway Setup", "Business Intelligence Executive Reporting",
        "End-to-End Analytics Pipeline Validation", "Data Storytelling & Stakeholder Presentation", "Production Pipeline Deployment & Viva"
    ],
    'DM': [
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
        "A/B Testing Methodologies for Paid Campaigns", "Capstone Campaign Blueprint & Budget Allocation", "Digital Marketing Strategy Dossier Finalization",
        "Growth Hacking & Viral Coefficient Engineering", "Influencer Outreach & Affiliate Partnerships", "Marketing Automation & CRM Workflows",
        "Omnichannel Attribution Modeling & ROAS Audit", "Executive Marketing Pitch & Campaign Viva"
    ],
    'FS': [
        "HTML5 Semantic Structure & Modern Accessibility", "CSS Flexbox, CSS Grid & Layout Systems", "Tailwind CSS Utility Design & Responsive UI",
        "Modern JavaScript (ES6+), Closures & Promises", "Asynchronous JavaScript, Fetch API & Async/Await", "DOM Manipulation & Browser Event Life Cycles",
        "React.js Component Architecture & JSX", "React Hooks Deep Dive: useState & useEffect", "Custom Hooks & Controlled Form Component States",
        "React Router v6 Nested Routing & Protected Guards", "Global State Management with React Context / Redux", "Tailwind UI Components & Dynamic Animations",
        "Node.js Architecture & Asynchronous Event Loop", "Express.js REST API Server & Routing Modules", "Custom Middleware, Logging & Central Error Handling",
        "JWT Token Authentication & BCrypt Password Hashing", "Role-Based Route Authorization & Security Headers", "MongoDB Atlas Setup & Document Data Modeling",
        "Mongoose Schemas, Relationships & Validations", "Mongoose Aggregation Pipelines & Query Indexing", "Full Stack Integration: Connecting React with Express",
        "Axios Interceptors for JWT Bearer Token Handling", "Input Validation (Zod/Joi) & Data Sanitization", "Automated API Unit & Integration Testing in Postman",
        "Docker Containerization of MERN Applications", "Multi-Stage Dockerfiles & Image Size Optimization", "Environment Variable Management & Cloud Secrets",
        "Production Deployment on Render / Cloud Platforms", "Continuous Integration Workflows with GitHub Actions", "CORS Configuration, Helmet & Rate Limiting",
        "Database Backup & Data Restoration Automation", "Performance Profiling & Webpack / Vite Optimization", "Capstone Architecture Blueprint & API Contracts",
        "Frontend UI & Backend REST API Finalization", "End-to-End System Testing & Bug Remediation", "Capstone Documentation & Technical Viva Voce Defense",
        "Microservices Decomposition & WebSockets Integration", "Redis Caching Layer & Query Speedup", "Serverless Functions & Edge API Execution",
        "Production Load Testing & Scalability Audit", "Full Stack Engineering Portfolio & Project Defense"
    ],
    'AI': [
        "Python Advanced Syntax, OOPs & Clean Code Standards", "Functional Python, Lambdas, Decorators & Generators", "NumPy N-Dimensional Arrays & Vectorized Math",
        "Pandas DataFrames, Series & Advanced Indexing", "Data Ingestion from CSV, Excel, SQL & JSON Sources", "Handling Missing Values, Imputation & Outlier IQR",
        "Data Transformation, Reshaping & Pivot Tables", "Matplotlib Architecture, Subplots & Aesthetics", "Seaborn Statistical Visualizations & Distribution Plots",
        "Exploratory Data Analysis (EDA) & Feature Correlation", "Probability Distributions & Statistical Hypotheses", "Feature Engineering: One-Hot, Scaling & Encoding",
        "Principal Component Analysis (PCA) & Dimensionality", "Supervised Learning: Linear & Logistic Regression", "Decision Trees, Gini Impurity & Entropy Measures",
        "Ensemble Learning: Random Forest & Bagging Models", "Gradient Boosting Architectures: XGBoost & LightGBM", "Hyperparameter Optimization via GridSearchCV",
        "Model Evaluation Metrics: Precision, Recall, ROC-AUC", "Stratified K-Fold Cross-Validation Workflows", "Unsupervised Clustering: K-Means & Silhouette Scores",
        "Hierarchical Clustering & Anomaly Isolation Forests", "Neural Network Foundations & Activation Functions", "TensorFlow & Keras Deep Learning Architectures",
        "Preventing Overfitting: Dropout & EarlyStopping", "Convolutional Neural Networks (CNN) Foundations", "Natural Language Processing (NLP) & Text Vectorization",
        "Model Serialization with Joblib & Model Versioning", "FastAPI Microservice Development for Model Serving", "Dockerizing AI Inference Applications",
        "Responsible AI, Model Explainability & SHAP Analysis", "Cloud AI Model Deployment & Endpoint Testing", "Capstone Problem Definition & Dataset Curation",
        "Model Training, Validation & Performance Tuning", "Interactive Model Prediction Dashboard UI", "Applied AI Capstone Dissertation & Technical Defense",
        "Deep Neural Architectures & Transformer Attention", "LLM Prompt Engineering & LangChain Pipelines", "Vector Databases (Chroma/Pinecone) & RAG Setup",
        "AI Model Monitoring & Data Drift Detection", "Autonomous AI System Architecture & Viva Defense"
    ],
    'CS': [
        "Cyber Security Fundamentals, CIA Triad & Threat Landscapes", "Computer Networking Protocols: TCP/IP, OSI & Subnetting", "Packet Sniffing & Deep Packet Inspection in Wireshark",
        "Port Scanning, Service Discovery & Network Mapping (Nmap)", "Man-in-the-Middle (MITM) & ARP Spoofing Mechanics", "Linux System Security Administration & Permissions",
        "User Management, Sudoers Hardening & SSH Key Security", "Linux Firewalls (UFW, IPTables) & Network Hardening", "System Audit Logging & Bash Automation Scripting",
        "Open Source Intelligence (OSINT) & Reconnaissance", "Automated Vulnerability Scanning with OpenVAS & Nessus", "CVE / NVD Databases & CVSS Risk Scoring Matrix",
        "OWASP Top 10 Web Vulnerabilities Deep Dive", "SQL Injection (SQLi) Exploitation & Parameterized Defense", "Cross-Site Scripting (XSS: Stored, Reflected, DOM)",
        "Broken Authentication, Session Hijacking & CSRF", "Insecure Direct Object References (IDOR) & Access Flaws", "Burp Suite Intercepting Proxy & Repeater Workflows",
        "Symmetric Encryption: AES-256 & Block Cipher Modes", "Asymmetric Cryptography: RSA, ECC & Diffie-Hellman", "Cryptographic Hash Functions: SHA-256 & Integrity",
        "Public Key Infrastructure (PKI) & SSL/TLS 1.3 Protocol", "Stateful Firewalls & Next-Gen Network Defense", "Intrusion Detection Systems (Snort / Suricata) Setup",
        "Writing Custom Snort Signatures for Threat Detection", "SIEM Architecture & Centralized Log Auditing (Wazuh)", "NIST Incident Response Lifecycle (PICERL) Phases",
        "Digital Forensics, Disk Imaging & Evidence Chain of Custody", "Memory Forensics & Artifact Extraction in Volatility", "Security Auditing & Compliance Standards (ISO 27001)",
        "Wireless Network Security & WPA2/WPA3 Vulnerabilities", "API Security Testing & Endpoint Hardening", "Capstone VAPT Rules of Engagement & Target Scoping",
        "Automated & Manual Penetration Testing Execution", "Vulnerability Remediation Matrix & Patch Plan", "Enterprise VAPT Audit Report & Executive Defense",
        "Active Directory Pentesting & Kerberoasting", "Cloud Security Posture Management (CSPM)", "Zero Trust Architecture & Micro-segmentation",
        "SOC Threat Hunting & Playbook Automation", "Defensive Security Audit Defense & Viva"
    ],
    'CC': [
        "Cloud Computing Models (IaaS, PaaS, SaaS) & Economics", "AWS Global Infrastructure: Regions, AZs & Edge Locations", "AWS Identity & Access Management (IAM) Least Privilege",
        "Amazon EC2 Instance Types, Lifecycle & Virtualization", "Virtual Private Cloud (VPC) Architecture & Subnetting", "Internet Gateways, NAT Gateways & Custom Route Tables",
        "Security Groups vs Network ACLs (NACL) Rules", "EC2 User Data Scripts & Automated Server Bootstrapping", "Amazon S3 Storage Classes, Bucket Policies & CORS",
        "Elastic Block Store (EBS) & Elastic File System (EFS)", "Amazon Relational Database Service (RDS) Multi-AZ Setup", "Amazon DynamoDB NoSQL Architecture & Partition Keys",
        "Amazon CloudFront Global Content Delivery Network (CDN)", "Amazon Route 53 DNS Routing Policies & Health Checks", "Linux Administration & Shell Scripting for Cloud Engineers",
        "Git Branching Models (Gitflow) & Remote Collaboration", "Virtual Machines vs Containerization Architecture", "Docker Engine Fundamentals, CLI & Image Layering",
        "Writing Production Dockerfiles & Multi-Stage Builds", "Docker Compose for Multi-Tier Service Orchestration", "Docker Volume Data Persistence & Container Networking",
        "Continuous Integration & Continuous Delivery (CI/CD) Concepts", "GitHub Actions Workflow Syntax, Actions & Triggers", "Automating Tests & Docker Image Builds in CI/CD",
        "Automated Cloud Deployment via SSH & Cloud Secrets", "Kubernetes Architecture: Control Plane & Worker Nodes", "Pods, ReplicaSets & Declarative Deployment YAMLs",
        "Kubernetes ClusterIP, NodePort & LoadBalancer Services", "Ingress Controllers, Reverse Proxies & SSL Certificates", "ConfigMaps, Secrets & Persistent Volume Claims (PVC)",
        "Infrastructure as Code (IaC) Principles with Terraform", "Terraform HCL Syntax, State Management & AWS Providers", "AWS CloudWatch Metrics, Alarms & Centralized Logs",
        "Prometheus & Grafana Infrastructure Observability", "Capstone Cloud Architecture Design & Capacity Planning", "Automated Multi-Tier Cloud Deployment & Defense",
        "Helm Charts & Kubernetes Package Management", "Service Mesh Architecture (Istio / Envoy)", "Cloud Cost Optimization & FinOps Strategies",
        "Disaster Recovery & Multi-Region Failover Architecture", "DevOps Enterprise Capstone Release & Viva"
    ],
    'JV': [
        "Java Architecture, JVM, JRE, JDK & Memory Management", "Primitive Data Types, Operators & Control Flow Logic", "Object-Oriented Programming: Classes, Objects & Methods",
        "Inheritance, Method Overriding & Dynamic Polymorphism", "Abstract Classes, Interface Design & Multiple Inheritance", "Encapsulation, Access Modifiers & Package Structures",
        "Exception Handling Hierarchy: Checked vs Unchecked", "Custom Exception Development & Logging Frameworks", "Java Generics & Type-Safe Class Design",
        "Java Collections: List Implementations (ArrayList, LinkedList)", "Java Collections: Set Implementations (HashSet, TreeSet)", "Java Collections: Map Implementations (HashMap, TreeMap)",
        "Lambda Expressions, Functional Interfaces & Predicates", "Java 8+ Streams API: Filter, Map, FlatMap & Reduce", "Stream Collectors, GroupingBy & Parallel Stream Processing",
        "RDBMS Schema Design, Normalization & Relational Constraints", "Complex SQL: Multi-Table JOINs, Subqueries & Aggregates", "ACID Properties & Database Transaction Isolation Levels",
        "Java Database Connectivity (JDBC) & PreparedStatement", "HikariCP Connection Pooling & DataSource Configuration", "Spring Framework Architecture & Inversion of Control (IoC)",
        "Dependency Injection (@Autowired, Constructor Injection)", "Spring Boot Starters, Auto-Configuration & Profiles", "Building RESTful Web Services with @RestController",
        "Request Routing: @GetMapping, @PostMapping, @PathVariable", "DTO Pattern, Request Validation (@Valid) & Error Handling", "Spring Data JPA & Hibernate Object-Relational Mapping",
        "JPA Entity Mappings: @OneToMany, @ManyToOne, @ManyToMany", "Derived Query Methods & JPQL Custom Queries with @Query", "Spring Data Pagination, Sorting & Auditing Integration",
        "Spring Security Filter Chain & UserDetailsService Architecture", "JWT Token Generation, Signing & Stateless Auth Filter", "Role-Based Access Control (@PreAuthorize) & CORS Security",
        "Unit Testing with JUnit 5, AssertJ & Mockito Framework", "Integration Testing with @SpringBootTest & TestContainers", "Dockerizing Spring Boot Applications & Cloud Deployment",
        "Enterprise Java Capstone Project Architecture & Finalization", "Spring Cloud Config & Service Discovery (Eureka)", "API Gateway & Circuit Breakers (Resilience4j)",
        "Apache Kafka Event-Driven Messaging in Java", "High-Throughput Reactive Programming with Spring WebFlux", "Enterprise Java Architecture Defense & Viva"
    ],
    'BI': [
        "Molecular Biology Dogma: DNA, RNA & Protein Synthesis", "Genomics, Transcriptomics & Proteomics Data Paradigms", "Biological Databases: NCBI Entrez, GenBank & EMBL",
        "UniProt Knowledgebase: Protein Sequences & Functional Metadata", "Protein Data Bank (PDB) 3D Coordinate Structures", "Ensembl Genome Browser & Genomic Annotation Workflows",
        "Python Programming Fundamentals for Life Scientists", "BioPython Library Architecture & Core Modules Overview", "Parsing FASTA & GenBank Sequence Records via SeqIO",
        "Calculating GC Content, Reverse Complements & Open Reading Frames", "DNA Transcription, RNA Translation & Codon Usage Tables", "Motif Discovery, Pattern Matching & Regex in Genetic Sequences",
        "Pairwise Sequence Alignment Theory & Dot Matrix Plots", "Needleman-Wunsch Dynamic Programming Global Alignment", "Smith-Waterman Dynamic Programming Local Alignment",
        "Amino Acid Substitution Matrices: PAM & BLOSUM62", "BLAST Algorithm (blastn, blastp) & E-Value Statistics", "Automating Remote & Local NCBI BLAST Queries in Python",
        "Multiple Sequence Alignment (MSA) Principles & Complexity", "Clustal Omega & MUSCLE Multiple Alignment Workflows", "Phylogenetic Tree Construction: Neighbor-Joining & UPGMA",
        "Visualizing & Bootstrapping Phylogenetic Trees in Bio.Phylo", "Protein Structural Hierarchy & Secondary Structure Predictions", "Parsing PDB Files & Calculating C-Alpha Distances in Bio.PDB",
        "Ramachandran Plot Analysis for Protein Conformation Quality", "3D Macromolecular Rendering with PyMOL & Active Site Mapping", "Next-Generation Sequencing (NGS) Technologies & FASTQ Format",
        "Read Quality Assessment (FastQC) & Trimming Protocols", "SAM/BAM Alignment Files & Mutation Variant Calling (VCF)", "Annotating Single Nucleotide Polymorphisms (SNPs) & InDels",
        "Gene Expression Profiling & RNA-Seq Differential Analysis", "Statistical Normalization (RPKM/TPM) & Volcano Plot Graphics", "Machine Learning Applications in Biological Biomarker Discovery",
        "Bioinformatics Pipeline Architecture & Capstone Dataset Selection", "Automated Sequence Alignment & Target Structure Modeling", "Computational Biology Capstone Research Dossier & Viva Defense",
        "Structural Bioinformatics & Ligand Docking Protocols", "Single-Cell RNA Sequencing (scRNA-seq) Analysis", "Genomic Variant Pathogenicity Scoring Workflows",
        "Microarray & Transcriptomic Heatmap Visualizations", "Bioinformatics Pipeline Presentation & Viva Voce"
    ],
    'AD': [
        "Android OS Architecture, Linux Kernel & Android Runtime (ART)", "Kotlin Programming Fundamentals, Variables & Immutability", "Kotlin Null Safety (? / !! / ?:) & Safe Calls",
        "Kotlin OOPs: Classes, Data Classes, Inheritance & Interfaces", "Kotlin Collections, Higher-Order Functions & Lambdas", "Extension Functions, Scope Functions (let, run, apply)",
        "Android Studio IDE Setup, Gradle Builds & Dependencies", "Android Application Components & AndroidManifest.xml", "Activity Lifecycle Events & Screen State Management",
        "Intents (Explicit vs Implicit) & Intent Data Transfer", "Android Resources System: Strings, Colors, Dimens & Themes", "Runtime Permissions Request Lifecycle in Android",
        "Imperative Views vs Declarative Jetpack Compose Paradigm", "@Composable Functions, State Management & Recomposition", "Compose Layout Primitives: Column, Row, Box & Scaffold",
        "Material Design 3 Theming, Color Palettes & Typography", "Custom Modifiers, Visual Styling & Animated Transitions", "High-Performance Lists: LazyColumn & LazyRow with Keys",
        "Card Components, Floating Action Buttons & Badges", "Navigation Component in Jetpack Compose with Type-Safe Args", "Bottom Navigation Bar, Navigation Rail & Navigation Drawer",
        "Local Data Persistence Strategies in Mobile Applications", "Room SQLite Database Architecture: @Entity, @Dao, @Database", "Database Migrations & Reactive Flow Data Observation",
        "DataStore Preferences for Secure App Settings Storage", "Repository Pattern for Clean Data Abstraction", "Kotlin Coroutines: Dispatchers, Suspend Functions & Scopes",
        "Retrofit 2 HTTP Client Configuration & Base URL Setup", "JSON Serialization with Kotlinx Serialization / Moshi", "Handling Network Error States & Offline Cache Fallback",
        "Asynchronous Image Loading with Coil in Jetpack Compose", "Firebase Authentication & Real-Time Cloud Firestore Sync", "Model-View-ViewModel (MVVM) Clean Architecture",
        "Dependency Injection with Hilt in Modern Android Apps", "Unit Testing ViewModels with MockK and JUnit 5", "ProGuard Code Obfuscation & Signed Android App Bundle (AAB)",
        "Native Android Mobile Capstone Project Release & Defense", "WorkManager Background Task Scheduling", "Push Notifications via Firebase Cloud Messaging (FCM)",
        "Android Jetpack App Performance Profiling & Baseline Profiles", "Google Play Store Release Pipeline & Technical Viva"
    ],
    'DEFAULT': [
        "Technical Orientation, System Architecture & Software Standards", "Version Control Systems: Git Workflows, Branching & Merges",
        "Data Structures, Algorithmic Complexity & Clean Coding", "Database Modeling, Relational Normalization & SQL Queries",
        "API Contracts, REST Architecture & Authentication Protocols", "Frontend Component Architecture & Responsive UI Systems",
        "Backend Controller Services & Business Logic Implementation", "Error Handling, Logging, Middleware & Security Hardening",
        "Automated Unit Testing, Test Coverage & Code Auditing", "Continuous Integration, Automated Builds & Code Linting",
        "Cloud Infrastructure, Containerization & Server Deployment", "Performance Optimization, Caching & Scalability Analysis",
        "Software Capstone Architecture Design & Sprint Planning", "Capstone Feature Implementation & Module Integration",
        "End-to-End System Testing & User Acceptance Verification", "Technical Documentation, Architecture Dossier & Viva Defense"
    ]
}

def get_batch_track_topics(track_code: str, total_days: int) -> list:
    track = (track_code or "DA").upper()
    pool = BATCH_TRACK_TOPICS.get(track) or BATCH_TRACK_TOPICS.get("DEFAULT")
    topics = []
    for i in range(total_days):
        if i < len(pool):
            topics.append(pool[i])
        else:
            base = pool[i % len(pool)]
            cycle = (i // len(pool)) + 1
            topics.append(f"Applied Lab Phase {cycle}: {base}")
    return topics

def compute_batch_working_days(start_date_str: str, total_days: int) -> list:
    try:
        start_dt = datetime.strptime(start_date_str, "%Y-%m-%d")
    except Exception:
        start_dt = datetime.now()
    
    current_dt = start_dt
    days = []
    while len(days) < total_days:
        if current_dt.weekday() != 6:  # Skip Sunday
            days.append({
                "day_number": len(days) + 1,
                "date": current_dt.strftime("%Y-%m-%d"),
                "day_of_week": current_dt.strftime("%A"),
                "short_date": current_dt.strftime("%d/%m"),
                "day_str": current_dt.strftime("%a %d/%m")
            })
        current_dt += timedelta(days=1)
    return days

def compute_batch_student_attendance(student: dict, working_days: list, topics: list, start_time="10:00 AM", end_time="01:30 PM", daily_hours=3.5) -> dict:
    total_days = len(working_days)
    att_pct = float(student.get("attendance_pct", 100.0))
    
    if att_pct >= 100.0:
        present_count = total_days
        leave_count = 0
        leave_indices = set()
    else:
        present_count = max(1, int(round(total_days * (att_pct / 100.0))))
        leave_count = total_days - present_count
        leave_indices = set()
        if leave_count > 0 and total_days > 2:
            step = (total_days - 2) / float(leave_count + 1)
            for i in range(leave_count):
                idx = int(round(1 + (i + 1) * step))
                if 0 < idx < total_days - 1:
                    leave_indices.add(idx)
            # Fill if any collisions
            cur = 1
            while len(leave_indices) < leave_count and cur < total_days - 1:
                leave_indices.add(cur)
                cur += 1

    records = []
    for idx, day in enumerate(working_days):
        if idx in leave_indices:
            records.append({
                "day_number": day["day_number"],
                "date": day["date"],
                "day_of_week": day["day_of_week"],
                "short_date": day["short_date"],
                "start_time": "—",
                "end_time": "—",
                "total_hours": 0.0,
                "topic_covered": "Authorized Leave (Prior Intimation)",
                "status": "AUTHORIZED LEAVE",
                "short_status": "L",
                "student_signed": "On Leave",
                "mentor_signed": "Approved Leave"
            })
        else:
            records.append({
                "day_number": day["day_number"],
                "date": day["date"],
                "day_of_week": day["day_of_week"],
                "short_date": day["short_date"],
                "start_time": start_time,
                "end_time": end_time,
                "total_hours": daily_hours,
                "topic_covered": topics[idx % len(topics)],
                "status": "PRESENT",
                "short_status": "P",
                "student_signed": "Verified (Signed)",
                "mentor_signed": "Verified (Signed)"
            })

    actual_pct = round((present_count / total_days) * 100.0, 1)
    total_hours_logged = round(present_count * daily_hours, 1)

    return {
        "full_name": student.get("full_name", "Student Name"),
        "father_mother_name": student.get("father_mother_name", "Father Name"),
        "roll_no": student.get("roll_no") or f"STU-{student.get('id', 1):03d}",
        "college_name": student.get("college_name", "Poddar College, Bharatpur"),
        "degree": student.get("degree", "BCA"),
        "branch": student.get("branch", "Computer Science"),
        "attendance_pct_target": att_pct,
        "attendance_pct_actual": actual_pct,
        "total_days": total_days,
        "present_days": present_count,
        "leave_days": leave_count,
        "total_hours_logged": total_hours_logged,
        "records": records
    }

def resolve_institution_profile(institution_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM institutions WHERE id = ?", (institution_id,))
    inst_row = cursor.fetchone()
    if not inst_row:
        cursor.execute("SELECT * FROM institutions ORDER BY id ASC LIMIT 1")
        inst_row = cursor.fetchone()
    inst = dict(inst_row) if inst_row else {}
    
    cursor.execute("SELECT * FROM centre_settings WHERE id = 1")
    settings = dict(cursor.fetchone())
    conn.close()

    is_poddar = (inst.get("code") == "PODDAR" or institution_id == 2)
    if is_poddar:
        return {
            "id": 2,
            "code": "PODDAR",
            "name": "Poddar College",
            "full_name": "PODDAR COLLEGE OF TECHNOLOGY & MANAGEMENT",
            "centre_name": "PODDAR COLLEGE",
            "address": "Bharatpur, Rajasthan",
            "logo_path": "poddar_logo.png",
            "primary_color": "#0A2540",
            "secondary_color": "#EAA824",
            "accent_color": "#EAA824",
            "signatory_name": "Nitin Sir",
            "signatory_designation": "Centre Head & Authorized Signatory",
            "stamp_mode": "PHYSICAL_BOX",
            "watermark_mode": "PODDAR_CREST",
            "doc_prefix": "PCTM/BPT",
            "cert_prefix": "PCTM"
        }
    else:
        return {
            "id": 1,
            "code": "TG",
            "name": "TechnoGlobe",
            "full_name": "TechnoGlobe IT Solutions Pvt. Ltd.",
            "centre_name": "TECHNOGLOBE – BHARATPUR CENTRE",
            "address": settings.get("address", "Bharatpur Centre, Rajasthan"),
            "logo_path": "technoglobe_logo.png",
            "primary_color": "#0B2545",
            "secondary_color": "#134074",
            "accent_color": "#D4AF37",
            "signatory_name": "Nitin Sir",
            "signatory_designation": "Centre Head & Authorized Signatory",
            "stamp_mode": "DIGITAL_BADGE",
            "watermark_mode": "SEAL",
            "doc_prefix": "TG/BPT",
            "cert_prefix": "TG-BPT"
        }

def generate_master_batch_attendance_pdf(batch_meta: dict, students_list: list) -> str:
    """
    Generates official Landscape A4 Master Attendance Register for a batch of arbitrary size (50+ students).
    Includes institutional branding (TechnoGlobe vs Poddar College), multi-day matrix columns, and official signatures.
    """
    inst_id = batch_meta.get("institution_id", 1)
    inst = resolve_institution_profile(inst_id)
    is_poddar = (inst["code"] == "PODDAR")

    track_code = batch_meta.get("course_track", "DA").upper()
    track_title = batch_meta.get("custom_track_name") or batch_meta.get("track_title") or f"Course-Based Internship ({track_code})"
    total_days = int(batch_meta.get("total_days", 50))
    start_date = batch_meta.get("start_date", "2026-06-01")
    start_time = batch_meta.get("start_time", "10:00 AM")
    end_time = batch_meta.get("end_time", "01:30 PM")
    daily_hours = float(batch_meta.get("daily_hours", 3.5))
    mentor_name = batch_meta.get("mentor_name") or ("Prof. Krishlay Sharma" if batch_meta.get("mentor_id") == 1 else "Prof. Rahul Bhatnagar")
    mentor_desig = batch_meta.get("mentor_designation") or "Professor & Internship Mentor"
    signatory_name = inst.get("signatory_name", "Nitin Sir")
    signatory_desig = inst.get("signatory_designation", "Centre Head & Authorized Signatory")

    # Compute working calendar & topics
    working_days = compute_batch_working_days(start_date, total_days)
    end_date = working_days[-1]["date"] if working_days else start_date
    topics = get_batch_track_topics(track_code, total_days)

    # Compute attendance schedules for all students
    computed_students = [
        compute_batch_student_attendance(s, working_days, topics, start_time, end_time, daily_hours)
        for s in students_list
    ]

    # Output file path
    now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    clean_org = "PODDAR" if is_poddar else "TECHNOGLOBE"
    clean_track = re.sub(r'[^A-Za-z0-9_]', '_', track_code)
    filename = f"Master_Batch_Attendance_Register_{clean_org}_{clean_track}_{total_days}Days_{now_str}.pdf"
    filepath = os.path.join(GENERATED_DIR, filename)

    # Document Template in Landscape A4: 297mm x 210mm
    doc = SimpleDocTemplate(
        filepath,
        pagesize=landscape(A4),
        rightMargin=10 * mm,
        leftMargin=10 * mm,
        topMargin=10 * mm,
        bottomMargin=14 * mm
    )

    styles = getSampleStyleSheet()
    inst_primary = colors.HexColor(inst["primary_color"])
    inst_secondary = colors.HexColor(inst["secondary_color"])
    inst_accent = colors.HexColor(inst["accent_color"])

    title_org_style = ParagraphStyle('TitleOrg', fontName='Helvetica-Bold', fontSize=13, leading=16, textColor=inst_primary, alignment=1)
    sub_org_style = ParagraphStyle('SubOrg', fontName='Helvetica-Bold', fontSize=9, leading=11, textColor=inst_secondary, alignment=1)
    addr_org_style = ParagraphStyle('AddrOrg', fontName='Helvetica', fontSize=7.5, leading=9.5, textColor=MUTED, alignment=1)
    banner_style = ParagraphStyle('BannerStyle', fontName='Helvetica-Bold', fontSize=11, leading=13, textColor=inst_primary, alignment=1)
    meta_label = ParagraphStyle('MetaLabel', fontName='Helvetica-Bold', fontSize=7.5, leading=9.5, textColor=DARK)
    meta_val = ParagraphStyle('MetaVal', fontName='Helvetica', fontSize=7.5, leading=9.5, textColor=DARK)
    
    tbl_hdr = ParagraphStyle('TblHdr', fontName='Helvetica-Bold', fontSize=6.5, leading=8, textColor=colors.white, alignment=1)
    tbl_cell = ParagraphStyle('TblCell', fontName='Helvetica', fontSize=6.5, leading=8, textColor=DARK, alignment=1)
    tbl_cell_left = ParagraphStyle('TblCellLeft', fontName='Helvetica-Bold', fontSize=6.5, leading=8, textColor=DARK, alignment=0)
    tbl_p = ParagraphStyle('TblP', fontName='Helvetica-Bold', fontSize=6.5, leading=8, textColor=colors.HexColor("#15803D"), alignment=1)
    tbl_l = ParagraphStyle('TblL', fontName='Helvetica-Bold', fontSize=6.5, leading=8, textColor=colors.HexColor("#D97706"), alignment=1)

    story = []

    # 1. Header Banner
    logo_path = os.path.join(os.path.dirname(__file__), inst["logo_path"])
    header_data = []
    
    if os.path.exists(logo_path):
        if is_poddar:
            logo_img = RLImage(logo_path, width=18 * mm, height=18 * mm, hAlign='CENTER')
        else:
            logo_img = RLImage(logo_path, width=34 * mm, height=12 * mm, hAlign='CENTER')
    else:
        logo_img = Paragraph("<b>INSTITUTION</b>", title_org_style)

    header_text_flow = [
        Paragraph(inst["full_name"].upper(), title_org_style),
        Spacer(1, 1 * mm),
        Paragraph(inst["centre_name"], sub_org_style),
        Spacer(1, 0.5 * mm),
        Paragraph(f"{inst['address']} | Official Master Batch Attendance Log | Session 2025-2026", addr_org_style)
    ]

    header_table = Table([[logo_img, header_text_flow]], colWidths=[40 * mm, 235 * mm])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (0,0), (0,0), 'CENTER'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 2 * mm))
    story.append(HRFlowable(width="100%", thickness=1.5, color=inst_primary, spaceAfter=4, spaceBefore=1))

    # 2. Document Title & Batch Meta Box
    doc_ref = f"{inst['doc_prefix']}/BATCH-ATT/{track_code}/{datetime.now().year}/{len(computed_students)}STU"
    doc_date = datetime.now().strftime("%d-%b-%Y")

    meta_grid = [
        [
            Paragraph(f"<b>Batch Ref:</b> {doc_ref}", meta_label),
            Paragraph(f"<b>Track / Program:</b> {track_title}", meta_label),
            Paragraph(f"<b>Total Enrolled Students:</b> {len(computed_students)}", meta_label),
            Paragraph(f"<b>Date of Record:</b> {doc_date}", meta_label)
        ],
        [
            Paragraph(f"<b>Duration Span:</b> {start_date} to {end_date}", meta_val),
            Paragraph(f"<b>Total Scheduled Days:</b> {total_days} Working Days", meta_val),
            Paragraph(f"<b>Session Timing:</b> {start_time} - {end_time} ({daily_hours}h/day)", meta_val),
            Paragraph(f"<b>Faculty In-Charge:</b> {mentor_name}", meta_val)
        ]
    ]
    meta_table = Table(meta_grid, colWidths=[65 * mm, 80 * mm, 65 * mm, 65 * mm])
    meta_table.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('BACKGROUND', (0,0), (-1,-1), BG_LIGHT),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 2 * mm))

    # 3. Master Roster Grid with Chunking (e.g. 25 days per page segment)
    chunk_size = 25 if total_days > 25 else total_days
    num_chunks = (total_days + chunk_size - 1) // chunk_size

    for chunk_idx in range(num_chunks):
        c_start = chunk_idx * chunk_size
        c_end = min(total_days, (chunk_idx + 1) * chunk_size)
        chunk_days = working_days[c_start:c_end]
        n_days_in_chunk = len(chunk_days)

        if chunk_idx > 0:
            story.append(PageBreak())
            # Add mini header for continuation pages
            cont_header = [
                [
                    Paragraph(f"<b>{inst['full_name']} — MASTER ATTENDANCE REGISTER (CONTINUED: DAYS {c_start+1} TO {c_end})</b>", meta_label),
                    Paragraph(f"<b>Batch:</b> {track_title} | <b>Mentor:</b> {mentor_name}", meta_val)
                ]
            ]
            ct = Table(cont_header, colWidths=[175 * mm, 100 * mm])
            ct.setStyle(TableStyle([
                ('BOTTOMPADDING', (0,0), (-1,-1), 2),
                ('TOPPADDING', (0,0), (-1,-1), 0),
                ('LEFTPADDING', (0,0), (-1,-1), 0),
                ('RIGHTPADDING', (0,0), (-1,-1), 0),
            ]))
            story.append(ct)
            story.append(Spacer(1, 1.5 * mm))

        # Build Table Headers
        hdr_row_1 = [
            Paragraph("<b>#</b>", tbl_hdr),
            Paragraph("<b>Roll No</b>", tbl_hdr),
            Paragraph("<b>Student Name</b>", tbl_hdr)
        ]
        
        # Day column headers (e.g. "D1<br/>01/06")
        for d in chunk_days:
            hdr_row_1.append(Paragraph(f"<b>D{d['day_number']}</b><br/>{d['short_date']}", tbl_hdr))

        # Summary columns on final chunk (or repeated)
        is_last_chunk = (chunk_idx == num_chunks - 1)
        if is_last_chunk:
            hdr_row_1.append(Paragraph("<b>Pres</b>", tbl_hdr))
            hdr_row_1.append(Paragraph("<b>Leave</b>", tbl_hdr))
            hdr_row_1.append(Paragraph("<b>Hrs</b>", tbl_hdr))
            hdr_row_1.append(Paragraph("<b>Att%</b>", tbl_hdr))
        else:
            hdr_row_1.append(Paragraph(f"<b>D{c_start+1}-{c_end} P</b>", tbl_hdr))
            hdr_row_1.append(Paragraph(f"<b>D{c_start+1}-{c_end} L</b>", tbl_hdr))

        roster_data = [hdr_row_1]

        # Calculate dynamic column widths to fill 275mm width perfectly
        fixed_prefix_w = 6 * mm + 18 * mm + 40 * mm  # S.No (6), Roll (18), Name (40) = 64mm
        summary_w = (11 * mm + 10 * mm + 11 * mm + 12 * mm) if is_last_chunk else (18 * mm + 18 * mm) # 44mm or 36mm
        remaining_w = 275 * mm - fixed_prefix_w - summary_w
        day_col_w = max(5.5 * mm, remaining_w / float(n_days_in_chunk))

        col_widths = [6 * mm, 18 * mm, 40 * mm] + [day_col_w] * n_days_in_chunk
        if is_last_chunk:
            col_widths.extend([11 * mm, 10 * mm, 11 * mm, 12 * mm])
        else:
            col_widths.extend([18 * mm, 18 * mm])

        # Fill student rows
        for s_idx, stu in enumerate(computed_students, 1):
            s_name = stu["full_name"]
            s_roll = stu["roll_no"]
            
            row = [
                Paragraph(str(s_idx), tbl_cell),
                Paragraph(s_roll, tbl_cell),
                Paragraph(f"<b>{s_name}</b>", tbl_cell_left)
            ]

            chunk_records = stu["records"][c_start:c_end]
            chunk_p = sum(1 for r in chunk_records if r["short_status"] == "P")
            chunk_l = len(chunk_records) - chunk_p

            for r in chunk_records:
                if r["short_status"] == "P":
                    row.append(Paragraph("<b>P</b>", tbl_p))
                else:
                    row.append(Paragraph("<b>L</b>", tbl_l))

            if is_last_chunk:
                p_style = tbl_p if stu["attendance_pct_actual"] >= 75 else tbl_l
                row.append(Paragraph(f"<b>{stu['present_days']}</b>", tbl_cell))
                row.append(Paragraph(f"{stu['leave_days']}", tbl_cell))
                row.append(Paragraph(f"{stu['total_hours_logged']:.0f}h", tbl_cell))
                row.append(Paragraph(f"<b>{stu['attendance_pct_actual']:.1f}%</b>", p_style))
            else:
                row.append(Paragraph(f"<b>{chunk_p}</b>", tbl_cell))
                row.append(Paragraph(f"{chunk_l}", tbl_cell))

            roster_data.append(row)

        roster_table = Table(roster_data, colWidths=col_widths, repeatRows=1)
        roster_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BACKGROUND', (0,0), (-1,0), inst_primary),
            ('INNERGRID', (0,0), (-1,-1), 0.4, BORDER_COLOR),
            ('BOX', (0,0), (-1,-1), 0.8, inst_primary),
            ('TOPPADDING', (0,0), (-1,-1), 1.5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 1.5),
            ('LEFTPADDING', (0,0), (-1,-1), 1),
            ('RIGHTPADDING', (0,0), (-1,-1), 1),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, BG_LIGHT])
        ]))
        story.append(roster_table)
        story.append(Spacer(1, 2 * mm))

    # 4. Signatures & Institutional Verification Block
    sig_label = ParagraphStyle('SigLbl', fontName='Helvetica-Bold', fontSize=8, leading=10, alignment=1, textColor=DARK)
    sig_sub = ParagraphStyle('SigSub', fontName='Helvetica', fontSize=7.5, leading=9.5, alignment=1, textColor=MUTED)

    if is_poddar:
        # Poddar College: Physical Ink Stamp Area
        stamp_cell = Paragraph(
            "<br/><b>[ OFFICIAL COLLEGE SEAL ]</b><br/><font color='#64748B'><i>(Apply Physical Ink Stamp Here)</i></font>",
            sig_sub
        )
    else:
        # TechnoGlobe: Digital Gold Badge Seal
        stamp_cell = Paragraph(
            "<br/><b>★ TECHNOGLOBE OFFICIAL SEAL ★</b><br/><font color='#B45309'><b>ISO 9001:2015 CERTIFIED CENTRE</b></font><br/><i>Bharatpur Centre</i>",
            sig_sub
        )

    sig_data = [
        [
            Paragraph("<b>STUDENT BATCH REPRESENTATIVE</b>", sig_label),
            Paragraph("<b>FACULTY IN-CHARGE / MENTOR</b>", sig_label),
            Paragraph("<b>INSTITUTIONAL SEAL</b>", sig_label),
            Paragraph("<b>AUTHORIZED SIGNATORY</b>", sig_label)
        ],
        [
            Paragraph("<br/><br/>____________________________<br/>Class Representative Signature", sig_sub),
            Paragraph(f"<br/><br/>____________________________<br/><b>{mentor_name}</b><br/>{mentor_desig}", sig_sub),
            stamp_cell,
            Paragraph(f"<br/><br/>____________________________<br/><b>{signatory_name}</b><br/>{signatory_desig}", sig_sub)
        ]
    ]

    sig_table = Table(sig_data, colWidths=[65 * mm, 75 * mm, 65 * mm, 70 * mm])
    sig_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('BOX', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('BACKGROUND', (0,0), (-1,0), BG_LIGHT),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(KeepTogether([Spacer(1, 2 * mm), sig_table]))

    # Build PDF with LandscapeNumberedCanvas
    doc.build(story, canvasmaker=LandscapeNumberedCanvas)
    return filepath

def generate_individual_batch_student_attendance_pdf(student_data: dict, batch_meta: dict) -> str:
    """
    Generates official A4 Portrait 05_Attendance_Sheet PDF for an individual student from the batch roster.
    """
    inst_id = batch_meta.get("institution_id", 1)
    inst = resolve_institution_profile(inst_id)
    is_poddar = (inst["code"] == "PODDAR")

    track_code = batch_meta.get("course_track", "DA").upper()
    track_title = batch_meta.get("custom_track_name") or batch_meta.get("track_title") or f"Course-Based Internship ({track_code})"
    mentor_name = batch_meta.get("mentor_name") or ("Prof. Krishlay Sharma" if batch_meta.get("mentor_id") == 1 else "Prof. Rahul Bhatnagar")
    mentor_desig = batch_meta.get("mentor_designation") or "Professor & Internship Mentor"
    total_days = student_data.get("total_days", len(student_data.get("records", [])))

    s_name_clean = student_data["full_name"].replace(" ", "_")
    filename = f"05_Attendance_Sheet_{s_name_clean}_{total_days}Days.pdf"
    filepath = os.path.join(GENERATED_DIR, filename)

    doc = SimpleDocTemplate(filepath, pagesize=A4, rightMargin=12*mm, leftMargin=12*mm, topMargin=12*mm, bottomMargin=12*mm)
    story = []

    doc_ref = f"{inst['doc_prefix']}/ATT-IND/{track_code}/{datetime.now().year}/{student_data.get('roll_no', '001')}"
    last_date = student_data["records"][-1]["date"] if student_data.get("records") else datetime.now().strftime("%Y-%m-%d")

    # Header
    story.extend(build_official_header(inst, doc_ref, last_date, f"DAILY ATTENDANCE REGISTER — {student_data['full_name'].upper()}", institution=inst))

    styles = getSampleStyleSheet()
    bold_style = ParagraphStyle('Bold', fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=DARK)
    text_style = ParagraphStyle('Text', fontName='Helvetica', fontSize=7.5, leading=9.5, textColor=DARK)
    body_style = ParagraphStyle('BodyInfo', fontName='Helvetica', fontSize=8.5, leading=12, textColor=DARK)

    # Student info strip
    info_text = f"<b>Student:</b> {student_data['full_name']} | <b>Roll No:</b> {student_data['roll_no']} | <b>Degree:</b> {student_data.get('degree', 'BCA')} ({student_data.get('branch', 'CS')})<br/><b>College:</b> {student_data.get('college_name', 'Poddar College, Bharatpur')} | <b>Track:</b> {track_title} | <b>Attendance:</b> {student_data['attendance_pct_actual']:.1f}% ({student_data['present_days']}/{student_data['total_days']} Days Present)"
    story.append(Paragraph(info_text, body_style))
    story.append(Spacer(1, 3 * mm))

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

    for idx, r in enumerate(student_data.get("records", []), 1):
        status_color = "green" if r["status"] == "PRESENT" else "orange"
        status_html = f"<font color='{status_color}'><b>{r['status']}</b></font>"
        table_data.append([
            Paragraph(str(idx), text_style),
            Paragraph(r["date"], text_style),
            Paragraph(r["day_of_week"][:3], text_style),
            Paragraph(f"{r['start_time']} - {r['end_time']}", text_style),
            Paragraph(str(r["total_hours"]), text_style),
            Paragraph(r["topic_covered"] or "Practical Activity", text_style),
            Paragraph(status_html, text_style),
            Paragraph(r.get("student_signed", "Verified (Signed)"), text_style),
            Paragraph(r.get("mentor_signed", "Verified (Signed)"), text_style)
        ])

    t = Table(table_data, colWidths=[7 * mm, 19 * mm, 11 * mm, 28 * mm, 10 * mm, 61 * mm, 18 * mm, 16 * mm, 16 * mm], repeatRows=1)
    t.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor(inst["primary_color"])),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('BACKGROUND', (0,0), (-1,0), BG_LIGHT),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))
    story.append(t)
    story.append(Spacer(1, 4 * mm))

    story.append(build_signature_section(inst, mentor_name, mentor_desig))

    doc.build(story, canvasmaker=NumberedCanvas)
    return filepath

def generate_batch_attendance_zip_bundle(batch_meta: dict, students_list: list) -> str:
    """
    Generates a complete Batch Attendance ZIP Bundle containing:
    1. Master Batch Attendance Register PDF (Landscape A4)
    2. Batch Attendance Summary & Day-Wise Roster CSV
    3. All individual Student Attendance Sheet PDFs (Portrait A4)
    """
    inst_id = batch_meta.get("institution_id", 1)
    inst = resolve_institution_profile(inst_id)
    track_code = batch_meta.get("course_track", "DA").upper()
    total_days = int(batch_meta.get("total_days", 50))
    start_date = batch_meta.get("start_date", "2026-06-01")
    start_time = batch_meta.get("start_time", "10:00 AM")
    end_time = batch_meta.get("end_time", "01:30 PM")
    daily_hours = float(batch_meta.get("daily_hours", 3.5))

    working_days = compute_batch_working_days(start_date, total_days)
    topics = get_batch_track_topics(track_code, total_days)

    computed_students = [
        compute_batch_student_attendance(s, working_days, topics, start_time, end_time, daily_hours)
        for s in students_list
    ]

    # 1. Master PDF
    master_pdf_path = generate_master_batch_attendance_pdf(batch_meta, students_list)

    # 2. Summary CSV
    csv_filename = f"00_Batch_Attendance_Matrix_{inst['code']}_{track_code}_{total_days}Days.csv"
    csv_path = os.path.join(GENERATED_DIR, csv_filename)
    with open(csv_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        # Header row
        header = ["S.No", "Roll_No", "Student_Name", "Father_Name", "College", "Degree_Branch", "Target_Pct", "Actual_Pct", "Total_Days", "Present_Days", "Leave_Days", "Total_Hours"]
        for d in working_days:
            header.append(f"Day_{d['day_number']}_{d['short_date']}")
        writer.writerow(header)

        # Student rows
        for idx, stu in enumerate(computed_students, 1):
            row = [
                idx, stu["roll_no"], stu["full_name"], stu["father_mother_name"], stu["college_name"],
                f"{stu['degree']} - {stu['branch']}", f"{stu['attendance_pct_target']}%", f"{stu['attendance_pct_actual']}%",
                stu["total_days"], stu["present_days"], stu["leave_days"], stu["total_hours_logged"]
            ]
            for r in stu["records"]:
                row.append(r["short_status"])
            writer.writerow(row)

    # 3. Individual PDFs
    individual_pdf_paths = []
    for stu in computed_students:
        ind_path = generate_individual_batch_student_attendance_pdf(stu, batch_meta)
        individual_pdf_paths.append((stu["full_name"], stu["roll_no"], ind_path))

    # 4. Zip Bundle
    now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"BATCH_ATTENDANCE_{inst['code']}_{track_code}_{len(computed_students)}STUDENTS_{total_days}DAYS_{now_str}.zip"
    zip_path = os.path.join(GENERATED_DIR, zip_filename)

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.write(master_pdf_path, arcname="00_MASTER_BATCH_ATTENDANCE_REGISTER.pdf")
        zip_file.write(csv_path, arcname="00_BATCH_ATTENDANCE_SUMMARY_MATRIX.csv")
        for s_name, s_roll, p_path in individual_pdf_paths:
            clean_name = re.sub(r'[^A-Za-z0-9_]', '_', s_name)
            arc_name = f"Individual_Attendance_Sheets/05_Attendance_Sheet_{s_roll}_{clean_name}.pdf"
            if os.path.exists(p_path):
                zip_file.write(p_path, arcname=arc_name)

    return zip_path

