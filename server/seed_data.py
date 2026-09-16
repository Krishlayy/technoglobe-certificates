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
    import re
    cleaned = re.sub(r'Course-Based IInternshipnternship', 'Course-Based Internship', text)
    cleaned = re.sub(r'Internship\s+Internship', 'Internship', cleaned)
    cleaned = re.sub(r'B\.TechBCA', 'BCA', cleaned)
    cleaned = re.sub(r'120120 Hours', '120 Hours', cleaned)
    cleaned = re.sub(r'None training hours', '120 Training Hours', cleaned)
    return ' '.join(cleaned.split())

# 3 Core Institutions: Poddar College, Poswal Developers & Technoglobe Jaipur
INSTITUTIONS_CATALOG = [
    (1, 'PODDAR', 'Poddar College', 'PODDAR COLLEGE OF TECHNOLOGY & MANAGEMENT', 'Excellence in Technology & Management',
     'Near SP Office, Bharatpur (Raj.)', 'Affiliated with University & Technical Board',
     'https://poddarcollege.org', 'nitin_pitm@yahoo.com', '9414293370',
     'poddar_logo.png', '#0A2540', '#1E3A8A', '#EAA824',
     'Nitin Agarwal', 'Director',
     'EMPTY_INK_PAD_BOX', 'PODDAR_LOGO_TRANSLUCENT', 'PCTM/BPT', 'PCTM', 1),
    (2, 'POSWAL', 'Poswal Developers', 'Poswal Developers', 'Solar Power & Industrial Development',
     '214, Bapu Nagar, Madan Vihar Colony, Kali Baghichi, Ghana Road, Bharatpur (Raj.) 321001',
     'GST: 08ABIFP2454N1ZQ | MSME: UDYAM-RJ-06-0052498',
     'https://poswaldevelopers.com', 'madhuvangurjar19@gmail.com', '9414694727',
     'poswal_logo.png', '#6B2222', '#1D4ED8', '#B45309',
     'Madhuvan Singh Gurjar', 'Authority',
     'EMPTY_INK_PAD_BOX', 'POSWAL_LOGO_TRANSLUCENT', 'POSWAL/BPT', 'POSWAL', 1),
    (3, 'TECHNOGLOBE', 'Technoglobe', 'TECHNOGLOBE - ADVANCED IT TRAINING & DEVELOPMENT', 'Transforming Careers Through Technology',
     'Technoglobe Corporate Center, Plot No. 4, Gopalpura Bypass, Jaipur (Raj.)',
     'Premier IT & Advanced Computing Institute • Jaipur',
     'https://technoglobe.co.in', 'info@technoglobe.co.in', '9829012345',
     'technoglobe_logo.png', '#831843', '#1E40AF', '#F59E0B',
     'Nitin Agarwal', 'Director',
     'EMPTY_INK_PAD_BOX', 'TECHNOGLOBE_LOGO_TRANSLUCENT', 'TG/JPR', 'TG', 1)
]

# Comprehensive Courses Definition (Solar Energy + IT/Computing)
COURSES_CATALOG = [
    ('SOL-01', 'Solar PV Installation & Building Integration (BIPV)', 'Course-Based Training in Rooftop Solar PV Installation & Building Integration',
     'Comprehensive industrial training covering rooftop solar PV installation, architectural building integration (BIPV), mounting structures, electrical distribution, and earth-pit safety.',
     6, 120, 'Offline'),
    ('SOL-02', 'Solar Structure Fitting & Panel Mounting', 'Course-Based Training in Solar Structure Fitting, Panel Mounting & Civil Layout',
     'Practical hands-on training on solar structure fitting, civil foundation layout, tilt angle alignment, wind load anchoring, and torque testing.',
     6, 120, 'Offline'),
    ('SOL-03', 'Solar Electrical Systems & Inverter Tech', 'Course-Based Training in Solar Electrical Systems, Inverters & Grid-Tied Technology',
     'Hands-on electrical training on string/micro-inverters, ACDB/DCDB protection boxes, MC4 crimping, and bi-directional net-metering synchronization.',
     6, 120, 'Offline'),
    ('SOL-04', 'Industrial Solar Power Plant O&M', 'Course-Based Training in Industrial Solar Power Plant Operations & Maintenance',
     'Utility-scale solar plant operations, SCADA monitoring, thermographic hotspot diagnostics, IV curve analysis, string testing, and preventive cleaning protocols.',
     6, 120, 'Offline'),
    ('SOL-05', 'Solar Water Heating & Pumping Systems', 'Course-Based Training in Solar Water Heating & Agricultural Pumping Systems',
     'Engineering of solar thermal collectors, evacuated tube collectors (ETC), flat plate collectors (FPC), and VFD solar agricultural pumping systems.',
     6, 120, 'Offline'),
    ('SOL-06', 'Off-Grid Solar Energy & Battery Storage', 'Course-Based Training in Off-Grid Solar Energy Storage & Battery Management Systems (BMS)',
     'Off-grid energy storage sizing, lithium LiFePO4 & tubular lead-acid batteries, MPPT/PWM hybrid charge controllers, and battery management systems.',
     6, 120, 'Offline'),
    ('SOL-07', 'Solar PV System Design & PVsyst Simulation', 'Course-Based Training in Solar PV System Design, Load Estimation & PVsyst Simulation',
     'System sizing calculations, AutoCAD electrical layout, PVsyst 3D shading analysis, irradiance modeling (GHI/DNI), and Levelized Cost of Energy (LCOE) calculations.',
     6, 120, 'Offline'),
    ('SOL-08', 'Solar Safety Standards & Net-Metering', 'Course-Based Training in Solar Safety Standards, Electrical Earthing & Net-Metering Compliance',
     'CEA electrical regulations, lightning arrestors, surge protection devices (SPD), ground resistance testing (< 2 ohms), PPE safety gear, and DISCOM interconnection procedures.',
     6, 120, 'Offline'),
    ('DA', 'Data Analytics & BI', 'Course-Based Internship in Data Analytics & Business Intelligence',
     'Industry-aligned comprehensive internship covering Excel, SQL, Python, Power BI, Statistics and Capstone Analytics.',
     6, 120, 'Offline'),
    ('DM', 'Digital Marketing & Growth Strategies', 'Course-Based Internship in Digital Marketing & Growth Strategies',
     'Practical marketing program covering SEO, SMM, Google Ads, Content Marketing, Analytics, Performance Marketing and AI tools.',
     6, 120, 'Offline'),
    ('FS', 'Full Stack Web Development (MERN)', 'Course-Based Internship in Full Stack Web Development (MERN Stack)',
     'Full stack engineering covering HTML5, CSS3, JavaScript ES6+, React.js, Node.js, Express.js, MongoDB, REST APIs and Cloud Deployment.',
     6, 120, 'Offline'),
    ('AI', 'Python & Machine Learning / AI', 'Course-Based Internship in Python Programming & Applied Artificial Intelligence',
     'Comprehensive AI internship covering Python, NumPy, Pandas, Scikit-Learn, Supervised/Unsupervised ML, Neural Networks and AI Deployment.',
     6, 120, 'Offline'),
    ('CS', 'Cyber Security & Ethical Hacking', 'Course-Based Internship in Cyber Security & Penetration Testing',
     'Industry cybersecurity program covering Network Security, Linux, Wireshark, OWASP Top 10, Cryptography, VAPT and Incident Response.',
     6, 120, 'Offline'),
    ('CC', 'Cloud Computing & DevOps', 'Course-Based Internship in Cloud Architecture & DevOps Engineering',
     'Enterprise cloud computing program covering AWS Core Services, Linux, Docker, CI/CD Automation, Kubernetes, Terraform and CloudWatch.',
     6, 120, 'Offline'),
    ('JV', 'Java Full Stack Development', 'Course-Based Internship in Enterprise Java & Spring Boot Development',
     'Enterprise application engineering covering Core Java, OOPs, Spring Boot, Hibernate ORM, MySQL, React Frontend and Microservices.',
     6, 120, 'Offline'),
    ('AD', 'Android & Mobile App Development', 'Course-Based Internship in Native Android & Mobile App Development',
     'Native mobile application development covering Kotlin, Android Jetpack Compose, MVVM Architecture, Room DB, Retrofit and Firebase.',
     6, 120, 'Offline')
]

MODULES_CATALOG = {
    'SOL-01': [
        (1, "Fundamentals of Solar Photovoltaics (PV) & Solar Geometry", "Photovoltaic cell physics, semiconductor junctions, solar spectrum, irradiance, azimuth, and optimal tilt angles.",
         ["Photovoltaic Effect & Semiconductor Principles", "Monocrystalline vs Polycrystalline vs Bifacial Panels", "Solar Irradiance, Peak Sun Hours (PSH) & Air Mass", "Solar Angles, Azimuth, Tilt & Shading Analysis"],
         ["Measurement of open-circuit voltage (Voc) and short-circuit current (Isc) under varying irradiance", "Using sun-path charts to determine seasonal shadow profiles"],
         ["Understand PV energy generation physics", "Calculate optimal solar orientation for geographical coordinates"], 14),
        (2, "Rooftop Solar Site Assessment & Structural Engineering", "Site survey methods, roof load-bearing capacity, wind speed standards, shading obstacles, and civil safety.",
         ["Structural Roof Assessment (RCC Flat Roof, Tin Shed, Tile Roof)", "Wind Velocity Analysis & IS 875 Part 3 Standards", "Rooftop Access, Walkways & Parapet Clearance", "Civil Anchor Fasteners & Deadweight Ballast Calculations"],
         ["Executing a 360-degree digital site survey of institutional rooftop", "Calculating wind thrust on elevated solar module tables"],
         ["Perform thorough rooftop structural viability audits", "Design wind-resistant ballast and anchor layouts"], 16),
        (3, "Building Integrated Photovoltaics (BIPV) Design", "Architectural integration of solar cells into building facades, skylights, canopies, and glazing.",
         ["BIPV Architecture vs Traditional Rooftop Systems", "Solar Glass, Facades & Building Envelope Integration", "Thermal Dissipation in BIPV Installations", "Aesthetic & Structural Architectural Standards"],
         ["Drafting a building facade solar integration layout", "Thermal modeling of semi-transparent solar glass modules"],
         ["Design architectural BIPV building installations", "Integrate solar generation seamlessly into building envelopes"], 16),
        (4, "Module Mounting Structures (MMS) Assembly & Alignment", "Aluminum & Hot-Dip Galvanized Iron (HDGI) structures, rafter assembly, mid/end clamps, torque tightening.",
         ["MMS Materials: Aluminum 6063 vs HDGI Steel", "Purlin, Rafter & Column Assembly Protocols", "Mid-Clamps & End-Clamps Installation with EPDM Rubber", "Torque Wrench Calibration & Corrosion Protection"],
         ["Assembling a 4-panel elevated mounting table with precision leveling", "Applying torque specifications to structure bolts"],
         ["Assemble heavy-duty solar mounting structures securely", "Prevent galvanic corrosion between dissimilar metals"], 16),
        (5, "DC Electrical Wiring, Stringing & Combiner Boxes", "Solar DC cable sizing, UV resistance, MC4 connectors, string calculation, and DC Array Junction Boxes (AJB).",
         ["Solar DC Cable Specifications (TUV 2 Pfg 1169)", "Voltage Drop Minimization & Cable Sizing Math", "MC4 Connector Crimping, Pin Insertion & Waterproof Testing", "DC Combiner Boxes, Fuses & Surge Protection Devices (SPD)"],
         ["Crimping professional MC4 connectors and testing contact resistance", "Wiring a 10-module series string with DC disconnect isolator"],
         ["Execute industry-standard DC wiring and stringing", "Ensure IP65/IP67 ingress protection on all outdoor DC joints"], 16),
        (6, "Inverter Interconnection, AC Distribution & Grid Sync", "On-grid string inverters, MPPT tracking, AC Distribution Board (ACDB), isolators, and grid synchronization.",
         ["Grid-Tied String Inverter Architecture & Efficiency Curves", "Maximum Power Point Tracking (MPPT) Algorithms", "ACDB Breakers, Earth Leakage Relays & Energy Meters", "Synchronization Criteria: Voltage, Frequency & Phase Angle"],
         ["Wiring an ACDB with 4-pole MCB and Type-2 AC SPD", "Configuring inverter grid-profile parameters for DISCOM standards"],
         ["Connect solar inverters to three-phase AC distribution boards", "Synchronize solar generation safely with the electrical grid"], 16),
        (7, "Earthing Pit Construction & Lightning Protection", "Chemical earthing, copper bonded rods, earth resistance testing, lightning arrestors (ESE).",
         ["Dedicated Solar Earthing vs Building Electrical Grounding", "Chemical Earth Pit Preparation (Bentonite / Marconite)", "Earth Resistance Measurement with 4-Terminal Earth Tester (< 2 Ohm)", "Early Streamer Emission (ESE) Lightning Arrestor Installation"],
         ["Constructing a maintenance-free chemical earthing pit", "Testing ground electrode resistance using fall-of-potential method"],
         ["Build low-resistance safety earthing networks", "Protect solar installations from lightning strikes and surges"], 14),
        (8, "Testing, Commissioning & Net-Metering Handover", "Pre-commissioning checklist, insulation resistance (Megger), anti-islanding test, DISCOM net-meter inspection.",
         ["Insulation Resistance (Megger) Testing on DC Strings", "Anti-Islanding Protection Functional Verification", "DISCOM Bidirectional Net-Meter Verification & Billing", "Project Documentation, SLD Drafting & Safety Handover"],
         ["Conducting Megger insulation resistance test at 1000V DC", "Performing live anti-islanding trip test with grid disconnection"],
         ["Commission rooftop solar systems according to national standards", "Complete DISCOM net-metering inspection dossiers"], 12)
    ],
    'SOL-02': [
        (1, "Civil Layout & Shadow Free Area Planning", "Site orientation, compass heading, magnetic declination, inter-row spacing, shadow analysis.",
         ["Civil Surveying Tools & Laser Distance Meters", "True North vs Magnetic North Correction", "Inter-Row Pitch Calculation to Eliminate 9am-3pm Shading", "Layout Optimization for Irregular Rooftops"],
         ["Marking column footing coordinates on a 500 sq. meter roof slab", "Plotting winter solstice shadow profiles"],
         ["Calculate exact row spacing without shading losses", "Lay out civil footprints efficiently"], 16),
        (2, "Structural Materials, Metallurgy & Anti-Corrosion", "HDG steel coating thickness (80+ microns), aluminum alloys, anodizing, stainless steel A2/A4 fasteners.",
         ["Hot Dip Galvanizing (IS 4759) & Micron Thickness Gauging", "Extruded Aluminum T6 Alloys & Tensile Strength", "Stainless Steel Fastener Grades (SS304 vs SS316)", "Preventing Galvanic Corrosion with Insulation Washers"],
         ["Measuring galvanizing thickness with digital coating gauge", "Testing tensile strength and fastener torque compliance"],
         ["Select corrosion-resistant structural materials", "Audit coating quality for 25-year outdoor durability"], 16),
        (3, "Foundation Systems & Anchor Fasteners", "Chemical anchor bolts, expansion anchors, concrete ballast blocks, penetration-free non-invasive mounting.",
         ["Chemical Anchoring (Hilti Epoxy / Vinylester Resin)", "Mechanical Wedge Anchors & Pull-Out Force Testing", "Prefabricated Concrete Ballast Blocks & Waterproofing Membranes", "Waterproof Sealants (Polyurethane & Bituminous Coatings)"],
         ["Drilling and installing chemical capsule anchors in RCC slab", "Applying waterproof chemical coatings over foundation pedestals"],
         ["Anchor solar structures firmly without leaking roof slabs", "Conduct pull-out load verification tests"], 16),
        (4, "Rafter, Purlin & Superstructure Assembly", "Structural member alignment, plumb-line verification, triangular truss assembly, tilt angle adjustment.",
         ["Truss Geometry: Fixed Tilt vs Seasonal Adjustable MMS", "Rafter & Purlin Splicing Protocols", "Leveling with Laser Line Levels and Plumb Bobs", "Diagonal Bracing & Wind Load Stiffeners"],
         ["Erecting a 15-degree seasonal adjustable solar truss superstructure", "Aligning purlin rails within +/- 2mm tolerance"],
         ["Assemble rigid solar superstructures accurately", "Ensure structural stability against heavy wind vibrations"], 18),
        (5, "Panel Clamping, Gasketing & Thermal Expansion", "Panel handling ergonomics, mid-clamp torqueing, end-clamp locking, EPDM rubber cushions, thermal gaps.",
         ["Safe Solar Panel Handling & Lifting Protocols", "Mid-Clamps & End-Clamps Locking Mechanisms", "Allowing Thermal Expansion Gaps Between Modules", "Micro-Crack Prevention & Pressure Distribution"],
         ["Mounting and clamping 12 bifacial solar modules on purlins", "Torque wrench verification of 12-14 Nm clamp specifications"],
         ["Install solar modules without micro-cracks or mechanical strain", "Apply uniform clamping force across solar arrays"], 18),
        (6, "Structural Earth Bonding & Quality Handover", "MMS grounding, bonding jumpers, serrated washers, quality assurance checklist, final certification.",
         ["Continuous Structure Earthing & Bonding Jumpers", "Star Washers for Anodized Aluminum Paint Penetration", "Structural Quality Punch List & Torque Marking", "Final Safety Sign-off & As-Built Structural Drawings"],
         ["Installing flexible copper bonding jumpers across all structure joints", "Conducting end-to-end structural continuity test (< 0.1 Ohm)"],
         ["Ensure 100% electrical continuity across all metal structures", "Deliver certified structural assembly sign-offs"], 16),
        (7, "Solar Structure Maintenance & Fastener Audits", "Periodic bolt torque checks, rust treatment, zinc spray application, storm damage remediation.",
         ["Preventive Structural Inspection Schedules", "Cold Galvanizing Zinc Spray Application on Scratch Marks", "Re-torquing Fasteners Post High-Wind Seasons", "Vibration Damper Inspection"],
         ["Conducting an annual structural integrity audit on existing array", "Applying zinc-rich primer to field-drilled holes"],
         ["Maintain solar structures over their 25-year operational lifecycle", "Remediate weather-induced structural loosening"], 10),
        (8, "Hands-on Capstone Installation Project", "End-to-end installation of a complete 5 kW solar mounting structure on live test bench.",
         ["Blueprint Reading & Material Requisition", "Civil Markings & Foundation Anchoring", "Superstructure Assembly & Plumb Alignment", "Panel Clamping & Bonding Jumper Verification", "Final Structural Dossier Preparation"],
         ["Complete physical installation and load testing of 5 kW structure"],
         ["Deliver certified commercial-grade solar structure installation"], 10)
    ]
}

def ensure_all_courses(cursor, conn):
    print("Ensuring all solar & technical courses, modules and batches are populated...")

    cursor.execute("UPDATE centre_settings SET verification_base_url = 'https://technoglobe-certificates.onrender.com', org_name = 'PODDAR COLLEGE OF TECHNOLOGY & MANAGEMENT', centre_name = 'PODDAR COLLEGE – BHARATPUR', phone = '9414293370', email = 'nitin@pctm', signatory_name = 'Nitin Agarwal', signatory_designation = 'Authority' WHERE id = 1")

    course_id_map = {}
    for code, name, title, desc, weeks, hours, mode in COURSES_CATALOG:
        cursor.execute("SELECT id FROM courses WHERE code = ?", (code,))
        row = cursor.fetchone()
        if row:
            c_id = row[0]
            cursor.execute("UPDATE courses SET name = ?, title = ?, description = ?, duration_weeks = ?, total_hours = ?, default_mode = ? WHERE id = ?", (name, title, desc, weeks, hours, mode, c_id))
        else:
            cursor.execute("INSERT INTO courses (code, name, title, description, duration_weeks, total_hours, default_mode) VALUES (?, ?, ?, ?, ?, ?, ?)", (code, name, title, desc, weeks, hours, mode))
            c_id = cursor.lastrowid
        course_id_map[code] = c_id

    for code, modules in MODULES_CATALOG.items():
        c_id = course_id_map.get(code)
        if not c_id:
            continue
        for mod_num, title, desc, topics, acts, outcomes, hours in modules:
            cursor.execute("SELECT id FROM course_modules WHERE course_id = ? AND module_number = ?", (c_id, mod_num))
            m_row = cursor.fetchone()
            if m_row:
                cursor.execute("UPDATE course_modules SET title = ?, description = ?, topics_json = ?, practical_activities_json = ?, learning_outcomes_json = ?, hours = ? WHERE id = ?", (title, desc, json.dumps(topics), json.dumps(acts), json.dumps(outcomes), hours, m_row[0]))
            else:
                cursor.execute("INSERT INTO course_modules (course_id, module_number, title, description, topics_json, practical_activities_json, learning_outcomes_json, hours) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (c_id, mod_num, title, desc, json.dumps(topics), json.dumps(acts), json.dumps(outcomes), hours))

    for code, c_id in course_id_map.items():
        batch_code = f"{code}-2026-B1"
        cursor.execute("SELECT id FROM batches WHERE course_id = ?", (c_id,))
        if not cursor.fetchone():
            m_id = 1 if 'SOL' in code else (2 if code in ['DA', 'AI', 'FS', 'JV', 'CS', 'CC', 'AD'] else 3)
            cursor.execute("INSERT INTO batches (course_id, batch_code, name, start_date, end_date, mentor_id, max_students) VALUES (?, ?, ?, '2026-06-01', '2026-07-12', ?, 35)", (c_id, batch_code, f"Summer Training 2026 - {code}", m_id))

    print("All courses, modules, and batches successfully synchronized.")

def ensure_institutions(cursor, conn):
    for inst in INSTITUTIONS_CATALOG:
        cursor.execute("""
        INSERT INTO institutions (
            id, code, name, full_name, tagline, address, affiliation_text, website, email, phone,
            logo_path, primary_color, secondary_color, accent_color, signatory_name, signatory_designation,
            stamp_mode, watermark_mode, doc_prefix, cert_prefix, is_active
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            code = excluded.code,
            name = excluded.name,
            full_name = excluded.full_name,
            tagline = excluded.tagline,
            address = excluded.address,
            affiliation_text = excluded.affiliation_text,
            website = excluded.website,
            email = excluded.email,
            phone = excluded.phone,
            logo_path = excluded.logo_path,
            primary_color = excluded.primary_color,
            secondary_color = excluded.secondary_color,
            accent_color = excluded.accent_color,
            signatory_name = excluded.signatory_name,
            signatory_designation = excluded.signatory_designation,
            stamp_mode = excluded.stamp_mode,
            watermark_mode = excluded.watermark_mode,
            doc_prefix = excluded.doc_prefix,
            cert_prefix = excluded.cert_prefix,
            is_active = 1
        """, inst)

def apply_faculty_updates(cursor, conn):
    ensure_institutions(cursor, conn)

    cursor.execute("""
    UPDATE centre_settings 
    SET signatory_name = 'Nitin Agarwal', 
        signatory_designation = 'Director',
        org_name = 'PODDAR COLLEGE OF TECHNOLOGY & MANAGEMENT',
        centre_name = 'PODDAR COLLEGE – BHARATPUR',
        address = 'Near SP Office, Bharatpur (Raj.)',
        phone = '9414293370',
        email = 'nitin_pitm@yahoo.com',
        website = 'https://poddarcollege.org',
        verification_base_url = 'https://technoglobe-certificates.onrender.com'
    WHERE id = 1
    """)

    cursor.execute("""
    INSERT INTO mentors (id, name, designation, email, phone, bio, is_active)
    VALUES 
    (1, 'Mahesh Chand Saini', 'Trainer', 'trainer@poswal.com', '9414694727', 'Lead Technical Trainer & Specialist in Solar PV Installation, Inverter Architecture, and Industrial Power Plants.', 1),
    (2, 'Krishlay', 'Faculty', 'krishlay@pctm', '9414293370', 'Supervising Faculty for Data Analytics, Computing, AI & Emerging Technologies.', 1),
    (3, 'Rahul', 'Faculty', 'rahul@pctm', '9414293370', 'Supervising Faculty for Digital Technologies, Information Systems & Web Engineering.', 1)
    ON CONFLICT(id) DO UPDATE SET
        name = excluded.name,
        designation = excluded.designation,
        email = excluded.email,
        phone = excluded.phone,
        bio = excluded.bio,
        is_active = 1
    """)

    cursor.execute("DELETE FROM users WHERE email IN ('vikas@technoglobe.co.in', 'viewer@technoglobe.co.in', 'admin@technoglobe.co.in', 'superadmin@technoglobe.co.in')")
    
    cursor.execute("SELECT id FROM users WHERE email = 'nitin@pctm'")
    if cursor.fetchone():
        cursor.execute("UPDATE users SET name = 'Nitin Agarwal', role = 'SUPER_ADMIN' WHERE email = 'nitin@pctm'")
    else:
        cursor.execute("INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?)",
                       ('Nitin Agarwal', 'nitin@pctm', hash_password('nitin321'), 'SUPER_ADMIN'))

    cursor.execute("SELECT id FROM users WHERE email = 'madhuvangurjar19@gmail.com'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?)",
                       ('Madhuvan Singh Gurjar', 'madhuvangurjar19@gmail.com', hash_password('poswal123'), 'SUPER_ADMIN'))

    cursor.execute("SELECT id FROM users WHERE email = 'trainer@poswal.com'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?)",
                       ('Mahesh Chand Saini', 'trainer@poswal.com', hash_password('trainer123'), 'CENTRE_ADMIN'))

    cursor.execute("SELECT id FROM users WHERE email = 'krishlay@pctm'")
    if cursor.fetchone():
        cursor.execute("UPDATE users SET name = 'Krishlay', role = 'SUPER_ADMIN' WHERE email = 'krishlay@pctm'")
    else:
        cursor.execute("INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?)",
                       ('Krishlay', 'krishlay@pctm', hash_password('krishlay321'), 'SUPER_ADMIN'))

    cursor.execute("SELECT id FROM users WHERE email = 'rahul@pctm'")
    if cursor.fetchone():
        cursor.execute("UPDATE users SET name = 'Rahul', role = 'SUPER_ADMIN' WHERE email = 'rahul@pctm'")
    else:
        cursor.execute("INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?)",
                       ('Rahul', 'rahul@pctm', hash_password('rahul321'), 'SUPER_ADMIN'))

    ensure_all_courses(cursor, conn)

def seed():
    init_db()
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM centre_settings")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
        INSERT INTO centre_settings (
            id, org_name, centre_name, centre_code, default_college, address, phone, email, website, auth_ref,
            signatory_name, signatory_designation, logo_url, signature_url, stamp_url,
            show_digital_signature, show_digital_stamp, cert_prefix, doc_prefix,
            default_required_hours, default_required_attendance_pct, verification_base_url
        ) VALUES (
            1,
            'PODDAR COLLEGE OF TECHNOLOGY & MANAGEMENT',
            'PODDAR COLLEGE – BHARATPUR',
            'PCTM-01',
            'Poddar College, Bharatpur',
            'Poddar College, Bharatpur, Rajasthan, India',
            '9414293370',
            'nitin@pctm',
            'https://poddarcollege.org',
            'PCTM/RAJ/BPT/2026-001',
            'Nitin Agarwal',
            'Authority',
            '', '', '',
            0, 0,
            'PCTM', 'PCTM/BPT',
            120, 75.0,
            'https://technoglobe-certificates.onrender.com'
        );
        """)
        apply_faculty_updates(cursor, conn)
    else:
        apply_faculty_updates(cursor, conn)

    conn.commit()
    conn.close()
    print("Database seeding, course catalog, institutions, and faculty updates complete.")

def delete_demo_data():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM students WHERE is_demo = 1")
    demo_student_ids = [r[0] for r in cursor.fetchall()]
    for s_id in demo_student_ids:
        cursor.execute("DELETE FROM students WHERE id = ?", (s_id,))
    conn.commit()
    conn.close()
    print("Demo data purged cleanly.")

if __name__ == '__main__':
    seed()
