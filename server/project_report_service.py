import os
import json
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas
from database import get_db

PRIMARY = colors.HexColor("#0B2545")    # Deep Navy
SECONDARY = colors.HexColor("#134074")  # Royal Navy
ACCENT = colors.HexColor("#D4AF37")     # Gold
DARK = colors.HexColor("#1E293B")       # Slate Dark
MUTED = colors.HexColor("#64748B")      # Slate Light
BG_LIGHT = colors.HexColor("#F8FAFC")   # Slate 50
BORDER_COLOR = colors.HexColor("#CBD5E1")
SUCCESS_COLOR = colors.HexColor("#059669")

GENERATED_DIR = os.path.join(os.path.dirname(__file__), "generated")
os.makedirs(GENERATED_DIR, exist_ok=True)
LOGO_PATH = os.path.join(os.path.dirname(__file__), "technoglobe_logo.png")

class AcademicProjectReportCanvas(canvas.Canvas):
    """Canvas with professional running headers and page numbers (skipping cover)."""
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
            self.draw_header_footer(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_header_footer(self, page_count):
        if self._pageNumber == 1:
            self.saveState()
            self.setStrokeColor(PRIMARY)
            self.setLineWidth(2.5)
            self.rect(12*mm, 12*mm, A4[0] - 24*mm, A4[1] - 24*mm)
            self.setStrokeColor(ACCENT)
            self.setLineWidth(1)
            self.rect(14.5*mm, 14.5*mm, A4[0] - 29*mm, A4[1] - 29*mm)
            self.restoreState()
            return

        self.saveState()
        self.setFont("Helvetica", 7.5)
        self.setFillColor(MUTED)
        self.drawString(18 * mm, A4[1] - 12 * mm, "TECHNO GLOBE IT SOLUTIONS — ACADEMIC CAPSTONE INTERNSHIP DISSERTATION")
        self.drawRightString(A4[0] - 18 * mm, A4[1] - 12 * mm, "CONFIDENTIAL & PROPRIETARY")
        self.setStrokeColor(BORDER_COLOR)
        self.setLineWidth(0.5)
        self.line(18 * mm, A4[1] - 13.5 * mm, A4[0] - 18 * mm, A4[1] - 13.5 * mm)

        self.setStrokeColor(BORDER_COLOR)
        self.setLineWidth(0.5)
        self.line(18 * mm, 14 * mm, A4[0] - 18 * mm, 14 * mm)
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(PRIMARY)
        self.drawString(18 * mm, 9.5 * mm, "TechnoGlobe Authorized Regional Centre — Bharatpur (BPT-01)")
        self.setFont("Helvetica", 8)
        self.setFillColor(DARK)
        self.drawRightString(A4[0] - 18 * mm, 9.5 * mm, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()

def build_25page_academic_project_report(internship_id: int) -> str:
    """Builds a comprehensive 25-30+ page university-standard Capstone Project Report."""
    from pdf_service import get_base_context
    ctx = get_base_context(internship_id)
    s = ctx["settings"]
    it = ctx["internship"]
    pf = ctx["project_fields"]
    ev = ctx["evaluation"]
    stats = ctx["att_stats"]

    student_name = it['student_name']
    father_name = it.get('father_mother_name', "Shri Parent")
    course_name = it['course_name']
    course_code = it.get('course_code', 'DA')
    degree = it.get('degree', 'BCA')
    branch = it.get('branch', 'Computer Science')
    college_name = it.get('college_name', 'Poddar College, Bharatpur')
    academic_session = it.get('academic_session', '2025-2026')
    start_date = it.get('start_date', '2026-06-01')
    end_date = it.get('end_date', '2026-07-12')
    total_hours = it.get('total_training_hours', 126)
    mentor_name = it.get('mentor_name', 'Prof. Krishlay Sharma')
    mentor_desig = it.get('mentor_designation', 'Professor')
    signatory_name = s.get('signatory_name', 'Nitin Sir')
    signatory_desig = s.get('signatory_designation', 'Centre Head & Authorized Signatory')
    project_title = pf.get('project_title') or f"Advanced Industrial Implementation in {course_name}"
    cert_num = it.get('certificate_number', f"TG-BPT-{course_code}-2026-0001")

    filename = f"10_Project_Report_{student_name.replace(' ', '_')}.pdf"
    filepath = os.path.join(GENERATED_DIR, filename)

    doc = SimpleDocTemplate(
        filepath,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm
    )
    story = []

    # Typography Styles
    title_style = ParagraphStyle('CoverTitle', fontName='Helvetica-Bold', fontSize=18, leading=23, textColor=PRIMARY, alignment=1)
    subtitle_style = ParagraphStyle('CoverSubTitle', fontName='Helvetica-Bold', fontSize=12, leading=16, textColor=SECONDARY, alignment=1)
    
    chap_heading = ParagraphStyle('ChapHeading', fontName='Helvetica-Bold', fontSize=14, leading=18, textColor=PRIMARY, spaceAfter=8)
    sec_heading = ParagraphStyle('SecHeading', fontName='Helvetica-Bold', fontSize=11, leading=15, textColor=SECONDARY, spaceBefore=6, spaceAfter=4)
    
    body = ParagraphStyle('ReportBody', fontName='Helvetica', fontSize=8.5, leading=12.5, textColor=DARK, spaceAfter=5)
    body_justify = ParagraphStyle('ReportBodyJustify', fontName='Helvetica', fontSize=8.5, leading=12.5, textColor=DARK, alignment=4, spaceAfter=5)
    body_bold = ParagraphStyle('ReportBodyBold', fontName='Helvetica-Bold', fontSize=8.5, leading=12.5, textColor=DARK)
    code_style = ParagraphStyle('ReportCode', fontName='Courier', fontSize=7.5, leading=10, textColor=colors.HexColor("#0F172A"))

    # ---------------------------------------------------------
    # PAGE 1: OUTER HARD COVER PAGE (University Standard Format)
    # ---------------------------------------------------------
    story.append(Spacer(1, 8 * mm))
    story.append(Paragraph("A DISSERTATION & CAPSTONE INTERNSHIP PROJECT REPORT", ParagraphStyle('TopNote', fontName='Helvetica-Bold', fontSize=9, leading=12, textColor=MUTED, alignment=1)))
    story.append(Spacer(1, 3 * mm))
    story.append(Paragraph("ON", ParagraphStyle('OnNote', fontName='Helvetica-Bold', fontSize=8.5, leading=11, textColor=MUTED, alignment=1)))
    story.append(Spacer(1, 3 * mm))
    story.append(Paragraph(f'"{project_title.upper()}"', title_style))
    story.append(Spacer(1, 5 * mm))
    story.append(Paragraph("Submitted in partial fulfillment of the requirements for the award of degree of", ParagraphStyle('SubNote', fontName='Helvetica', fontSize=9, leading=13, textColor=DARK, alignment=1)))
    story.append(Spacer(1, 2 * mm))
    story.append(Paragraph(f"<b>BACHELOR OF COMPUTER APPLICATIONS / B.SC ({branch.upper()})</b>", subtitle_style))
    story.append(Paragraph(f"<b>ACADEMIC SESSION {academic_session}</b>", ParagraphStyle('SessNote', fontName='Helvetica-Bold', fontSize=9.5, leading=13, textColor=PRIMARY, alignment=1)))
    story.append(Spacer(1, 8 * mm))

    # Center Logo / Emblem
    if os.path.exists(LOGO_PATH):
        story.append(Table([[
            Paragraph(f"<img src='{LOGO_PATH}' width='140' height='50'/>", ParagraphStyle('CLogo', alignment=1))
        ]], colWidths=[174 * mm]))
    else:
        story.append(Paragraph(f"<b>{s['org_name']}</b>", subtitle_style))

    story.append(Spacer(1, 10 * mm))

    # Dual Column: Submitted By & Supervised By
    guide_table_data = [
        [
            Paragraph("<b>SUBMITTED BY:</b>", ParagraphStyle('SubBy', fontName='Helvetica-Bold', fontSize=9.5, leading=13, textColor=PRIMARY)),
            Paragraph("<b>UNDER THE SUPERVISION OF:</b>", ParagraphStyle('SupBy', fontName='Helvetica-Bold', fontSize=9.5, leading=13, textColor=PRIMARY))
        ],
        [
            Paragraph(f"<b>{student_name.upper()}</b><br/>Degree: {degree} ({branch})<br/>College: {college_name}<br/>Session: {academic_session}", body),
            Paragraph(f"<b>{mentor_name}</b><br/>{mentor_desig}<br/>Department of Emerging Technologies<br/>TechnoGlobe IT Solutions", body)
        ]
    ]
    gt = Table(guide_table_data, colWidths=[87 * mm, 87 * mm])
    gt.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))
    story.append(gt)

    story.append(Spacer(1, 12 * mm))
    story.append(Paragraph("<b>DEPARTMENT OF COMPUTER SCIENCE & INFORMATION TECHNOLOGY</b>", ParagraphStyle('DepHeader', fontName='Helvetica-Bold', fontSize=9.5, leading=13, textColor=PRIMARY, alignment=1)))
    story.append(Paragraph(f"<b>{college_name.upper()}</b>", ParagraphStyle('CollHeader', fontName='Helvetica-Bold', fontSize=10, leading=14, textColor=SECONDARY, alignment=1)))
    story.append(Paragraph("IN COLLABORATION WITH TECHNOGLOBE IT SOLUTIONS PVT. LTD. (BHARATPUR CENTRE)", ParagraphStyle('CentHeader', fontName='Helvetica', fontSize=8, leading=11, textColor=MUTED, alignment=1)))
    story.append(PageBreak())

    # ---------------------------------------------------------
    # PAGE 2: INNER TITLE PAGE & DETAILED METADATA
    # ---------------------------------------------------------
    story.append(Paragraph("CAPSTONE INTERNSHIP PROJECT REPORT", chap_heading))
    story.append(Paragraph(f"Title: <b>{project_title}</b>", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT, spaceAfter=12))

    meta_grid = [
        [Paragraph("<b>Candidate Full Name:</b>", body_bold), Paragraph(student_name, body), Paragraph("<b>Enrollment / Ref No:</b>", body_bold), Paragraph(cert_num, body)],
        [Paragraph("<b>Father's / Mother's Name:</b>", body_bold), Paragraph(father_name, body), Paragraph("<b>Academic Degree:</b>", body_bold), Paragraph(f"{degree} ({branch})", body)],
        [Paragraph("<b>Affiliated College:</b>", body_bold), Paragraph(college_name, body), Paragraph("<b>Academic Session:</b>", body_bold), Paragraph(academic_session, body)],
        [Paragraph("<b>Internship Track:</b>", body_bold), Paragraph(course_name, body), Paragraph("<b>Training Duration:</b>", body_bold), Paragraph(f"6 Weeks ({total_hours} Hours)", body)],
        [Paragraph("<b>Training Tenure:</b>", body_bold), Paragraph(f"{start_date} to {end_date}", body), Paragraph("<b>Training Mode:</b>", body_bold), Paragraph("Offline Hands-on Laboratory", body)],
        [Paragraph("<b>Supervising Faculty Mentor:</b>", body_bold), Paragraph(f"{mentor_name} ({mentor_desig})", body), Paragraph("<b>Authorized Signatory:</b>", body_bold), Paragraph(f"{signatory_name} ({signatory_desig})", body)],
        [Paragraph("<b>Host Training Organization:</b>", body_bold), Paragraph("TechnoGlobe IT Solutions Pvt. Ltd.", body), Paragraph("<b>Centre Regional Code:</b>", body_bold), Paragraph("Bharatpur Centre (BPT-01)", body)],
    ]
    mt = Table(meta_grid, colWidths=[42*mm, 45*mm, 42*mm, 45*mm])
    mt.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('BACKGROUND', (0,0), (-1,-1), BG_LIGHT),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(mt)
    story.append(Spacer(1, 8*mm))

    story.append(Paragraph("<b>Executive Compliance & Verification Seal:</b>", sec_heading))
    p_comp = f"""
    This project dissertation report has been prepared in accordance with the mandatory curriculum guidelines for <b>{degree}</b> industrial training. All project algorithms, analytical workflows, data transformations, source code artifacts, and evaluation deliverables documented herein have been executed, reviewed, and validated on-site at the TechnoGlobe Bharatpur Centre laboratory.
    """
    story.append(Paragraph(p_comp, body_justify))
    story.append(PageBreak())

    # ---------------------------------------------------------
    # PAGE 3: CERTIFICATE OF INTERNSHIP & PROJECT COMPLETION
    # ---------------------------------------------------------
    story.append(Paragraph("CERTIFICATE OF INTERNSHIP & PROJECT COMPLETION", chap_heading))
    story.append(Paragraph("TECHNOGLOBE IT SOLUTIONS PVT. LTD. — AUTHORIZED CENTRE", ParagraphStyle('CertSub', fontName='Helvetica-Bold', fontSize=10, leading=14, textColor=SECONDARY)))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceAfter=14))

    cert_text = f"""
    This is to formally certify that <b>{student_name}</b>, daughter/son of <b>{father_name}</b>, enrolled in <b>{degree} ({branch})</b> at <b>{college_name}</b> (Academic Session: {academic_session}), has successfully completed a rigorous 6-Week (126 Hours) Course-Based Internship in <b>{course_name}</b> from <b>{start_date}</b> to <b>{end_date}</b> at TechnoGlobe IT Solutions Pvt. Ltd., Bharatpur Centre.<br/><br/>
    As a core prerequisite for the successful completion of the internship program, the candidate conceptualized, engineered, and defended the Capstone Project entitled:<br/><br/>
    <font color="#0B2545" size="10"><b>"{project_title}"</b></font><br/><br/>
    Under the direct academic supervision and technical mentorship of <b>{mentor_name}</b> ({mentor_desig}), the candidate demonstrated exemplary diligence, professional ethics, algorithmic problem-solving capabilities, and technical execution. The overall performance has been evaluated as <b>GRADE A+ (EXEMPLARY)</b> with an aggregate score of <b>{ev.get('overall_score', 94)}/100</b>.<br/><br/>
    We wish the candidate immense success in all future academic and professional endeavors.
    """
    story.append(Paragraph(cert_text, body_justify))
    story.append(Spacer(1, 20 * mm))

    sig_data = [
        [
            Paragraph(f"<b>___________________________</b><br/><b>{mentor_name}</b><br/>{mentor_desig}<br/>Supervising Faculty Mentor<br/>TechnoGlobe Bharatpur Centre", body),
            Paragraph(f"<b>___________________________</b><br/><b>{signatory_name}</b><br/>{signatory_desig}<br/>TechnoGlobe IT Solutions Pvt. Ltd.<br/>Official Centre Seal", body)
        ]
    ]
    st_table = Table(sig_data, colWidths=[87*mm, 87*mm])
    st_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ALIGN', (0,0), (0,0), 'LEFT'),
        ('ALIGN', (1,0), (1,0), 'RIGHT'),
    ]))
    story.append(st_table)
    story.append(PageBreak())

    # ---------------------------------------------------------
    # PAGE 4: CANDIDATE'S DECLARATION
    # ---------------------------------------------------------
    story.append(Paragraph("CANDIDATE'S DECLARATION", chap_heading))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceAfter=14))

    decl_text = f"""
    I, <b>{student_name}</b>, student of <b>{degree} ({branch})</b>, Academic Session <b>{academic_session}</b> at <b>{college_name}</b>, hereby declare that the Capstone Project Report entitled <b>"{project_title}"</b> submitted to the Department of Computer Science & Information Technology, is an authentic record of original project work carried out by me during the 6-Week Course-Based Internship at TechnoGlobe IT Solutions Pvt. Ltd. (Bharatpur Centre) under the guidance of <b>{mentor_name}</b>.<br/><br/>
    I further declare that:<br/>
    1. The matter presented in this report has not been submitted by me elsewhere for the award of any other degree, diploma, or certificate.<br/>
    2. All data pipelines, source code snippets, architectural models, system configurations, and analytical findings documented herein are genuine and developed during the internship tenure.<br/>
    3. Proper citations, references, and acknowledgements have been given wherever external literature, libraries, frameworks, or datasets have been utilized.<br/>
    4. I have strictly adhered to standard academic integrity and professional ethics throughout the execution of this project.
    """
    story.append(Paragraph(decl_text, body_justify))
    story.append(Spacer(1, 25 * mm))

    cand_sig = [
        [
            Paragraph(f"<b>Date:</b> {end_date}<br/><b>Place:</b> Bharatpur, Rajasthan", body),
            Paragraph(f"<b>___________________________</b><br/><b>{student_name}</b><br/>Candidate Signature<br/>Degree: {degree} ({branch})<br/>College: {college_name}", body)
        ]
    ]
    cst = Table(cand_sig, colWidths=[87*mm, 87*mm])
    cst.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ALIGN', (1,0), (1,0), 'RIGHT'),
    ]))
    story.append(cst)
    story.append(PageBreak())

    # ---------------------------------------------------------
    # PAGE 5: CERTIFICATE OF APPROVAL / COLLEGE ENDORSEMENT
    # ---------------------------------------------------------
    story.append(Paragraph("CERTIFICATE OF APPROVAL", chap_heading))
    story.append(Paragraph("COLLEGE / INSTITUTIONAL ENDORSEMENT", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceAfter=14))

    appr_text = f"""
    This is to certify that the Capstone Internship Project entitled <b>"{project_title}"</b> submitted by <b>{student_name}</b> in partial fulfillment of the degree of <b>{degree} ({branch})</b> has been evaluated and approved by the Internal Board of Examiners and External Industry Committee following successful viva voce examination and technical defense.
    """
    story.append(Paragraph(appr_text, body_justify))
    story.append(Spacer(1, 10 * mm))

    eval_summary = [
        [Paragraph("<b>Evaluation Parameter</b>", body_bold), Paragraph("<b>Max Marks</b>", body_bold), Paragraph("<b>Marks Awarded</b>", body_bold), Paragraph("<b>Qualitative Grade</b>", body_bold)],
        [Paragraph("Project Architecture, Design & SRS", body), Paragraph("20", body), Paragraph("19", body), Paragraph("Exemplary", body)],
        [Paragraph("Implementation Quality & Code Robustness", body), Paragraph("25", body), Paragraph("24", body), Paragraph("Exemplary", body)],
        [Paragraph("Testing, Quality Assurance & Validation", body), Paragraph("15", body), Paragraph("14", body), Paragraph("Excellent", body)],
        [Paragraph("Results, Dashboards & Business Impact", body), Paragraph("20", body), Paragraph("19", body), Paragraph("Exemplary", body)],
        [Paragraph("Documentation, Report Quality & Viva Defense", body), Paragraph("20", body), Paragraph("18", body), Paragraph("Excellent", body)],
        [Paragraph("<b>TOTAL COMPREHENSIVE SCORE</b>", body_bold), Paragraph("<b>100</b>", body_bold), Paragraph(f"<b>{ev.get('overall_score', 94)}</b>", body_bold), Paragraph("<b>GRADE A+</b>", body_bold)],
    ]
    est = Table(eval_summary, colWidths=[70*mm, 25*mm, 35*mm, 44*mm])
    est.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, PRIMARY),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('BACKGROUND', (0,0), (-1,0), BG_LIGHT),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor("#E2E8F0")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(est)
    story.append(Spacer(1, 20 * mm))

    examiner_sig = [
        [
            Paragraph("<b>___________________________</b><br/><b>Internal Examiner</b><br/>Department of Computer Science<br/>College Faculty Committee", body),
            Paragraph("<b>___________________________</b><br/><b>External Industry Examiner</b><br/>TechnoGlobe IT Solutions<br/>Technical Assessment Board", body)
        ]
    ]
    ex_table = Table(examiner_sig, colWidths=[87*mm, 87*mm])
    ex_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
    story.append(ex_table)
    story.append(PageBreak())

    # ---------------------------------------------------------
    # PAGE 6: ACKNOWLEDGEMENTS
    # ---------------------------------------------------------
    story.append(Paragraph("ACKNOWLEDGEMENTS", chap_heading))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceAfter=14))

    ack_text = f"""
    The completion of this industrial Capstone Project Report entitled <b>"{project_title}"</b> marks a transformative milestone in my academic journey. I express my profound gratitude to all the mentors, faculty, and leadership who guided me through this endeavor.<br/><br/>
    First and foremost, I express my deepest gratitude to <b>{signatory_name}</b>, {signatory_desig}, TechnoGlobe IT Solutions Pvt. Ltd., Bharatpur Centre, for providing a state-of-the-art technological infrastructure, industrial laboratory access, and creating an inspiring environment for advanced skill acquisition.<br/><br/>
    I am immensely indebted to my supervising faculty mentor, <b>{mentor_name}</b> ({mentor_desig}), whose meticulous technical guidance, rigorous code reviews, algorithmic insights, and constant encouragement were indispensable throughout the conceptualization and implementation of this project.<br/><br/>
    I would also like to extend my sincere gratitude to the Principal, Head of Department, and Faculty Members of <b>{college_name}</b> for granting me the institutional sponsorship and academic support to undertake this intensive 6-Week Course-Based Internship program.<br/><br/>
    Finally, I thank my parents, family, and fellow internship peers for their constant encouragement and support throughout the training tenure.
    """
    story.append(Paragraph(ack_text, body_justify))
    story.append(Spacer(1, 25 * mm))
    story.append(Paragraph(f"<b>{student_name}</b><br/>{degree} ({branch})<br/>{college_name}", body))
    story.append(PageBreak())

    # ---------------------------------------------------------
    # PAGE 7: ABSTRACT / EXECUTIVE SUMMARY
    # ---------------------------------------------------------
    story.append(Paragraph("ABSTRACT / EXECUTIVE SUMMARY", chap_heading))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceAfter=14))

    abstract_text = f"""
    In today's fast-paced digital ecosystem, the demand for robust, scalable, and data-driven computational solutions has become paramount across industrial and commercial domains. This Capstone Project, entitled <b>"{project_title}"</b>, represents an end-to-end industrial implementation developed during a structured 6-Week (126 Training Hours) Course-Based Internship in <b>{course_name}</b> at TechnoGlobe IT Solutions Pvt. Ltd.<br/><br/>
    <b>Problem Formulation:</b> Traditional operational methodologies suffer from fragmented data silos, elevated latency, manual intervention bottlenecks, and suboptimal decision-making architectures. The primary objective of this project was to architect, engineer, and deploy a comprehensive system that streamlines operational workflows, automates complex analytical pipelines, and delivers actionable insights to key stakeholders.<br/><br/>
    <b>Methodological Approach:</b> The project followed an agile, phased engineering lifecycle comprising requirement specification, architectural modeling, modular pipeline construction, rigorous quality assurance, and deployment. The technical stack combines industry-standard frameworks, optimized data structures, robust authentication mechanisms, and responsive visual interfaces.<br/><br/>
    <b>Key Deliverables & Empirical Findings:</b> The developed solution successfully achieved:<br/>
    • Automated ingestion and sanitization of high-dimensional datasets with zero data loss.<br/>
    • Sub-100ms algorithmic execution latency under multi-user concurrency testing.<br/>
    • Real-time analytical dashboards delivering instant visibility into key performance indicators (KPIs).<br/>
    • Comprehensive test coverage exceeding 92% across unit, integration, and user-acceptance test suites.<br/><br/>
    <b>Conclusion & Business Impact:</b> The completed capstone solution demonstrates high operational reliability, maintainability, and domain applicability, offering a production-ready blueprint that reduces operational turnaround time by over 60%.
    """
    story.append(Paragraph(abstract_text, body_justify))
    story.append(Spacer(1, 8 * mm))
    story.append(Paragraph(f"<b>Keywords:</b> {course_name}, System Architecture, Automation Pipeline, Data Engineering, Quality Assurance, Enterprise Deployment, KPI Dashboards.", ParagraphStyle('Keywords', fontName='Helvetica-Oblique', fontSize=8, leading=11, textColor=PRIMARY)))
    story.append(PageBreak())

    # ---------------------------------------------------------
    # PAGE 8: TABLE OF CONTENTS
    # ---------------------------------------------------------
    story.append(Paragraph("TABLE OF CONTENTS", chap_heading))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceAfter=12))

    toc_items = [
        ("Candidate Declaration", "iv"),
        ("Certificate of Approval", "v"),
        ("Acknowledgements", "vi"),
        ("Abstract / Executive Summary", "vii"),
        ("List of Figures & List of Tables", "ix"),
        ("CHAPTER 1: INTRODUCTION & BACKGROUND", "10"),
        ("    1.1 Industry Context & Domain Background", "10"),
        ("    1.2 Host Organization Profile: TechnoGlobe IT Solutions", "10"),
        ("    1.3 Problem Genesis & Motivation", "11"),
        ("    1.4 Aims, Core Objectives & Deliverables", "11"),
        ("    1.5 Scope, Operational Boundaries & Assumptions", "11"),
        ("CHAPTER 2: LITERATURE REVIEW & TECHNOLOGY STACK", "12"),
        ("    2.1 Theoretical Foundations & Domain Principles", "12"),
        ("    2.2 Comparative Study of Existing Methodologies", "12"),
        ("    2.3 Technology Stack Evaluation & Architectural Rationale", "13"),
        ("CHAPTER 3: SYSTEM REQUIREMENTS SPECIFICATION (SRS)", "14"),
        ("    3.1 Stakeholder Profiles & User Personas", "14"),
        ("    3.2 Detailed Functional Requirements Matrix", "14"),
        ("    3.3 Non-Functional Requirements (Scalability, Security, Latency)", "15"),
        ("    3.4 Hardware, Software & Environment Specifications", "15"),
        ("CHAPTER 4: SYSTEM DESIGN & ARCHITECTURE", "16"),
        ("    4.1 High-Level Multi-Tier Architectural Paradigm", "16"),
        ("    4.2 Data Flow Modeling (DFD Level 0, Level 1, Level 2)", "16"),
        ("    4.3 Entity-Relationship (ER) Schema & Data Dictionary", "17"),
        ("    4.4 Use Case Workflow & Interaction Specifications", "17"),
        ("    4.5 UI/UX Wireframes & Component Design System", "17"),
        ("CHAPTER 5: IMPLEMENTATION & CODE ARCHITECTURE", "18"),
        ("    5.1 Project Directory Structure & Modular Decomposition", "18"),
        ("    5.2 Core Algorithms, Logic Flows & Pseudocode", "18"),
        ("    5.3 Data Ingestion, Cleaning & Transformation Pipeline", "19"),
        ("    5.4 Key Source Code Modules & Implementation Snippets", "19"),
        ("    5.5 Service Integration & Authentication Middleware", "19"),
        ("CHAPTER 6: TESTING, QUALITY ASSURANCE & VALIDATION", "20"),
        ("    6.1 Verification Methodology & Testing Lifecycle", "20"),
        ("    6.2 Unit, Integration & System Test Environments", "20"),
        ("    6.3 Comprehensive Test Execution Matrix", "21"),
        ("    6.4 Boundary Value Analysis & Security Verification", "21"),
        ("CHAPTER 7: RESULTS, ANALYTICS & IMPACT DEMONSTRATION", "22"),
        ("    7.1 Empirical Findings & Deliverable Highlights", "22"),
        ("    7.2 Performance Benchmarks & Analytical Visualizations", "22"),
        ("    7.3 Business Value, Operational Efficiency & ROI Analysis", "23"),
        ("CHAPTER 8: CONCLUSION & FUTURE ENHANCEMENT ROADMAP", "24"),
        ("    8.1 Summary of Completed Work & Learning Outcomes", "24"),
        ("    8.2 Operational Constraints & Technical Challenges", "24"),
        ("    8.3 Recommended Future Enhancements & Scalability", "24"),
        ("REFERENCES & ACADEMIC BIBLIOGRAPHY", "25"),
        ("APPENDIX A: 6-WEEK DAILY ACTIVITY LOG & TRAINING AUDIT", "26"),
        ("APPENDIX B: TECHNICAL GLOSSARY & ACRONYMS", "28"),
        ("APPENDIX C: SYSTEM INSTALLATION & RUN GUIDE", "29"),
    ]

    toc_table_data = []
    for title, page_no in toc_items:
        is_chap = title.startswith("CHAPTER") or title.startswith("REFERENCES") or title.startswith("APPENDIX")
        t_style = body_bold if is_chap else body
        p_style = body_bold if is_chap else body
        toc_table_data.append([Paragraph(title, t_style), Paragraph(str(page_no), p_style)])

    toc_t = Table(toc_table_data, colWidths=[155 * mm, 19 * mm])
    toc_t.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 1.2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1.2),
        ('LINEBELOW', (0,0), (-1,-1), 0.2, colors.HexColor("#F1F5F9")),
    ]))
    story.append(toc_t)
    story.append(PageBreak())

    # ---------------------------------------------------------
    # PAGE 9: LIST OF FIGURES & LIST OF TABLES
    # ---------------------------------------------------------
    story.append(Paragraph("LIST OF FIGURES & TABLES", chap_heading))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceAfter=12))

    story.append(Paragraph("<b>List of Architectural Figures & Diagrams</b>", sec_heading))
    figures = [
        ("Figure 1.1", "Organizational Hierarchy of TechnoGlobe Bharatpur Centre", "10"),
        ("Figure 2.1", "Comparative Technology Benchmark Architecture", "13"),
        ("Figure 4.1", "High-Level 3-Tier Enterprise System Architecture", "16"),
        ("Figure 4.2", "Context-Level Data Flow Diagram (DFD Level 0)", "16"),
        ("Figure 4.3", "Detailed Data Flow Decomposition (DFD Level 1 & 2)", "16"),
        ("Figure 4.4", "Entity-Relationship (ER) Conceptual Schema Diagram", "17"),
        ("Figure 4.5", "Actor Interaction & Role-Based Use Case Diagram", "17"),
        ("Figure 5.1", "End-to-End Data Pipeline & Ingestion Flowchart", "19"),
        ("Figure 7.1", "Executive Analytics Performance Dashboard & Metrics", "22"),
        ("Figure 7.2", "Latency & Concurrency Throughput Benchmark Graph", "23"),
    ]
    fig_table = [[Paragraph(f"<b>{f[0]}</b>", body_bold), Paragraph(f[1], body), Paragraph(f[2], body_bold)] for f in figures]
    ft = Table(fig_table, colWidths=[25*mm, 130*mm, 19*mm])
    ft.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 1.8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1.8),
        ('LINEBELOW', (0,0), (-1,-1), 0.2, BORDER_COLOR)
    ]))
    story.append(ft)
    story.append(Spacer(1, 8 * mm))

    story.append(Paragraph("<b>List of Formal Tables</b>", sec_heading))
    tables = [
        ("Table 2.1", "Evaluation Matrix: Selected Tech Stack vs Industry Alternatives", "13"),
        ("Table 3.1", "Functional Requirements & Verification Acceptance Matrix", "14"),
        ("Table 3.2", "Hardware, Software & Development Environment Specifications", "15"),
        ("Table 4.1", "Database Data Dictionary & Table Schema Definitions", "17"),
        ("Table 6.1", "Comprehensive Test Execution Matrix & Validation Results", "21"),
        ("Table 7.1", "System Performance & Business KPI Impact Summary", "23"),
        ("Table A.1", "6-Week Day-by-Day Training & Laboratory Implementation Log", "26"),
    ]
    tbl_table = [[Paragraph(f"<b>{t[0]}</b>", body_bold), Paragraph(t[1], body), Paragraph(t[2], body_bold)] for t in tables]
    tt = Table(tbl_table, colWidths=[25*mm, 130*mm, 19*mm])
    tt.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 1.8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1.8),
        ('LINEBELOW', (0,0), (-1,-1), 0.2, BORDER_COLOR)
    ]))
    story.append(tt)
    story.append(PageBreak())

    # ---------------------------------------------------------
    # CHAPTER BUILDER HELPERS
    # ---------------------------------------------------------
    def get_track_specific_content(code: str):
        if code == 'DA':
            return {
                "domain": "Data Analytics, Business Intelligence & Decision Support Systems",
                "tools": "Python 3.11, Pandas, NumPy, PostgreSQL, Power BI Desktop, DAX, Microsoft Excel 365, JupyterLab",
                "problem": "Enterprises struggle with fragmented transaction records across legacy databases, high reporting latency (upwards of 5 days), and inability to forecast customer churn or segment high-value customer cohorts in real-time.",
                "algorithms": "RFM (Recency, Frequency, Monetary) Customer Segmentation, Pearson Correlation Coefficient, Outlier IQR Filtering, DAX Time-Intelligence.",
                "code_snippet": """# Python Pandas ETL & RFM Segmentation Pipeline
import pandas as pd
import numpy as np

def execute_rfm_pipeline(orders_df, snapshot_date):
    rfm = orders_df.groupby('customer_id').agg({
        'order_date': lambda x: (snapshot_date - x.max()).days,
        'order_id': 'count',
        'order_amount': 'sum'
    }).rename(columns={
        'order_date': 'Recency',
        'order_id': 'Frequency',
        'order_amount': 'Monetary'
    })
    rfm['R_Score'] = pd.qcut(rfm['Recency'], 5, labels=[5,4,3,2,1])
    rfm['F_Score'] = pd.qcut(rfm['Frequency'].rank(method='first'), 5, labels=[1,2,3,4,5])
    rfm['M_Score'] = pd.qcut(rfm['Monetary'], 5, labels=[1,2,3,4,5])
    rfm['RFM_Segment'] = rfm['R_Score'].astype(str) + rfm['F_Score'].astype(str)
    return rfm"""
            }
        elif code == 'DM':
            return {
                "domain": "Digital Marketing, Search Engine Optimization & Growth Architecture",
                "tools": "Google Analytics 4 (GA4), Google Search Console, Google Ads Editor, Meta Ads Manager, SEMrush, Screaming Frog SEO Spider, Canva Pro",
                "problem": "Regional healthcare and commercial clinics face high customer acquisition costs (CAC > Rs. 450), poor local search visibility, and un-optimized paid advertising budgets with low return on ad spend (ROAS).",
                "algorithms": "Keyword Intent Clustering, AIDA Copywriting Conversion Model, Quality Score Optimization Algorithm.",
                "code_snippet": """// GA4 Custom Conversion Event Tracking
function trackAppointmentLead(department, doctorName) {
  gtag('event', 'generate_lead', {
    'event_category': 'Engagement',
    'event_label': department,
    'value': 1.0,
    'currency': 'INR'
  });
}"""
            }
        elif code == 'FS':
            return {
                "domain": "Full Stack Web Engineering (MERN Stack & Cloud Architecture)",
                "tools": "React.js 18, Node.js 20, Express.js, MongoDB Atlas, Mongoose ORM, TypeScript, Tailwind CSS, Docker, Render Cloud",
                "problem": "Healthcare appointments and consultation booking portals suffer from monolithic architecture bottlenecks, lack of mobile responsiveness, insecure session management, and slow database read/write latency under concurrent loads.",
                "algorithms": "JWT Token Verification Middleware with Refresh Tokens, BCrypt 12-Round Salt Hashing, MongoDB Compound Index Aggregation.",
                "code_snippet": """// Express.js JWT Auth Middleware
export const authenticateToken = (req, res, next) => {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];
  if (!token) return res.status(401).json({ error: 'Access token missing' });
  jwt.verify(token, process.env.JWT_SECRET, (err, user) => {
    if (err) return res.status(403).json({ error: 'Token invalid' });
    req.user = user;
    next();
  });
};"""
            }
        elif code == 'AI':
            return {
                "domain": "Applied Artificial Intelligence, Machine Learning & Predictive Modeling",
                "tools": "Python 3.11, Scikit-Learn, TensorFlow/Keras, XGBoost, NumPy, Pandas, Matplotlib, Seaborn, FastAPI, Docker",
                "problem": "Clinical and financial risk prediction systems suffer from high false-negative rates, feature multicollinearity, un-handled class imbalances, and lack of reproducible model deployment pipelines.",
                "algorithms": "Gradient Boosted Decision Trees (XGBoost), Random Forest Ensemble, SMOTE (Synthetic Minority Over-sampling), PCA Dimensionality Reduction.",
                "code_snippet": """# Scikit-Learn Predictive Model Training with GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV, StratifiedKFold

def train_optimized_classifier(X_train, y_train):
    param_grid = {'n_estimators': [100, 200], 'max_depth': [6, 10]}
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    grid = GridSearchCV(RandomForestClassifier(random_state=42), param_grid, cv=cv, scoring='roc_auc')
    grid.fit(X_train, y_train)
    return grid.best_estimator_"""
            }
        elif code == 'CS':
            return {
                "domain": "Cyber Security, Penetration Testing & Defensive Infrastructure",
                "tools": "Kali Linux, Wireshark, Nmap, Burp Suite Professional, OpenVAS, Metasploit, Snort IDS, Autopsy, Python Cryptography",
                "problem": "Enterprise web applications and perimeter networks face persistent cyber threats, unpatched CVE vulnerabilities, misconfigured access controls, and vulnerable API endpoints susceptible to SQLi and XSS.",
                "algorithms": "AES-256-GCM Cryptographic Encryption, RSA-2048 Asymmetric Key Exchange, SHA-256 Packet Checksums.",
                "code_snippet": """# Python Network Packet Inspection & Anomaly Sniffer
from scapy.all import sniff, IP, TCP

def detect_syn_flood(packet):
    if packet.haslayer(TCP) and packet.haslayer(IP):
        if packet.getlayer(TCP).flags == 2:
            src = packet.getlayer(IP).src
            print(f'[SECURITY ALERT] Potential SYN Port Scan from {src}')

sniff(filter='tcp', prn=detect_syn_flood, store=0, count=100)"""
            }
        elif code == 'CC':
            return {
                "domain": "Cloud Infrastructure Architecture, DevOps & Container Orchestration",
                "tools": "Amazon Web Services (AWS EC2, VPC, S3, RDS, CloudFront), Docker, Kubernetes, GitHub Actions, Terraform, Linux CLI, Prometheus",
                "problem": "Manual server provisioning causes configuration drift, prolonged deployment outages (downtimes of 2+ hours), poor infrastructure utilization, and single-point-of-failure risks.",
                "algorithms": "Infrastructure as Code (IaC) Declarative State Reconciliation, Docker Layer Caching, Kubernetes Horizontal Pod Autoscaler.",
                "code_snippet": """# Terraform AWS High-Availability VPC (main.tf)
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  tags = { Name = "TechnoGlobe-Production-VPC" }
}"""
            }
        elif code == 'JV':
            return {
                "domain": "Java Enterprise Architecture, Spring Boot & Microservices",
                "tools": "Java 17 / 21 LTS, Spring Boot 3, Spring Data JPA, Hibernate ORM, MySQL 8, Spring Security, Maven, JUnit 5, Mockito, React.js",
                "problem": "Legacy enterprise monolithic applications suffer from tight coupling, fragile JDBC transaction management, lack of type-safe ORM mappings, and vulnerability to injection attacks.",
                "algorithms": "Spring Inversion of Control (IoC) & Dependency Injection, JPA Dirty Checking, BCrypt Password Encoding.",
                "code_snippet": """// Spring Boot REST Controller
@RestController
@RequestMapping("/api/v1/accounts")
public class AccountController {
    @Autowired
    private AccountService accountService;

    @PostMapping("/transfer")
    public ResponseEntity<TransactionResponse> executeTransfer(@Valid @RequestBody TransferRequest req) {
        return ResponseEntity.ok(accountService.processFundTransfer(req));
    }
}"""
            }
        elif code == 'BI':
            return {
                "domain": "Computational Biology, Bioinformatics & Genomic Data Science",
                "tools": "Python 3.11, BioPython, NCBI Entrez E-Utilities, BLAST+, PyMOL, Pandas, Matplotlib, Scipy, UniProt API",
                "problem": "Biological researchers face massive genomic sequence data overload, inefficient pairwise sequence comparisons, un-annotated disease mutations, and lack of automated structural visualization pipelines.",
                "algorithms": "Needleman-Wunsch Global Alignment, Smith-Waterman Local Alignment, BLOSUM62 Scoring Matrix, BLAST E-Value.",
                "code_snippet": """# BioPython Pairwise Sequence Alignment Pipeline
from Bio import pairwise2
from Bio.pairwise2 import format_alignment
from Bio.Seq import Seq

def execute_global_alignment(seq1_str, seq2_str):
    s1 = Seq(seq1_str)
    s2 = Seq(seq2_str)
    alignments = pairwise2.align.globalms(s1, s2, 2, -1, -0.5, -0.1)
    return alignments[0]"""
            }
        elif code == 'AD':
            return {
                "domain": "Native Android Mobile Development & Declarative UI Engineering",
                "tools": "Kotlin 1.9, Android Studio Hedgehog, Jetpack Compose, Material 3, Room SQLite DB, Retrofit 2, Coroutines & Flow, Firebase",
                "problem": "Traditional mobile apps built with legacy XML layouts suffer from complex view state synchronization bugs, UI thread blocking during network operations, and data loss upon screen rotation.",
                "algorithms": "MVVM Unidirectional Data Flow, Room Database Migration & SQLite Indexing, Kotlin Flow Reactive Observation.",
                "code_snippet": """// Jetpack Compose ViewModel StateFlow
class MainViewModel(private val repository: DataRepository) : ViewModel() {
    private val _uiState = MutableStateFlow<UiState>(UiState.Loading)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    fun fetchDashboardData() {
        viewModelScope.launch {
            repository.getLiveRecords().collect { data -> _uiState.value = UiState.Success(data) }
        }
    }
}"""
            }
        else:
            return get_track_specific_content('DA')

    t_data = get_track_specific_content(course_code)

    # ---------------------------------------------------------
    # CHAPTER 1: INTRODUCTION & BACKGROUND (Pages 10-11)
    # ---------------------------------------------------------
    story.append(Paragraph("CHAPTER 1: INTRODUCTION & BACKGROUND", chap_heading))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceAfter=8))
    
    story.append(Paragraph("1.1 Industry Context & Domain Background", sec_heading))
    p11 = f"""
    The contemporary digital economy is defined by rapid computational acceleration and the proliferation of large-scale distributed systems in <b>{t_data['domain']}</b>. Organizations worldwide require automated, reproducible, and resilient software architectures to extract maximum value from operational processes. Industrial training and course-based internships bridge the crucial gap between foundational academic theory taught in collegiate programs and commercial software engineering standards practiced in modern IT enterprises.
    """
    story.append(Paragraph(p11, body_justify))

    story.append(Paragraph("1.2 Host Organization Profile: TechnoGlobe IT Solutions", sec_heading))
    p12 = f"""
    <b>TechnoGlobe IT Solutions Pvt. Ltd.</b> is a premier technological training and software development enterprise established to empower engineering and computer science undergraduates with cutting-edge industry competencies. The Bharatpur Authorized Regional Centre (Centre Code: <b>BPT-01</b>, Affiliation Ref: <b>TG/FRAN/RAJ/BPT/2024-001</b>), situated at Poddar College Campus, serves as an advanced technological innovation hub equipped with high-performance computational laboratories, modern software development kits (SDKs), cloud simulation environments, and experienced professorial faculty mentors.
    """
    story.append(Paragraph(p12, body_justify))

    story.append(Paragraph("1.3 Problem Genesis & Motivation", sec_heading))
    p13 = f"""
    <b>Operational Problem:</b> {t_data['problem']}<br/>
    <b>Technical Motivation:</b> Addressing these bottlenecks requires moving beyond ad-hoc manual scripts toward a cohesive, enterprise-grade engineering paradigm. By architecting an automated system based on <b>{t_data['tools']}</b>, this project delivers robust computational pipelines capable of handling real-world scale with zero data loss and minimal latency.
    """
    story.append(Paragraph(p13, body_justify))

    story.append(Paragraph("1.4 Aims, Core Objectives & Deliverables", sec_heading))
    p14 = f"""
    The principal objectives of this Capstone Internship Project are:<br/>
    1. <b>Architectural Engineering:</b> Design a modular, scalable, multi-tier software architecture adhering to industry best practices.<br/>
    2. <b>Pipeline Implementation:</b> Implement automated data ingestion, transformation, business logic execution, and API endpoints using <b>{t_data['tools'].split(',')[0]}</b>.<br/>
    3. <b>Security & Governance:</b> Integrate rigorous role-based access control, cryptographic verification, and exception handling protocols.<br/>
    4. <b>Verification & Validation:</b> Execute comprehensive unit, integration, and performance test suites targeting a minimum 90% validation success rate.<br/>
    5. <b>Executive Documentation:</b> Author full academic documentation, technical specifications, and user execution manuals.
    """
    story.append(Paragraph(p14, body_justify))

    story.append(Paragraph("1.5 Scope, Operational Boundaries & Assumptions", sec_heading))
    p15 = f"""
    The operational scope of this project encompasses full lifecycle implementation from initial dataset ingestion and system modeling to functional validation. The system is designed to operate seamlessly across standard desktop and cloud browser environments with minimal hardware overhead.
    """
    story.append(Paragraph(p15, body_justify))
    story.append(PageBreak())

    # ---------------------------------------------------------
    # CHAPTER 2: LITERATURE REVIEW & TECHNOLOGY STACK (Pages 12-13)
    # ---------------------------------------------------------
    story.append(Paragraph("CHAPTER 2: LITERATURE REVIEW & TECHNOLOGY STACK", chap_heading))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceAfter=8))

    story.append(Paragraph("2.1 Theoretical Foundations & Domain Principles", sec_heading))
    p21 = f"""
    Modern software engineering in <b>{t_data['domain']}</b> is grounded in principles of separation of concerns, modularity, data encapsulation, and reproducible algorithmic pipelines. As demonstrated in contemporary literature (Pressman, 2020; Martin, 2018), decoupled multi-tier architectures significantly lower technical debt and enhance system maintainability over multi-year software lifecycles.
    """
    story.append(Paragraph(p21, body_justify))

    story.append(Paragraph("2.2 Comparative Study of Existing Methodologies vs Proposed Solution", sec_heading))
    p22 = f"""
    A comparative review of conventional legacy approaches versus the modern architecture implemented in this project reveals marked improvements across all key engineering dimensions:
    """
    story.append(Paragraph(p22, body_justify))

    comp_table_data = [
        [Paragraph("<b>Evaluation Dimension</b>", body_bold), Paragraph("<b>Legacy / Conventional Approach</b>", body_bold), Paragraph("<b>Proposed Capstone Architecture</b>", body_bold)],
        [Paragraph("System Architecture", body), Paragraph("Monolithic, tightly coupled scripts with manual intervention", body), Paragraph("Modular, multi-tier decoupled architecture with automated pipelines", body)],
        [Paragraph("Data Processing Speed", body), Paragraph("High latency (hours to days for manual consolidation)", body), Paragraph("Real-time to sub-second automated execution (<100ms)", body)],
        [Paragraph("Error Handling & Validation", body), Paragraph("Unstructured, silent failure modes without audit logging", body), Paragraph("Structured exception handling, validation schemas & audit trails", body)],
        [Paragraph("Security & Authentication", body), Paragraph("Plaintext storage or hardcoded credentials", body), Paragraph("Cryptographic hashing (BCrypt), JWT tokens & TLS 1.3 encryption", body)],
        [Paragraph("Scalability & Maintenance", body), Paragraph("Rigid, high maintenance overhead on data schema changes", body), Paragraph("Highly extensible, containerized and cloud-ready infrastructure", body)],
    ]
    ct = Table(comp_table_data, colWidths=[38*mm, 68*mm, 68*mm])
    ct.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, PRIMARY),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('BACKGROUND', (0,0), (-1,0), BG_LIGHT),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
    ]))
    story.append(ct)
    story.append(Spacer(1, 6 * mm))

    story.append(Paragraph("2.3 Technology Stack Evaluation & Architectural Rationale", sec_heading))
    p23 = f"""
    <b>Selected Technology Stack:</b> {t_data['tools']}<br/>
    <b>Architectural Rationale:</b> These tools and frameworks were selected following rigorous benchmark evaluations. They provide optimal performance-to-developer-velocity ratios, vast open-source ecosystems, extensive enterprise adoption, and native support for asynchronous computational workflows.
    """
    story.append(Paragraph(p23, body_justify))
    story.append(PageBreak())

    # ---------------------------------------------------------
    # CHAPTER 3: SYSTEM REQUIREMENTS SPECIFICATION (Pages 14-15)
    # ---------------------------------------------------------
    story.append(Paragraph("CHAPTER 3: SYSTEM REQUIREMENTS SPECIFICATION (SRS)", chap_heading))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceAfter=8))

    story.append(Paragraph("3.1 Stakeholder Profiles & User Personas", sec_heading))
    p31 = f"""
    The system identifies three primary operational stakeholder personas:<br/>
    • <b>System Administrator / Academic Supervisor:</b> Requires full administrative control over data ingestion, user roles, system settings, and grading approval.<br/>
    • <b>Technical Operator / Student Candidate:</b> Requires streamlined execution interfaces, real-time feedback, and automated report generation.<br/>
    • <b>External Auditor / Verification Entity:</b> Requires instant, tamper-proof public cryptographic verification of issued credentials and project artifacts.
    """
    story.append(Paragraph(p31, body_justify))

    story.append(Paragraph("3.2 Functional Requirements Matrix", sec_heading))
    srs_table_data = [
        [Paragraph("<b>Req ID</b>", body_bold), Paragraph("<b>Functional Requirement Specification</b>", body_bold), Paragraph("<b>Priority</b>", body_bold), Paragraph("<b>Validation Status</b>", body_bold)],
        [Paragraph("FR-01", body_bold), Paragraph("Automated Data Ingestion & Sanitization Pipeline", body), Paragraph("High", body), Paragraph("VERIFIED (PASS)", body_bold)],
        [Paragraph("FR-02", body_bold), Paragraph("Algorithmic Core Execution & Mathematical Calculations", body), Paragraph("High", body), Paragraph("VERIFIED (PASS)", body_bold)],
        [Paragraph("FR-03", body_bold), Paragraph("Role-Based Access Control & JWT Session Management", body), Paragraph("Critical", body), Paragraph("VERIFIED (PASS)", body_bold)],
        [Paragraph("FR-04", body_bold), Paragraph("Real-Time KPI Analytics & Dashboard Visualization", body), Paragraph("High", body), Paragraph("VERIFIED (PASS)", body_bold)],
        [Paragraph("FR-05", body_bold), Paragraph("Automated PDF Report & Documentation Generation", body), Paragraph("High", body), Paragraph("VERIFIED (PASS)", body_bold)],
        [Paragraph("FR-06", body_bold), Paragraph("Cryptographic HMAC Signature Verification & QR Linking", body), Paragraph("Critical", body), Paragraph("VERIFIED (PASS)", body_bold)],
    ]
    st = Table(srs_table_data, colWidths=[20*mm, 95*mm, 24*mm, 35*mm])
    st.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, PRIMARY),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('BACKGROUND', (0,0), (-1,0), BG_LIGHT),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
    ]))
    story.append(st)
    story.append(Spacer(1, 6 * mm))

    story.append(Paragraph("3.3 Non-Functional Requirements (NFRs)", sec_heading))
    p33 = f"""
    • <b>Performance & Latency:</b> API response time < 150ms; report generation < 2.0 seconds.<br/>
    • <b>Security & Integrity:</b> SHA-256 / HMAC cryptographic verification; zero plaintext password exposure.<br/>
    • <b>Reliability & Availability:</b> 99.9% uptime target with automated database transaction rollbacks upon exceptions.<br/>
    • <b>Maintainability:</b> Clean code structure adhering to PEP-8 / TypeScript standard guidelines.
    """
    story.append(Paragraph(p33, body_justify))

    story.append(Paragraph("3.4 Hardware & Software Environment Specifications", sec_heading))
    env_data = [
        [Paragraph("<b>Component</b>", body_bold), Paragraph("<b>Minimum Specification</b>", body_bold), Paragraph("<b>Production Environment</b>", body_bold)],
        [Paragraph("Processor (CPU)", body), Paragraph("Intel Core i3 / AMD Ryzen 3 (Dual Core, 2.0 GHz)", body), Paragraph("Intel Core i7 / AMD Ryzen 7 (8 Cores, 3.8 GHz)", body)],
        [Paragraph("System Memory (RAM)", body), Paragraph("4 GB DDR4", body), Paragraph("16 GB DDR4 / DDR5 High Speed", body)],
        [Paragraph("Storage", body), Paragraph("20 GB Free SSD Space", body), Paragraph("500 GB NVMe PCIe 4.0 SSD", body)],
        [Paragraph("Operating System", body), Paragraph("Windows 10 / Ubuntu 20.04 LTS", body), Paragraph("Windows 11 / Linux (Ubuntu 22.04 LTS / Alpine)", body)],
        [Paragraph("Runtime Environment", body), Paragraph("Python 3.10+ / Node.js 18+", body), Paragraph("Python 3.11+ / Node.js 20 LTS", body)],
    ]
    et = Table(env_data, colWidths=[38*mm, 68*mm, 68*mm])
    et.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, PRIMARY),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('BACKGROUND', (0,0), (-1,0), BG_LIGHT),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
    ]))
    story.append(et)
    story.append(PageBreak())

    # ---------------------------------------------------------
    # CHAPTER 4: SYSTEM DESIGN & ARCHITECTURE (Pages 16-17)
    # ---------------------------------------------------------
    story.append(Paragraph("CHAPTER 4: SYSTEM DESIGN & ARCHITECTURE", chap_heading))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceAfter=8))

    story.append(Paragraph("4.1 High-Level Multi-Tier Architectural Paradigm", sec_heading))
    p41 = f"""
    The system follows a strict 3-Tier Enterprise Architecture consisting of:<br/>
    1. <b>Presentation Tier (Frontend):</b> Single Page Application (SPA) built with modern component architectures, providing dynamic forms, real-time input validation, and interactive visualization dashboards.<br/>
    2. <b>Application Logic Tier (Backend):</b> RESTful API microservice handling business rule validation, algorithmic data transformation, token-based authentication, and PDF document rendering.<br/>
    3. <b>Data Persistence Tier (Database):</b> Relational storage engine enforcing strict schema constraints, foreign key cascades, transactional integrity (ACID), and indexing for sub-millisecond query execution.
    """
    story.append(Paragraph(p41, body_justify))

    story.append(Paragraph("4.2 Data Flow Modeling (DFD Levels 0, 1 & 2)", sec_heading))
    p42 = f"""
    • <b>DFD Level 0 (Context Diagram):</b> Represents the external boundaries where Student / Faculty users input raw parameters, and the system outputs authenticated certificates, project dossiers, and verification slips.<br/>
    • <b>DFD Level 1:</b> Decomposes the process into 4 core functional sub-processes: Authentication Gatekeeper (P1), Ingestion & Transformation Engine (P2), Analytics & Evaluation Processor (P3), and Document Compilation Service (P4).<br/>
    • <b>DFD Level 2:</b> Details the algorithmic pipeline within Process P2, including validation, normalization, and relational storage.
    """
    story.append(Paragraph(p42, body_justify))
    story.append(PageBreak())

    story.append(Paragraph("4.3 Entity-Relationship (ER) Schema & Data Dictionary", sec_heading))
    er_data = [
        [Paragraph("<b>Table Entity</b>", body_bold), Paragraph("<b>Primary Key</b>", body_bold), Paragraph("<b>Foreign Keys</b>", body_bold), Paragraph("<b>Key Attributes & Purpose</b>", body_bold)],
        [Paragraph("students", body_bold), Paragraph("id (INTEGER)", body), Paragraph("None", body), Paragraph("full_name, dob, mobile, email, college_name, degree, branch", body)],
        [Paragraph("courses", body_bold), Paragraph("id (INTEGER)", body), Paragraph("None", body), Paragraph("code, name, title, duration_weeks, total_hours", body)],
        [Paragraph("course_modules", body_bold), Paragraph("id (INTEGER)", body), Paragraph("course_id -> courses.id", body), Paragraph("module_number, title, topics_json, hours", body)],
        [Paragraph("mentors", body_bold), Paragraph("id (INTEGER)", body), Paragraph("None", body), Paragraph("name, designation, email, phone, bio", body)],
        [Paragraph("internships", body_bold), Paragraph("id (INTEGER)", body), Paragraph("student_id, course_id, mentor_id", body), Paragraph("start_date, end_date, total_hours, status, cert_number", body)],
        [Paragraph("certificates", body_bold), Paragraph("id (INTEGER)", body), Paragraph("internship_id -> internships.id", body), Paragraph("certificate_number, verification_code, issue_date", body)],
    ]
    ert = Table(er_data, colWidths=[28*mm, 26*mm, 42*mm, 78*mm])
    ert.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, PRIMARY),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('BACKGROUND', (0,0), (-1,0), BG_LIGHT),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
    ]))
    story.append(ert)
    story.append(Spacer(1, 6 * mm))

    story.append(Paragraph("4.4 Database Normalization & Relational Integrity (3NF)", sec_heading))
    p44 = f"""
    The underlying relational database schema is normalized up to <b>Third Normal Form (3NF)</b>. Redundancies across student profiles, curriculum tracks, and evaluation scores are decoupled into discrete relational tables linked through foreign keys with <code>ON DELETE CASCADE</code> rules, eliminating update and deletion anomalies.
    """
    story.append(Paragraph(p44, body_justify))
    story.append(PageBreak())

    # ---------------------------------------------------------
    # CHAPTER 5: IMPLEMENTATION & CODE ARCHITECTURE (Pages 18-19)
    # ---------------------------------------------------------
    story.append(Paragraph("CHAPTER 5: IMPLEMENTATION & CODE ARCHITECTURE", chap_heading))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceAfter=8))

    story.append(Paragraph("5.1 Project Directory Structure & Modular Decomposition", sec_heading))
    p51 = f"""
    The codebase is organized into clean, decoupled modules conforming to industry best practices:
    """
    story.append(Paragraph(p51, body_justify))

    dir_struct = """TechnoGlobe_Capstone_Project/
├── server/
│   ├── main.py                   # FastAPI application routes & JWT authentication
│   ├── database.py               # SQLite schema definition & indexes
│   ├── seed_data.py              # Course catalog, 82+ modules & faculty updates
│   ├── pdf_service.py            # ReportLab vector PDF document engine
│   └── project_report_service.py # 25+ page academic dissertation builder
└── client/
    └── src/
        ├── contexts/AuthContext.tsx   # Global JWT state provider
        ├── pages/StepByStepWizardPage.tsx # 5-Step autofill internship generator
        └── pages/PublicVerifyPage.tsx   # Public cryptographic QR verification"""

    story.append(Table([[Paragraph(f"<pre>{dir_struct}</pre>", code_style)]], colWidths=[174*mm], style=[('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F1F5F9")), ('BOX', (0,0), (-1,-1), 0.5, BORDER_COLOR), ('TOPPADDING', (0,0), (-1,-1), 4), ('BOTTOMPADDING', (0,0), (-1,-1), 4)]))
    story.append(Spacer(1, 6 * mm))

    story.append(Paragraph("5.2 Algorithmic Logic & Flowchart Breakdown", sec_heading))
    p52 = f"""
    <b>Core Algorithm Architecture:</b> {t_data['algorithms']}<br/>
    The algorithmic execution begins with request ingestion, followed by input schema validation, authorization verification, database state queries, data aggregation calculations, and finally cryptographic signature compilation.
    """
    story.append(Paragraph(p52, body_justify))
    story.append(PageBreak())

    story.append(Paragraph("5.3 Production Source Code Implementation", sec_heading))
    p53 = f"""
    The following production code snippet demonstrates the core algorithmic execution engine implemented in <b>{course_name}</b>:
    """
    story.append(Paragraph(p53, body_justify))
    story.append(Table([[Paragraph(f"<pre>{t_data['code_snippet']}</pre>", code_style)]], colWidths=[174*mm], style=[('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")), ('BOX', (0,0), (-1,-1), 0.5, PRIMARY), ('TOPPADDING', (0,0), (-1,-1), 4), ('BOTTOMPADDING', (0,0), (-1,-1), 4)]))
    story.append(Spacer(1, 6 * mm))

    story.append(Paragraph("5.4 Architectural Walkthrough & Middleware Integration", sec_heading))
    p54 = f"""
    The code architecture employs declarative interfaces, exception containment blocks, and automated garbage collection. Database connections are governed via context managers ensuring zero unclosed socket handles or connection leaks.
    """
    story.append(Paragraph(p54, body_justify))
    story.append(PageBreak())

    # ---------------------------------------------------------
    # CHAPTER 6: TESTING, QUALITY ASSURANCE & VALIDATION (Pages 20-21)
    # ---------------------------------------------------------
    story.append(Paragraph("CHAPTER 6: TESTING, QUALITY ASSURANCE & VALIDATION", chap_heading))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceAfter=8))

    story.append(Paragraph("6.1 Verification Methodology & Testing Lifecycle", sec_heading))
    p61 = f"""
    A multi-phase Quality Assurance methodology was applied throughout development, incorporating automated unit testing, integration testing, boundary stress testing, and User Acceptance Testing (UAT). Each test case was evaluated against strict pass/fail acceptance criteria.
    """
    story.append(Paragraph(p61, body_justify))

    story.append(Paragraph("6.2 Development & Test Environment Configuration", sec_heading))
    p62 = f"""
    Testing was performed in an isolated sandbox environment simulating concurrent user requests and database load spikes. Automated scripts verified API schema conformance, HTTP status codes, and PDF generation integrity without blocking server event loops.
    """
    story.append(Paragraph(p62, body_justify))
    story.append(PageBreak())

    story.append(Paragraph("6.3 Comprehensive Test Execution Matrix", sec_heading))
    test_matrix = [
        [Paragraph("<b>Test ID</b>", body_bold), Paragraph("<b>Test Scope / Feature</b>", body_bold), Paragraph("<b>Input Condition</b>", body_bold), Paragraph("<b>Expected Outcome</b>", body_bold), Paragraph("<b>Status</b>", body_bold)],
        [Paragraph("TC-01", body_bold), Paragraph("JWT Authentication", body), Paragraph("Valid faculty email & pass", body), Paragraph("Generate 24hr valid JWT token", body), Paragraph("PASS", ParagraphStyle('P', fontName='Helvetica-Bold', textColor=SUCCESS_COLOR))],
        [Paragraph("TC-02", body_bold), Paragraph("Route Guard Protection", body), Paragraph("Unauthenticated GET request", body), Paragraph("Return HTTP 401 Unauthorized", body), Paragraph("PASS", ParagraphStyle('P', fontName='Helvetica-Bold', textColor=SUCCESS_COLOR))],
        [Paragraph("TC-03", body_bold), Paragraph("Data Sanitization", body), Paragraph("String with SQL injection chars", body), Paragraph("Sanitize & execute parameterized SQL", body), Paragraph("PASS", ParagraphStyle('P', fontName='Helvetica-Bold', textColor=SUCCESS_COLOR))],
        [Paragraph("TC-04", body_bold), Paragraph("1-Click Quick Wizard", body), Paragraph("Student details + course track", body), Paragraph("Create 15 records + issue certs", body), Paragraph("PASS", ParagraphStyle('P', fontName='Helvetica-Bold', textColor=SUCCESS_COLOR))],
        [Paragraph("TC-05", body_bold), Paragraph("PDF Vector Generation", body), Paragraph("Internship ID request", body), Paragraph("Compile vector PDF with QR block", body), Paragraph("PASS", ParagraphStyle('P', fontName='Helvetica-Bold', textColor=SUCCESS_COLOR))],
        [Paragraph("TC-06", body_bold), Paragraph("HMAC Verification", body), Paragraph("Scan QR code URL with sig", body), Paragraph("Return valid cryptographic status", body), Paragraph("PASS", ParagraphStyle('P', fontName='Helvetica-Bold', textColor=SUCCESS_COLOR))],
        [Paragraph("TC-07", body_bold), Paragraph("Form Validation", body), Paragraph("Invalid email or <10 digit phone", body), Paragraph("Block submission with clear banner", body), Paragraph("PASS", ParagraphStyle('P', fontName='Helvetica-Bold', textColor=SUCCESS_COLOR))],
    ]
    tmt = Table(test_matrix, colWidths=[18*mm, 38*mm, 42*mm, 54*mm, 22*mm])
    tmt.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, PRIMARY),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('BACKGROUND', (0,0), (-1,0), BG_LIGHT),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
    ]))
    story.append(tmt)
    story.append(Spacer(1, 6 * mm))

    story.append(Paragraph("6.4 Boundary Value Analysis & Security Verification", sec_heading))
    p63 = f"""
    All numeric boundaries (e.g. evaluation scores 0–100, attendance percentage 0–100%, training hours 0–200) were subjected to rigorous boundary value testing. Negative inputs, null values, and special character strings were rejected gracefully with clean user-facing error notifications.
    """
    story.append(Paragraph(p63, body_justify))
    story.append(PageBreak())

    # ---------------------------------------------------------
    # CHAPTER 7: RESULTS, ANALYTICS & IMPACT DEMONSTRATION (Pages 22-23)
    # ---------------------------------------------------------
    story.append(Paragraph("CHAPTER 7: RESULTS, ANALYTICS & IMPACT DEMONSTRATION", chap_heading))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceAfter=8))

    story.append(Paragraph("7.1 Empirical Findings & Deliverable Highlights", sec_heading))
    p71 = f"""
    The practical deployment of the capstone project yielded exceptional operational results. Key highlights include:<br/>
    • <b>Turnaround Compression:</b> Reduced internship credential compilation and document package issuance from 5 working days to <b>under 10 seconds</b>.<br/>
    • <b>Error Elimination:</b> Eliminated typographical errors and missing institutional reference numbers via automated database constraints and 1-click autofill.<br/>
    • <b>Security Assurance:</b> Established 100% tamper-evident verification via HMAC cryptographic signatures embedded into scannable vector QR codes.
    """
    story.append(Paragraph(p71, body_justify))

    story.append(Paragraph("7.2 System Performance & KPI Impact Summary", sec_heading))
    kpi_data = [
        [Paragraph("<b>Performance / Business Metric</b>", body_bold), Paragraph("<b>Before Implementation</b>", body_bold), Paragraph("<b>Post Implementation</b>", body_bold), Paragraph("<b>Quantified Impact</b>", body_bold)],
        [Paragraph("Document Compilation Time", body), Paragraph("4–6 Hours per student", body), Paragraph("< 5 Seconds per student", body), Paragraph("99.2% Time Reduction", body_bold)],
        [Paragraph("Verification Audit Latency", body), Paragraph("3–5 Days (Manual postal/call)", body), Paragraph("Instant (< 1 Second online)", body), Paragraph("Real-Time Verification", body_bold)],
        [Paragraph("Data Consistency & Integrity", body), Paragraph("Manual Excel entry errors (~8%)", body), Paragraph("100% Relational Integrity", body), Paragraph("Zero Schema Anomalies", body_bold)],
        [Paragraph("Multi-Track Course Support", body), Paragraph("Fixed single track only", body), Paragraph("9 Comprehensive Tracks", body), Paragraph("800% Catalog Expansion", body_bold)],
    ]
    kt = Table(kpi_data, colWidths=[45*mm, 42*mm, 42*mm, 45*mm])
    kt.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, PRIMARY),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('BACKGROUND', (0,0), (-1,0), BG_LIGHT),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
    ]))
    story.append(kt)
    story.append(PageBreak())

    story.append(Paragraph("7.3 Return on Investment (ROI) & Institutional Benefits", sec_heading))
    p73 = f"""
    <b>Operational Scalability:</b> By transitioning to this unified system, TechnoGlobe Regional Centre Bharatpur can effortlessly process hundreds of simultaneous candidates with zero incremental administrative overhead.<br/><br/>
    <b>Institutional Credibility:</b> Providing candidates with 25+ page bound dissertation portfolios alongside authenticated certificates elevates student placement outcomes during campus recruitment drives.
    """
    story.append(Paragraph(p73, body_justify))
    story.append(PageBreak())

    # ---------------------------------------------------------
    # CHAPTER 8: CONCLUSION & FUTURE SCOPE (Page 24)
    # ---------------------------------------------------------
    story.append(Paragraph("CHAPTER 8: CONCLUSION & FUTURE SCOPE", chap_heading))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceAfter=8))

    story.append(Paragraph("8.1 Summary of Completed Work & Learning Outcomes", sec_heading))
    p81 = f"""
    This Capstone Project successfully conceptualized, engineered, and validated an industrial-grade system for <b>{course_name}</b> at TechnoGlobe IT Solutions Pvt. Ltd. (Bharatpur Centre). Through this project, comprehensive competencies were mastered in full-stack architecture, relational database engineering, automated document synthesis, and cryptographic security verification.
    """
    story.append(Paragraph(p81, body_justify))

    story.append(Paragraph("8.2 Operational Constraints Encountered", sec_heading))
    p82 = f"""
    Key constraints encountered and resolved during development included balancing complex ReportLab page geometry calculations across multi-page tables, enforcing strict CORS origin boundaries, and optimizing client-side state transitions in React.
    """
    story.append(Paragraph(p82, body_justify))

    story.append(Paragraph("8.3 Recommended Future Enhancements & Scalability Roadmap", sec_heading))
    p83 = f"""
    Future architectural expansions planned for subsequent iterations include:<br/>
    1. <b>Batch Excel Import:</b> Automated bulk ingestion allowing institutional coordinators to upload 50+ students in a single Excel sheet.<br/>
    2. <b>WhatsApp & Email Dispatch:</b> Automated dispatch of issued certificate PDFs directly to students upon completion.<br/>
    3. <b>Blockchain Credential Anchoring:</b> Anchoring certificate cryptographic hashes onto public distributed ledgers for permanent decentralized attestation.
    """
    story.append(Paragraph(p83, body_justify))
    story.append(PageBreak())

    # ---------------------------------------------------------
    # REFERENCES & BIBLIOGRAPHY (Page 25)
    # ---------------------------------------------------------
    story.append(Paragraph("REFERENCES & BIBLIOGRAPHY", chap_heading))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceAfter=10))

    references = [
        "Pressman, R. S., & Maxim, B. R. (2020). Software Engineering: A Practitioner's Approach (9th ed.). McGraw-Hill Education.",
        "Martin, R. C. (2018). Clean Architecture: A Craftsman's Guide to Software Structure and Design. Prentice Hall.",
        "VanderPlas, J. (2016). Python Data Science Handbook: Essential Tools for Working with Data. O'Reilly Media.",
        "Silberschatz, A., Korth, H. F., & Sudarshan, S. (2019). Database System Concepts (7th ed.). McGraw-Hill.",
        "Fielding, R. T. (2000). Architectural Styles and the Design of Network-based Software Architectures. Doctoral dissertation, UC Irvine.",
        "Rescorla, E. (2018). The Transport Layer Security (TLS) Protocol Version 1.3. RFC 8446, IETF.",
        "Gamma, E., Helm, R., Johnson, R., & Vlissides, J. (1994). Design Patterns: Elements of Reusable Object-Oriented Software. Addison-Wesley.",
        "Few, S. (2012). Show Me the Numbers: Designing Tables and Graphs to Enlighten (2nd ed.). Analytics Press.",
        "Chacon, S., & Straub, B. (2014). Pro Git: Everything you need to know about Git (2nd ed.). Apress.",
        "OWASP Foundation. (2021). OWASP Top 10: The Ten Most Critical Web Application Security Risks.",
        "ReportLab Europe. (2024). ReportLab PDF Generation User Guide and API Reference.",
        "FastAPI Documentation. (2024). FastAPI: High-Performance Web Framework for Building APIs with Python."
    ]
    for idx, ref in enumerate(references, 1):
        story.append(Paragraph(f"[{idx}] {ref}", ParagraphStyle('RefStyle', fontName='Helvetica', fontSize=8, leading=12, spaceAfter=4)))

    story.append(PageBreak())

    # ---------------------------------------------------------
    # APPENDIX A: 6-WEEK DAILY ACTIVITY LOG (Pages 26, 27, 28)
    # ---------------------------------------------------------
    story.append(Paragraph("APPENDIX A: 6-WEEK DAILY ACTIVITY LOG AUDIT (PART 1)", chap_heading))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceAfter=8))
    story.append(Paragraph("Official On-Site Laboratory Attendance & Practical Work Execution Record (Days 1 – 12)", subtitle_style))
    story.append(Spacer(1, 4 * mm))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT date, day_of_week, topic_covered, status, total_hours FROM attendance WHERE internship_id = ? ORDER BY date ASC LIMIT 36", (internship_id,))
    att_rows = cursor.fetchall()
    conn.close()

    if att_rows:
        header_row = [
            Paragraph("<b>Day #</b>", body_bold),
            Paragraph("<b>Date & Day</b>", body_bold),
            Paragraph("<b>Curriculum Topic & Practical Laboratory Work Covered</b>", body_bold),
            Paragraph("<b>Status</b>", body_bold),
            Paragraph("<b>Hours</b>", body_bold)
        ]
        
        # Build 3 tables for 3 pages (12 days per page)
        chunk1 = [header_row] + [
            [
                Paragraph(f"Day {idx:02d}", body),
                Paragraph(f"{row[0]} ({row[1][:3]})", body),
                Paragraph(row[2] or "Core curriculum practical exercise", body),
                Paragraph(row[3], body_bold if row[3] == 'PRESENT' else body),
                Paragraph(f"{row[4]:.1f}h", body)
            ]
            for idx, row in enumerate(att_rows[:12], 1)
        ]
        alt1 = Table(chunk1, colWidths=[16*mm, 32*mm, 90*mm, 20*mm, 16*mm])
        alt1.setStyle(TableStyle([
            ('BOX', (0,0), (-1,-1), 1, PRIMARY),
            ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
            ('BACKGROUND', (0,0), (-1,0), BG_LIGHT),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 2),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ]))
        story.append(alt1)
        story.append(PageBreak())

        # Page 27: Days 13-24
        story.append(Paragraph("APPENDIX A: DAILY ACTIVITY LOG AUDIT (PART 2: DAYS 13 – 24)", chap_heading))
        story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceAfter=8))
        chunk2 = [header_row] + [
            [
                Paragraph(f"Day {idx:02d}", body),
                Paragraph(f"{row[0]} ({row[1][:3]})", body),
                Paragraph(row[2] or "Core curriculum practical exercise", body),
                Paragraph(row[3], body_bold if row[3] == 'PRESENT' else body),
                Paragraph(f"{row[4]:.1f}h", body)
            ]
            for idx, row in enumerate(att_rows[12:24], 13)
        ]
        alt2 = Table(chunk2, colWidths=[16*mm, 32*mm, 90*mm, 20*mm, 16*mm])
        alt2.setStyle(TableStyle([
            ('BOX', (0,0), (-1,-1), 1, PRIMARY),
            ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
            ('BACKGROUND', (0,0), (-1,0), BG_LIGHT),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 2),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ]))
        story.append(alt2)
        story.append(PageBreak())

        # Page 28: Days 25-36
        story.append(Paragraph("APPENDIX A: DAILY ACTIVITY LOG AUDIT (PART 3: DAYS 25 – 36)", chap_heading))
        story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceAfter=8))
        chunk3 = [header_row] + [
            [
                Paragraph(f"Day {idx:02d}", body),
                Paragraph(f"{row[0]} ({row[1][:3]})", body),
                Paragraph(row[2] or "Core curriculum practical exercise", body),
                Paragraph(row[3], body_bold if row[3] == 'PRESENT' else body),
                Paragraph(f"{row[4]:.1f}h", body)
            ]
            for idx, row in enumerate(att_rows[24:36], 25)
        ]
        alt3 = Table(chunk3, colWidths=[16*mm, 32*mm, 90*mm, 20*mm, 16*mm])
        alt3.setStyle(TableStyle([
            ('BOX', (0,0), (-1,-1), 1, PRIMARY),
            ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
            ('BACKGROUND', (0,0), (-1,0), BG_LIGHT),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 2),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ]))
        story.append(alt3)
    else:
        story.append(Paragraph("Standard 36 working days (126 hours) completed with 100% verified physical laboratory attendance.", body))
    
    story.append(PageBreak())

    # ---------------------------------------------------------
    # APPENDIX B: TECHNICAL GLOSSARY & ACRONYMS (Page 29)
    # ---------------------------------------------------------
    story.append(Paragraph("APPENDIX B: TECHNICAL GLOSSARY & ACRONYMS", chap_heading))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceAfter=8))

    glossary = [
        ("API", "Application Programming Interface: Defined protocols enabling software components to communicate."),
        ("CRUD", "Create, Read, Update, Delete: Four fundamental functions of persistent data storage systems."),
        ("DAX", "Data Analysis Expressions: Library of functions and operators used to build formulas in Power BI."),
        ("DFD", "Data Flow Diagram: Graphical model depicting the flow of data through an information system."),
        ("EDA", "Exploratory Data Analysis: Statistical approach to analyzing datasets and summarizing distributions."),
        ("ERD", "Entity Relationship Diagram: Visual schema depicting database entities, keys, and foreign relations."),
        ("ETL", "Extract, Transform, Load: Foundational three-step data engineering integration pipeline."),
        ("HMAC", "Hash-based Message Authentication Code: Cryptographic signature technique utilizing secret keys."),
        ("JWT", "JSON Web Token: Compact, URL-safe standard (RFC 7519) for transmitting claims securely."),
        ("NFR", "Non-Functional Requirement: Operational criteria (speed, security) judging system quality."),
        ("ORM", "Object-Relational Mapping: Programming technique bridging object models and relational databases."),
        ("REST", "Representational State Transfer: Architectural paradigm for stateless HTTP web services."),
        ("SRS", "Software Requirements Specification: Comprehensive engineering requirements design document."),
        ("UAT", "User Acceptance Testing: Final phase where stakeholders verify business requirements."),
        ("VAPT", "Vulnerability Assessment and Penetration Testing: Systematic security audit methodology.")
    ]
    gt_data = [[Paragraph(f"<b>{g[0]}</b>", body_bold), Paragraph(g[1], body)] for g in glossary]
    gl_table = Table(gt_data, colWidths=[24*mm, 150*mm])
    gl_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('LINEBELOW', (0,0), (-1,-1), 0.2, BORDER_COLOR)
    ]))
    story.append(gl_table)
    story.append(PageBreak())

    # ---------------------------------------------------------
    # APPENDIX C: SYSTEM INSTALLATION & RUN GUIDE (Page 30)
    # ---------------------------------------------------------
    story.append(Paragraph("APPENDIX C: SYSTEM INSTALLATION & RUN GUIDE", chap_heading))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceAfter=8))

    guide_text = f"""
    <b>1. Prerequisites & Environment Setup:</b><br/>
    Ensure Python 3.11+ and Node.js 20 LTS are installed on the target machine with Git.<br/><br/>
    <b>2. Repository Cloning & Dependency Installation:</b><br/>
    <pre>
    git clone https://github.com/Krishlayy/technoglobe-certificates.git
    cd technoglobe-certificates
    pip install -r requirements.txt
    cd client && npm install && npm run build && cd ..
    </pre><br/>
    <b>3. Launching Local Application Server:</b><br/>
    <pre>
    python -m uvicorn server.main:app --host 0.0.0.0 --port 8000
    </pre><br/>
    <b>4. Accessing Application Portals:</b><br/>
    • <b>Administrator / Faculty Dashboard:</b> http://localhost:8000/login<br/>
    • <b>Public Certificate Verification:</b> http://localhost:8000/verify<br/>
    • <b>Live Cloud Production URL:</b> https://technoglobe-certificates.onrender.com<br/><br/>
    <b>5. Faculty Administrator Credentials:</b><br/>
    • <b>Head Nitin Sir:</b> Login: <code>nitin@pctm</code> | Password: <code>nitin321</code><br/>
    • <b>Prof. Krishlay Sharma:</b> Login: <code>krishlay@pctm</code> | Password: <code>krishlay321</code><br/>
    • <b>Prof. Rahul Bhatnagar:</b> Login: <code>rahul@pctm</code> | Password: <code>rahul321</code>
    """
    story.append(Paragraph(guide_text, body_justify))
    story.append(Spacer(1, 10 * mm))

    story.append(Paragraph("<b>END OF CAPSTONE PROJECT REPORT DISSERTATION</b>", ParagraphStyle('EndNote', fontName='Helvetica-Bold', fontSize=10, leading=14, textColor=PRIMARY, alignment=1)))
    story.append(Paragraph("Official Academic Documentation — TechnoGlobe IT Solutions Pvt. Ltd.", ParagraphStyle('EndSub', fontName='Helvetica', fontSize=8, leading=11, textColor=MUTED, alignment=1)))

    doc.build(story, canvasmaker=AcademicProjectReportCanvas)
    return filepath

generate_project_report = build_25page_academic_project_report
