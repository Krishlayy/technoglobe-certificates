# TECHNOGLOBE COURSE-BASED INTERNSHIP DOCUMENTATION & CERTIFICATE MANAGEMENT SYSTEM
**Authorized Franchise Centre — Bharatpur, Rajasthan**  
*Poddar College, Near SP Office, Bharatpur, Rajasthan, India*

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/Krishlayy/technoglobe-certificates)

---

## Overview

The **TechnoGlobe Course-Based Internship Documentation & Certificate Management System** is a production-grade educational and institutional administration platform. It enables authorized centre administrators to enter a student's information **ONE TIME** and automatically generate, preview, print, and package a complete 15-document internship portfolio plus an academic-grade consolidated report and `.zip` archive for college/university submission.

---

## Key Features

1. **Organization & Centre Identity**:
   - Organization: `TECHNOGLOBE IT SOLUTIONS PVT. LTD.`
   - Centre: `TECHNOGLOBE – BHARATPUR CENTRE` (Poddar College, Bharatpur)
   - Configurable signatory, contact details, authorization reference, logo, and numbering prefixes (`TG-BPT`, `TG/BPT`).
   - Authentic signature and stamp philosophy: designated blank zones for real physical signatures and institutional seals, with optional admin toggles for digital assets. No fake handwritten signatures or fabricated affiliations.

2. **Supported Industry Tracks**:
   - **Course 1: Data Analytics** (9 Modules: Excel, SQL, Python, Pandas, Data Viz, Power BI, DAX, Statistics, Intro to ML, Capstone Project).
   - **Course 2: Digital Marketing** (10 Modules: SEO, Social Media Marketing, Copywriting, Google Ads, Email Marketing, GA4 Analytics, Performance Marketing, AI Tools, Live Campaign Project).
   - Fully editable curriculums from the administrator dashboard.

3. **University/College Compliance Module & Gatekeeper**:
   - Institutional tracking of College/University name, affiliation reference, faculty coordinator, and approval status (`APPROVED`, `PENDING`, `NOT_REQUIRED`, `REJECTED`).
   - Automated 7-gate compliance checklist before allowing certificate finalization:
     1. Verified Attendance Requirement ($\ge 75\%$)
     2. Total Training Hours Completed ($\ge 120$ hrs)
     3. Daily & Weekly Activity Logs verified
     4. Capstone Project submitted & approved
     5. Mentor Rubric Evaluation completed ($\ge 50/100$)
     6. University/College Compliance validated
     7. Centre Authorized Signatory configured
   - Displays official status: **DOCUMENTATION COMPLETE — READY FOR AUTHORIZED SIGNATURE & STAMP**.

4. **The 15 Generated Official Documents**:
   - `01_Offer_Letter.pdf` — Formal Internship Enrollment & Learning Objectives
   - `02_Joining_Letter.pdf` — Official Commencement Report to College Principal / TPO
   - `03_Course_Syllabus.pdf` — Comprehensive Curriculum & Module Outline
   - `04_Training_Schedule.pdf` — Week-by-Week Timeline & Practical Deliverables
   - `05_Attendance_Sheet.pdf` — Daily Register with Time In/Out & Signatures
   - `06_Attendance_Summary.pdf` — Verified Attendance Audit & Calculated Percentage
   - `07_Daily_Logbook.pdf` — Daily Practical Activity Logbook / Diary
   - `08_Weekly_Progress_Report.pdf` — Weekly Review & Competency Acquisition
   - `09_Project_Assignment.pdf` — Capstone Project Charter & Scope Brief
   - `10_Project_Report.pdf` — Complete Technical Project Documentation
   - `11_Mentor_Evaluation.pdf` — 9-Criteria Rubric Assessment & Score out of 100
   - `12_Performance_Report.pdf` — Consolidated Academic Performance Report
   - `13_Student_Feedback.pdf` — Student Appraisal of Course & Mentorship
   - `14_Internship_Completion_Certificate.pdf` — A4 Landscape Certificate with Security Guilloche Borders, QR Code, and Unique Certificate Number
   - `15_Experience_Training_Certificate.pdf` — A4 Portrait Industrial Experience Credential
   - **Complete Academic Report** (`Complete_Academic_Internship_Report.pdf`) — 25+ page bound university report with Cover Page, Declaration, Certificate, Acknowledgement, TOC, Chapters 1–7, and Appendix.
   - **One-Click Package** (`TECHNOGLOBE_INTERNSHIP_COMPLETE_PACKAGE.zip`) — All 15 documents neatly packaged.

5. **Strictly Internal Offline QR Verification**:
   - The completion certificate features a native vector QR code encoding a **100% self-contained JSON metadata payload**.
   - Zero public URLs; offline verifiable with any standard camera or QR scanner.
   - Distinctive caption beneath QR: `SCAN TO VIEW CERTIFICATE DETAILS`.

6. **50/50 Live Document Editor (`/document-editor`)**:
   - Split-screen workspace: Left 50% form controls & live fields, Right 50% real-time A4 document preview.
   - Real-time updates for particulars, dates, hours, and remarks with instant PDF download and print.

7. **Interactive Attendance Register & Simulation Planner (`/attendance`)**:
   - 36-day attendance sheet with real-time stats and calculations.
   - Dedicated Attendance Planner simulation modal (85%–100% targets) with working days (36), required present days, and maximum non-present days.
   - Labeled: `PLANNING / SIMULATION ONLY — NOT AN OFFICIAL ATTENDANCE RECORD`.
   - Quick bulk actions: `MARK ALL PRESENT`, `MARK SELECTED ABSENT`, `MARK SELECTED LEAVE`, `CLEAR`.

8. **System Backup & Restore (`/backup-restore`)**:
   - SQLite `.db` database download and upload restore with `PRAGMA integrity_check`.
   - Full 17-table JSON export.
   - Demo data controls: `Reset Demo Data` (restores 1 DA and 1 DM student) and `Delete Demo Data`.

---

## Quick Start & Running

### Starting the Application

Double-click `run_server.bat` or execute in PowerShell:
```powershell
python -m uvicorn server.main:app --host 127.0.0.1 --port 8000
```
Open your browser at:
**http://127.0.0.1:8000**

*(The application is completely self-contained; FastAPI serves the compiled React single-page application at port 8000 with deep SPA route fallback)*.

### Optional: Running Frontend in Development Mode (Vite)
If you wish to edit React files with Hot Module Reloading:
```powershell
cd client
npm run dev
```
Open your browser at:
**http://127.0.0.1:3000** (automatically proxies API requests to port 8000).

---

## Testing & Verification

Run the automated end-to-end workflow verification script:
```powershell
cd server
python test_workflow.py
```
This automatically verifies:
- Registering a Data Analytics student
- Recording 36 daily attendance records (100% attendance, 126 hours)
- Recording 36 daily logs and 6 weekly reports
- Submitting and approving the capstone project
- Completing the 9-parameter mentor evaluation rubric
- Passing the compliance gatekeeper
- Finalizing and locking the certificate with automatic sequence numbering (`TG-BPT-DA-2026-xxxx`)
- Verifying the self-contained offline QR JSON payload
- Generating the complete 15-document `.zip` package
- Repeating the exact workflow for a Digital Marketing candidate
- Testing backup database download, JSON export, and demo data reset

---

## Default Credentials (Demo & Faculty Access)

- **Faculty Admin**: `nitin@pctm` / `nitin321` (SUPER_ADMIN full access)
- **Centre Admin**: `admin@technoglobe.co.in` / `admin123`
- **Super Admin**: `superadmin@technoglobe.co.in` / `super123`
- **Industry Mentor**: `vikas@technoglobe.co.in` / `mentor123`
