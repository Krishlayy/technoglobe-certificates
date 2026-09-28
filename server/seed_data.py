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

# TechnoGlobe Bharatpur Institutions Catalog
INSTITUTIONS_CATALOG = [
    (1, 'TECHNOGLOBE', 'TechnoGlobe Bharatpur', 'TECHNOGLOBE - ADVANCED IT TRAINING & DEVELOPMENT', 'Transforming Careers Through Technology & Industry Excellence',
     'Near SP Office, Bharatpur (Rajasthan) 321001', 'Premier IT Training & Technical Development Institute • Bharatpur',
     'https://technoglobe.co.in', 'nitin_pitm@yahoo.com', '9414293370',
     'technoglobe_logo.png', '#0A2540', '#1E3A8A', '#EAA824',
     'Nitin Agarwal', 'Director / Center Head',
     'OFFICIAL_SEAL', 'TECHNOGLOBE_LOGO_TRANSLUCENT', 'TG/BPT', 'TG', 1)
]

# Comprehensive Courses Definition (TechnoGlobe Advanced IT & Engineering Curriculums)
COURSES_CATALOG = [
    ('DA', 'Data Analytics & Business Intelligence', 'Course-Based Internship in Data Analytics & Business Intelligence',
     'Comprehensive industry training covering Advanced Excel, SQL, Python, Power BI, Statistical Modeling, and Business Intelligence Dashboards.',
     6, 120, 'Offline'),
    ('FS', 'Full Stack Web Development (MERN)', 'Course-Based Internship in Full Stack Web Development (MERN Stack)',
     'Full stack engineering covering HTML5, CSS3, JavaScript ES6+, React.js, Node.js, Express.js, MongoDB, RESTful APIs, and Cloud Deployment.',
     6, 120, 'Offline'),
    ('AI', 'Python & Machine Learning / AI', 'Course-Based Internship in Python Programming & Applied Artificial Intelligence',
     'Comprehensive AI/ML internship covering Python, NumPy, Pandas, Scikit-Learn, Supervised/Unsupervised ML, Neural Networks, and Generative AI.',
     6, 120, 'Offline'),
    ('CS', 'Cyber Security & Ethical Hacking', 'Course-Based Internship in Cyber Security & Penetration Testing',
     'Hands-on cybersecurity program covering Network Security, Linux Administration, Wireshark, OWASP Top 10, Cryptography, VAPT, and Threat Defense.',
     6, 120, 'Offline'),
    ('JV', 'Java Full Stack Development', 'Course-Based Internship in Enterprise Java & Spring Boot Development',
     'Enterprise application engineering covering Core Java, OOPs, Spring Boot, Hibernate ORM, MySQL, Microservices Architecture, and React Frontend.',
     6, 120, 'Offline'),
    ('CC', 'Cloud Computing & DevOps', 'Course-Based Internship in Cloud Architecture & DevOps Engineering',
     'Enterprise cloud program covering AWS Core Services, Linux, Docker Containers, CI/CD Pipelines, Kubernetes, Terraform, and Cloud Monitoring.',
     6, 120, 'Offline'),
    ('AD', 'Android & Mobile App Development', 'Course-Based Internship in Native Android & Mobile App Development',
     'Native mobile application development covering Kotlin, Android Jetpack Compose, MVVM Architecture, Room Database, Retrofit, and Firebase.',
     6, 120, 'Offline'),
    ('DM', 'Digital Marketing & Growth Strategies', 'Course-Based Internship in Digital Marketing & Growth Strategies',
     'Practical growth marketing covering Search Engine Optimization (SEO), Social Media Marketing (SMM), Google Ads, Content Marketing, Analytics, and Performance Growth.',
     6, 120, 'Offline')
]

MODULES_CATALOG = {
    'DA': [
        (1, "Advanced Excel & Data Modeling", "Mastering complex formulas, pivot tables, XLOOKUP, power query, and dynamic financial/analytical models.",
         ["Advanced Formulas (INDEX/MATCH, XLOOKUP, Nested IFs)", "Data Cleaning & Transformation via Power Query", "Dynamic Pivot Tables & Slicers", "What-If Analysis & Goal Seek"],
         ["Building an Automated Sales Reporting Dashboard", "Reconciling multi-source institutional dataset with Power Query"],
         ["Clean and structure raw enterprise datasets", "Construct dynamic KPI calculation models in Excel"], 14),
        (2, "Relational Databases & SQL Querying", "Database normalization, SQL syntax, joins, aggregations, window functions, and subqueries.",
         ["Relational Schema Design & Constraints", "Complex JOINS (INNER, LEFT, FULL, CROSS)", "Aggregate Functions & GROUP BY / HAVING", "Window Functions (ROW_NUMBER, RANK, DENSE_RANK, LAG/LEAD)"],
         ["Writing complex analytical queries on multi-million row SQLite database", "Executing data pipeline ETL queries"],
         ["Extract and transform business data with SQL", "Optimize query performance for analytical reporting"], 16),
        (3, "Python for Data Analysis (NumPy & Pandas)", "Python data manipulation, vectorization, dataframe slicing, handling missing values, and time-series.",
         ["NumPy Multidimensional Arrays & Vectorized Ops", "Pandas DataFrames, Series & Indexing", "Handling Missing Data, Imputation & Outlier Detection", "Time Series Resampling & Rolling Statistics"],
         ["Analyzing a 5-year retail dataset using Pandas", "Automating weekly ETL pipelines with Python scripts"],
         ["Manipulate large data structures programmatically", "Perform automated exploratory data analysis (EDA)"], 16),
        (4, "Data Visualization & Exploratory Analysis", "Visual storytelling using Matplotlib, Seaborn, and interactive Plotly charts.",
         ["Design Principles for Effective Visual Storytelling", "Statistical Plots (Histograms, Boxplots, Heatmaps)", "Categorical & Multivariate Visualizations", "Interactive Visualizations with Plotly"],
         ["Creating an interactive correlation and distribution dashboard", "Plotting customer cohort retention heatmaps"],
         ["Translate complex numbers into intuitive executive charts", "Identify underlying data anomalies through visualization"], 16),
        (5, "Power BI Dashboard Engineering & DAX", "Power BI Desktop, data modeling (Star Schema), DAX measures, calculated columns, and publishing.",
         ["Star Schema & Snowflake Data Modeling", "DAX Calculated Measures vs Calculated Columns", "Time Intelligence Functions (YTD, MTD, YoY Growth)", "Interactive Visual Drill-throughs, Bookmarks & Tooltips"],
         ["Developing an enterprise Executive KPI Dashboard in Power BI", "Implementing role-level security and published workspaces"],
         ["Architect enterprise-grade Power BI report suites", "Write advanced DAX expressions for financial metrics"], 16),
        (6, "Applied Statistics & Predictive Analytics", "Descriptive statistics, hypothesis testing, linear regression, logistic classification, and model metrics.",
         ["Probability Distributions & Central Limit Theorem", "Hypothesis Testing (t-test, ANOVA, Chi-Square)", "Linear & Multiple Regression Modeling", "Classification Metrics (Confusion Matrix, Precision/Recall, ROC-AUC)"],
         ["Building a predictive sales forecasting model in Python", "Conducting A/B testing statistical significance analysis"],
         ["Apply rigorous statistical methods to business decisions", "Deploy foundational machine learning models for forecasting"], 16),
        (7, "ETL Pipelines & Automated Reporting", "Automating data ingest, API fetching, scheduled report generation, and data governance.",
         ["ETL vs ELT Workflows & Architecture", "Automating Data Extraction from REST APIs", "Scheduled Python CRON Scripts & Email Alerts", "Data Quality Auditing & Error Handling"],
         ["Building an automated end-to-end pipeline from API to Power BI", "Writing data consistency validation scripts"],
         ["Maintain dependable data pipelines without manual touch", "Ensure high data fidelity and compliance across reports"], 14),
        (8, "Capstone Business Intelligence Project", "Comprehensive real-world BI implementation with live presentation and executive briefing.",
         ["Business Problem Framing & Scope Definition", "Data Extraction, Cleansing & Modeling", "Interactive Multi-Page Power BI Dashboard Creation", "Executive Presentation & Insights Delivery"],
         ["End-to-end deployment of an Enterprise Analytics Suite"],
         ["Deliver a complete professional analytics solution from raw data to board-level presentation"], 12)
    ],
    'FS': [
        (1, "Modern Frontend Foundations (HTML5, Modern CSS & JS ES6+)", "Semantic HTML, CSS Flexbox/Grid, Responsive Design, and modern ES6+ JavaScript features.",
         ["HTML5 Semantic Tags & Accessibility", "CSS3 Flexbox, CSS Grid & Tailwind CSS", "JavaScript ES6+ (Arrow Functions, Destructuring, Promises, Async/Await)", "DOM Manipulation & Event Loop Mechanics"],
         ["Building a fully responsive multi-page web application with Tailwind CSS", "Asynchronous API client implementation"],
         ["Build modern, accessible responsive web layouts", "Master asynchronous JavaScript programming"], 14),
        (2, "React.js Component Architecture & State Management", "Component lifecycle, Hooks (useState, useEffect, useContext, useMemo), custom hooks, and routing.",
         ["JSX Syntax & Component Composition", "React Hooks (useState, useEffect, useRef, useMemo, useCallback)", "Client-side Routing with React Router v6", "Context API & Global State Management"],
         ["Creating a feature-rich dynamic Single Page Application (SPA)", "Building custom reusable hooks for data fetching"],
         ["Architect scalable React component trees", "Manage complex application state cleanly"], 16),
        (3, "Backend Development with Node.js & Express.js", "Server setup, routing, middleware, RESTful API design, authentication, and file handling.",
         ["Node.js Event-driven Architecture & Modules", "Express.js Routing, Middleware & Error Handling", "RESTful API Design Standards & HTTP Status Codes", "JWT Authentication, Bcrypt Password Hashing & CORS"],
         ["Building a secure REST API with JWT auth and validation middleware", "Implementing role-based access control (RBAC)"],
         ["Develop secure and high-throughput server backends", "Design standard compliant REST APIs"], 16),
        (4, "Database Engineering with MongoDB & Mongoose", "NoSQL database design, schemas, CRUD operations, indexing, aggregation pipelines, and transactions.",
         ["MongoDB Document Architecture vs Relational DBs", "Mongoose Schema Validation & Middleware Hooks", "Advanced Aggregation Pipelines ($match, $group, $lookup, $project)", "Database Indexing & Performance Optimization"],
         ["Designing an e-commerce database schema with Mongoose", "Building complex aggregation queries for business reporting"],
         ["Model scalable NoSQL database structures", "Perform fast aggregations and indexing on MongoDB"], 16),
        (5, "Full Stack Integration & State Management", "Connecting React frontend to Express backend, Axios interceptors, TanStack React Query, and state sync.",
         ["API Integration with Axios & Global Interceptors", "Server State Caching with TanStack React Query", "Optimistic UI Updates & Error Boundary Handling", "File Upload Handling (Multer & Cloudinary)"],
         ["Connecting React SPA with backend authentication and CRUD operations", "Implementing real-time UI notifications"],
         ["Bridge frontend and backend seamlessly with resilient error handling", "Implement optimistic updates and caching"], 16),
        (6, "Real-Time Communication & WebSockets", "Full duplex communication using Socket.io, real-time messaging, notifications, and room broadcasting.",
         ["WebSocket Protocol vs HTTP Polling", "Socket.io Server & Client Event Handling", "Rooms, Namespaces & Broadcasting", "Real-Time State Synchronization"],
         ["Building a real-time collaborative chat and notification application", "Handling connection lifecycles and reconnects"],
         ["Implement real-time interactive user experiences", "Manage persistent WebSocket channels reliably"], 16),
        (7, "Testing, Security & Performance Optimization", "Unit testing, integration testing, API security (Helmet, Rate Limiting), bundle optimization, and caching.",
         ["API Security Best Practices (Helmet, Rate Limiting, XSS & SQLi Defense)", "Frontend Bundle Optimization & Code Splitting", "Unit & Integration Testing (Jest, React Testing Library)", "Redis Caching for High-Volume Endpoints"],
         ["Securing Express endpoints with rate limiters and sanitization", "Running test suites and optimizing build bundles"],
         ["Harden applications against common security vulnerabilities", "Optimize frontend load times and server throughput"], 14),
        (8, "Capstone Full Stack Application Deployment", "End-to-end full stack SaaS application deployment on cloud platforms with CI/CD and custom domains.",
         ["Docker Containerization of MERN Stack", "Cloud Deployment (Render, Vercel, AWS)", "Environment Variables & Production Config Management", "Final Capstone Presentation & Code Review"],
         ["Deploying a live production-grade MERN web application with SSL & CI/CD"],
         ["Deliver a production-ready, cloud-hosted web application"], 12)
    ],
    'AI': [
        (1, "Python Core for Scientific Computing", "Advanced Python constructs, object-oriented design, functional paradigms, and package management.",
         ["Advanced Python Features (Generators, Decorators, Context Managers)", "Object-Oriented Programming (OOP) for Machine Learning", "Virtual Environments & Package Management (pip, uv, poetry)", "Profiling & Performance Optimization"],
         ["Building a custom data processing library with Python OOP", "Benchmarking execution times of algorithmic approaches"],
         ["Write clean, modular, and performant Python code", "Structure professional Python project repositories"], 14),
        (2, "Numerical Computing & Data Slicing (NumPy & Pandas)", "Vectorized operations, multidimensional slicing, broadcasting, Pandas manipulations, and cleaning.",
         ["NumPy Array Broadcasting & Linear Algebra", "Pandas Data Ingestion, Slicing & Grouping", "Data Imputation, Outlier Treatment & Encoding", "High-Performance Data Pipelines"],
         ["Processing high-dimensional sensor datasets with NumPy", "Cleaning unstructured tabular datasets for ML readiness"],
         ["Manipulate multi-dimensional tensors and dataframes", "Build robust preprocessing pipelines for machine learning"], 16),
        (3, "Supervised Machine Learning (Regression & Classification)", "Scikit-Learn, cost functions, gradient descent, linear models, tree models, and ensemble methods.",
         ["Linear & Ridge/Lasso Regression Algorithms", "Logistic Regression & Decision Trees", "Ensemble Methods (Random Forests, Gradient Boosting, XGBoost)", "Hyperparameter Tuning (GridSearchCV, RandomizedSearchCV)"],
         ["Training and optimizing an XGBoost classification model", "Evaluating models with cross-validation and confusion matrices"],
         ["Train, evaluate, and tune supervised ML algorithms", "Select appropriate evaluation metrics for business problems"], 16),
        (4, "Unsupervised Learning & Dimensionality Reduction", "Clustering algorithms (K-Means, DBSCAN), PCA, t-SNE, and anomaly detection techniques.",
         ["K-Means Clustering & Elbow Method Evaluation", "Density-Based Spatial Clustering (DBSCAN)", "Principal Component Analysis (PCA) & Variance Ratio", "Anomaly Detection via Isolation Forests"],
         ["Customer segmentation analysis on multi-feature behavioral data", "Reducing 100+ feature datasets with PCA for visualization"],
         ["Discover hidden patterns in unlabeled datasets", "Perform dimensionality reduction without losing critical variance"], 16),
        (5, "Deep Learning Foundations & Neural Networks (PyTorch)", "Perceptrons, multi-layer neural networks, backpropagation, activation functions, and PyTorch tensors.",
         ["Neural Network Mathematics & Backpropagation", "Activation Functions (ReLU, Sigmoid, GeLU, Softmax)", "PyTorch Tensors, Autograd & Custom Dataset Loaders", "Training Loops, Loss Functions & Adam Optimizer"],
         ["Building and training a multi-layer perceptron from scratch in PyTorch", "Visualizing loss curves and preventing overfitting"],
         ["Construct and train deep neural networks in PyTorch", "Debug gradient flow and neural network convergence"], 16),
        (6, "Computer Vision & Convolutional Neural Networks (CNN)", "Image processing, OpenCV, CNN architectures (ResNet, MobileNet), transfer learning, and object detection.",
         ["Image Processing with OpenCV (Filters, Transforms, Contours)", "Convolutional, Pooling & Dense Layer Architecture", "Transfer Learning with Pre-trained ResNet/EfficientNet", "Image Classification & Real-time Inference"],
         ["Building a custom image classification model with Transfer Learning", "Real-time webcam inference pipeline with OpenCV"],
         ["Implement deep learning solutions for computer vision", "Apply transfer learning to custom image datasets"], 16),
        (7, "Natural Language Processing (NLP) & Large Language Models", "Text preprocessing, tokenization, embeddings (Word2Vec, BERT), Transformers, and LLM APIs.",
         ["Text Tokenization, Lemmatization & Vectorization", "Word Embeddings & Transformer Architecture (Self-Attention)", "Fine-Tuning Hugging Face Models for Sentiment Analysis", "Building LLM-Powered Apps with LangChain & OpenAI/Gemini APIs"],
         ["Developing a retrieval-augmented question-answering assistant", "Fine-tuning a transformer model on customer review texts"],
         ["Process textual data with modern NLP techniques", "Integrate state-of-the-art LLMs into functional applications"], 14),
        (8, "Capstone Applied AI Project Deployment", "Packaging AI models as REST APIs using FastAPI, Dockerizing, and deploying to cloud infrastructure.",
         ["Building High-Performance Model Inference APIs with FastAPI", "Containerizing PyTorch/Scikit-Learn Models with Docker", "Cloud Deployment & GPU Inference Optimization", "Final Project Demonstration & Technical Walkthrough"],
         ["Deploying a live AI inference web application with FastAPI and Docker"],
         ["Deliver end-to-end production AI application from dataset to live API"], 12)
    ],
    'CS': [
        (1, "Fundamentals of Information Security & Networking", "OSI model, TCP/IP protocols, subnetting, packet analysis with Wireshark, and cryptography basics.",
         ["OSI & TCP/IP Model Layers & Protocol Analysis", "Subnetting, Routing & Firewall Concepts", "Packet Sniffing & Inspection with Wireshark", "Symmetric vs Asymmetric Cryptography (AES, RSA, ECC)"],
         ["Analyzing network traffic capture to detect cleartext passwords", "Configuring firewall iptables rules in Linux"],
         ["Analyze network packet streams for anomalies", "Apply cryptographic primitives to protect sensitive data"], 14),
        (2, "Linux Administration & Command Line Mastery", "Linux file system permissions, user administration, systemd services, SSH hardening, and shell scripting.",
         ["Linux File Hierarchy, Permissions & ACLs", "Process Management, Daemons & Cron Automation", "SSH Key-based Authentication & Hardening", "Bash Scripting for Automated Security Auditing"],
         ["Automating Linux system hardening checks with Bash scripts", "Configuring secure chroot and SSH bastion environments"],
         ["Administer secure Linux enterprise environments", "Automate routine security tasks with shell scripts"], 16),
        (3, "Web Application Security & OWASP Top 10", "SQL Injection, Cross-Site Scripting (XSS), CSRF, Broken Auth, and server-side request forgery (SSRF).",
         ["SQL Injection (In-band, Error-based, Blind) & Remediation", "Cross-Site Scripting (Reflected, Stored, DOM-based)", "Broken Authentication & Session Management Flaws", "Server-Side Request Forgery (SSRF) & Security Misconfigurations"],
         ["Exploiting and patching OWASP Top 10 vulnerabilities on test lab", "Configuring Content Security Policy (CSP) headers"],
         ["Identify critical web vulnerabilities in source code and live apps", "Remediate application flaws using defense-in-depth"], 16),
        (4, "Reconnaissance & Vulnerability Assessment", "Passive/active reconnaissance, Nmap scanning, OSINT, vulnerability scanners (OpenVAS, Nessus), and CVE tracking.",
         ["Passive Reconnaissance & OSINT Frameworks", "Nmap Port Scanning, NSE Scripts & Service Enumeration", "Vulnerability Scanning with Nessus & OpenVAS", "CVE Analysis, CVSS Scoring & Risk Prioritization"],
         ["Executing a full network perimeter vulnerability scan", "Compiling a prioritized vulnerability mitigation report"],
         ["Map enterprise attack surfaces methodically", "Evaluate vulnerabilities and formulate remediation timelines"], 16),
        (5, "Penetration Testing & Exploitation Frameworks", "Metasploit framework, payload generation, privilege escalation (Windows/Linux), and lateral movement.",
         ["Metasploit Framework Architecture & Modules", "Payload Crafting (MSFVenom) & Handler Setup", "Linux & Windows Privilege Escalation Vectors", "Post-Exploitation & Credential Harvesting"],
         ["Conducting an authorized simulated penetration test on target machine", "Exploiting misconfigured SUID binaries for privilege escalation"],
         ["Execute controlled penetration testing engagements", "Identify privilege escalation vectors and patch them"], 16),
        (6, "Wireless & Endpoint Security", "WPA2/WPA3 auditing, Evil Twin attacks, endpoint detection & response (EDR), and antivirus evasion defense.",
         ["Wi-Fi Security Protocols (WPA2-PSK, WPA3, 802.1X)", "Deauthentication & Handshake Capture Analysis", "Endpoint Security Architecture (Antivirus, EDR, HIDS)", "Malware Analysis Fundamentals & Sandboxing"],
         ["Capturing and auditing Wi-Fi authentication handshakes in controlled lab", "Analyzing malicious executable behavior in sandbox"],
         ["Secure wireless networks against unauthorized interception", "Evaluate endpoint defense mechanisms against malware"], 16),
        (7, "Incident Response, Digital Forensics & SOC Operations", "SIEM tools (Splunk, ELK), log analysis, memory forensics (Volatility), and incident handling procedures.",
         ["Security Information & Event Management (SIEM) Operations", "Log Analysis for Indicators of Compromise (IoCs)", "Memory Forensics & Dump Analysis with Volatility", "NIST Incident Handling Lifecycle (Preparation, Containment, Eradication)"],
         ["Investigating simulated breach timeline using SIEM logs", "Extracting compromised process artifacts from memory dump"],
         ["Respond efficiently to live cyber incidents", "Perform forensic evidence collection and analysis"], 14),
        (8, "Capstone Penetration Testing & VAPT Audit", "Comprehensive end-to-end vulnerability assessment and penetration test with formal executive report.",
         ["Scope Agreement & Rules of Engagement", "Complete VAPT Execution across Network & Web Assets", "Executive Risk Scoring & Remediation Roadmap Drafting", "Technical Debrief & Remediation Verification"],
         ["Delivering a full commercial-grade VAPT report for target organization"],
         ["Produce professional cybersecurity audit reports with remediation strategies"], 12)
    ]
}

# Add default modules for other IT courses
for code in ['JV', 'CC', 'AD', 'DM']:
    if code not in MODULES_CATALOG:
        MODULES_CATALOG[code] = [
            (1, "Fundamentals & Core Foundations", "Essential domain concepts, syntax, tooling, and environment setup.",
             ["Domain Architecture & Standards", "Environment Setup & Tooling", "Core Principles & Best Practices", "Foundational Lab Work"],
             ["Initial configuration and baseline project setup", "Verifying environment toolchains"],
             ["Master fundamental domain concepts", "Configure professional development environments"], 14),
            (2, "Intermediate Engineering & Implementation", "Hands-on implementation of core technical components.",
             ["Component Design & Architecture", "Data Handling & Processing", "API & Interface Integration", "Error Handling Protocols"],
             ["Implementing core functional modules", "Conducting verification tests"],
             ["Implement robust technical components", "Integrate modular interfaces cleanly"], 16),
            (3, "Advanced Features & Enterprise Architecture", "Scalability, performance, security, and advanced configurations.",
             ["Advanced Design Patterns", "Performance Optimization", "Security Best Practices", "Scalable Infrastructure"],
             ["Building advanced feature sets with optimal performance", "Executing performance profiling"],
             ["Architect scalable enterprise solutions", "Apply security and optimization best practices"], 16),
            (4, "Testing, Debugging & Quality Assurance", "Comprehensive testing, debugging, code review, and QA verification.",
             ["Automated Testing Frameworks", "Debugging Workflows & Tooling", "Code Quality Auditing", "Regression Testing"],
             ["Writing unit and integration test suites", "Resolving identified defects and bottlenecks"],
             ["Ensure software quality through rigorous testing", "Eliminate defects and regressions"], 16),
            (5, "Integration & Lifecycle Management", "Connecting multi-tier systems, CI/CD automation, and deployment pipelines.",
             ["System Integration Protocols", "CI/CD Pipeline Configuration", "Release Management & Versioning", "Monitoring & Logging"],
             ["Configuring automated deployment pipelines", "Setting up health monitors and telemetry"],
             ["Manage complete software lifecycles", "Deploy automated release pipelines"], 16),
            (6, "Security, Governance & Compliance", "Ensuring regulatory compliance, data protection, and governance.",
             ["Security Hardening & Access Control", "Compliance Standards & Auditing", "Data Protection & Privacy", "Documentation Standards"],
             ["Conducting comprehensive security and compliance audits", "Finalizing compliance documentation"],
             ["Maintain rigorous security compliance", "Ensure data protection standards"], 16),
            (7, "Practical Case Studies & Mini-Projects", "Real-world scenario simulations and industry case study execution.",
             ["Industry Case Study Analysis", "Problem-Solving Simulations", "Cross-Functional Collaboration", "Sprint Reviews"],
             ["Executing an end-to-end practical case study project", "Presenting technical findings"],
             ["Solve real-world industry technical problems", "Collaborate within modern sprint cycles"], 14),
            (8, "Capstone Project & Technical Certification", "Final comprehensive project execution, presentation, and certification review.",
             ["Capstone Specification & Milestones", "Implementation & Integration", "Final Technical Documentation", "Oral Defense & Demonstration"],
             ["Delivering the final comprehensive capstone project with live demonstration"],
             ["Deliver production-grade capstone project and earn certification"], 12)
        ]

def sync_courses_and_modules(cursor, conn):
    print("Synchronizing TechnoGlobe IT courses and modules...")
    course_id_map = {}
    for code, name, title, desc, weeks, hours, mode in COURSES_CATALOG:
        cursor.execute("SELECT id FROM courses WHERE code = ?", (code,))
        row = cursor.fetchone()
        if row:
            c_id = row[0]
            cursor.execute("""
                UPDATE courses 
                SET name = ?, title = ?, description = ?, duration_weeks = ?, total_hours = ?, default_mode = ?, is_active = 1 
                WHERE id = ?
            """, (name, title, desc, weeks, hours, mode, c_id))
        else:
            cursor.execute("""
                INSERT INTO courses (code, name, title, description, duration_weeks, total_hours, default_mode, is_active) 
                VALUES (?, ?, ?, ?, ?, ?, ?, 1)
            """, (code, name, title, desc, weeks, hours, mode))
            c_id = cursor.lastrowid
        course_id_map[code] = c_id

    # Clean up non-TechnoGlobe courses (e.g. SOL-*)
    cursor.execute("UPDATE courses SET is_active = 0 WHERE code LIKE 'SOL-%'")

    # Synchronize modules
    for code, modules in MODULES_CATALOG.items():
        c_id = course_id_map.get(code)
        if not c_id:
            continue
        for mod_num, title, desc, topics, acts, outcomes, hours in modules:
            cursor.execute("SELECT id FROM course_modules WHERE course_id = ? AND module_number = ?", (c_id, mod_num))
            m_row = cursor.fetchone()
            if m_row:
                cursor.execute("""
                    UPDATE course_modules 
                    SET title = ?, description = ?, topics_json = ?, practical_activities_json = ?, learning_outcomes_json = ?, hours = ? 
                    WHERE id = ?
                """, (title, desc, json.dumps(topics), json.dumps(acts), json.dumps(outcomes), hours, m_row[0]))
            else:
                cursor.execute("""
                    INSERT INTO course_modules (course_id, module_number, title, description, topics_json, practical_activities_json, learning_outcomes_json, hours) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (c_id, mod_num, title, desc, json.dumps(topics), json.dumps(acts), json.dumps(outcomes), hours))

    # Synchronize batches
    for code, c_id in course_id_map.items():
        batch_code = f"TG-{code}-2026-B1"
        cursor.execute("SELECT id FROM batches WHERE course_id = ?", (c_id,))
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO batches (course_id, batch_code, name, start_date, end_date, mentor_id, max_students) 
                VALUES (?, ?, ?, '2026-06-01', '2026-07-12', 1, 35)
            """, (c_id, batch_code, f"TechnoGlobe Summer Training 2026 - {code}"))

    print("[OK] TechnoGlobe IT courses, modules, and batches synchronized.")

def seed():
    init_db()
    conn = get_db()
    cursor = conn.cursor()

    # 1. Ensure Centre Settings
    cursor.execute("""
    INSERT INTO centre_settings (
        id, org_name, centre_name, centre_code, default_college, address, phone, email, website, auth_ref,
        signatory_name, signatory_designation, logo_url, signature_url, stamp_url,
        show_digital_signature, show_digital_stamp, cert_prefix, doc_prefix,
        default_required_hours, default_required_attendance_pct, verification_base_url
    ) VALUES (
        1,
        'TECHNOGLOBE',
        'TECHNOGLOBE – BHARATPUR',
        'TG-BPT-01',
        'TechnoGlobe Institute of Information Technology, Bharatpur',
        'Near SP Office, Bharatpur (Raj.) 321001',
        '9414293370',
        'nitin_pitm@yahoo.com',
        'https://technoglobe.co.in',
        'TG/RAJ/BPT/2026-001',
        'Nitin Agarwal',
        'Director / Center Head',
        'technoglobe_logo.png',
        'nitin_sign.png',
        'poddar_stamp.png',
        1, 1,
        'TG', 'TG/BPT',
        120, 75.0,
        'https://technoglobe-certificates.onrender.com'
    )
    ON CONFLICT(id) DO UPDATE SET
        org_name = 'TECHNOGLOBE',
        centre_name = 'TECHNOGLOBE – BHARATPUR',
        centre_code = 'TG-BPT-01',
        default_college = 'TechnoGlobe Institute of Information Technology, Bharatpur',
        address = 'Near SP Office, Bharatpur (Raj.) 321001',
        phone = '9414293370',
        email = 'nitin_pitm@yahoo.com',
        website = 'https://technoglobe.co.in',
        auth_ref = 'TG/RAJ/BPT/2026-001',
        signatory_name = 'Nitin Agarwal',
        signatory_designation = 'Director / Center Head',
        logo_url = 'technoglobe_logo.png',
        signature_url = 'nitin_sign.png',
        stamp_url = 'poddar_stamp.png',
        show_digital_signature = 1,
        show_digital_stamp = 1,
        cert_prefix = 'TG',
        doc_prefix = 'TG/BPT',
        verification_base_url = 'https://technoglobe-certificates.onrender.com'
    """)

    # 2. Ensure Institutions Catalog
    cursor.execute("UPDATE internships SET institution_id = 1 WHERE institution_id != 1")
    cursor.execute("UPDATE appreciation_certificates SET institution_id = 1 WHERE institution_id != 1")
    cursor.execute("DELETE FROM institutions WHERE id != 1")
    for inst in INSTITUTIONS_CATALOG:
        cursor.execute("SELECT id FROM institutions WHERE id = ?", (inst[0],))
        if cursor.fetchone():
            cursor.execute("""
            UPDATE institutions SET
                code = ?, name = ?, full_name = ?, tagline = ?, address = ?, affiliation_text = ?,
                website = ?, email = ?, phone = ?, logo_path = ?, primary_color = ?, secondary_color = ?,
                accent_color = ?, signatory_name = ?, signatory_designation = ?, stamp_mode = ?,
                watermark_mode = ?, doc_prefix = ?, cert_prefix = ?, is_active = 1
            WHERE id = ?
            """, (inst[1], inst[2], inst[3], inst[4], inst[5], inst[6], inst[7], inst[8], inst[9], inst[10],
                  inst[11], inst[12], inst[13], inst[14], inst[15], inst[16], inst[17], inst[18], inst[19], inst[0]))
        else:
            cursor.execute("""
            INSERT INTO institutions (
                id, code, name, full_name, tagline, address, affiliation_text, website, email, phone,
                logo_path, primary_color, secondary_color, accent_color, signatory_name, signatory_designation,
                stamp_mode, watermark_mode, doc_prefix, cert_prefix, is_active
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, inst)

    # 3. Ensure Mentors / Faculty
    cursor.execute("""
    INSERT INTO mentors (id, name, designation, email, phone, bio, is_active)
    VALUES 
    (1, 'Krishlay', 'Lead Technical Trainer & Faculty', 'krishlay@technoglobe.co.in', '9414293370', 'Senior Technical Trainer for Full Stack Development, Data Analytics, Python & Applied AI.', 1),
    (2, 'Rahul', 'Senior Faculty & Systems Lead', 'rahul@technoglobe.co.in', '9414293370', 'Senior Faculty for Cloud Architecture, Cyber Security & Enterprise Computing.', 1)
    ON CONFLICT(id) DO UPDATE SET
        name = excluded.name,
        designation = excluded.designation,
        email = excluded.email,
        phone = excluded.phone,
        bio = excluded.bio,
        is_active = 1
    """)

    # 4. Ensure Users
    cursor.execute("DELETE FROM users WHERE role = 'VIEWER'")
    
    users_to_seed = [
        ('Nitin Agarwal', 'nitin@technoglobe.co.in', 'nitin321', 'SUPER_ADMIN'),
        ('Nitin Agarwal', 'nitin_pitm@yahoo.com', 'nitin321', 'SUPER_ADMIN'),
        ('Krishlay', 'krishlay@technoglobe.co.in', 'krishlay321', 'SUPER_ADMIN'),
        ('Rahul', 'rahul@technoglobe.co.in', 'rahul321', 'SUPER_ADMIN')
    ]
    for u_name, u_email, u_pass, u_role in users_to_seed:
        cursor.execute("SELECT id FROM users WHERE email = ?", (u_email,))
        if cursor.fetchone():
            cursor.execute("UPDATE users SET name = ?, role = ?, password_hash = ? WHERE email = ?", (u_name, u_role, hash_password(u_pass), u_email))
        else:
            cursor.execute("INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?)",
                           (u_name, u_email, hash_password(u_pass), u_role))

    # 5. Sync Courses
    sync_courses_and_modules(cursor, conn)

    conn.commit()
    conn.close()
    print("[OK] TechnoGlobe Bharatpur database seeded cleanly.")

if __name__ == '__main__':
    seed()
