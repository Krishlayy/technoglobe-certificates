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

# 9 Full Industry Courses Definition
COURSES_CATALOG = [
    ('DA', 'Data Analytics', 'Course-Based Internship in Data Analytics & Business Intelligence',
     'Industry-aligned comprehensive internship covering Excel, SQL, Python, Power BI, Statistics and Capstone Analytics.',
     6, 120, 'Offline'),
    ('DM', 'Digital Marketing', 'Course-Based Internship in Digital Marketing & Growth Strategies',
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
    ('BI', 'Bioinformatics & Computational Biology', 'Course-Based Internship in Bioinformatics & Biological Data Science',
     'Computational biology internship covering BioPython, Genomic Sequences, NCBI/BLAST Querying, PDB Structural Modeling and Biostatistics.',
     6, 120, 'Offline'),
    ('AD', 'Android & Mobile App Development', 'Course-Based Internship in Native Android & Mobile App Development',
     'Native mobile application development covering Kotlin, Android Jetpack Compose, MVVM Architecture, Room DB, Retrofit and Firebase.',
     6, 120, 'Offline')
]

MODULES_CATALOG = {
    'DA': [
        (1, "Introduction to Data Analytics", "Data analytics fundamentals, types of data, analytics lifecycle, business problems and analytical thinking.",
         ["Data Analytics Fundamentals", "Types of Data (Structured vs Unstructured)", "Data Analytics Lifecycle", "Business Problems & Analytical Thinking", "Metrics & KPIs"],
         ["Case study evaluation on real-world retail problems", "Mapping business questions to data metrics"],
         ["Understand analytics workflow", "Formulate clear business questions"], 12),
        (2, "Microsoft Excel", "Spreadsheet data cleaning, formatting, formulas, functions, lookup functions, pivot tables, dynamic dashboards, data validation, what-if analysis.",
         ["Data Cleaning & Formatting", "Formulas & Mathematical Functions", "Lookup Functions (XLOOKUP, VLOOKUP, INDEX-MATCH)", "Pivot Tables & Pivot Charts", "Interactive Dashboards", "Data Validation & What-If Analysis"],
         ["Building a dynamic sales tracker in Excel", "Automated executive summary dashboard"],
         ["Proficiency in advanced Excel functions", "Create interactive business dashboards"], 14),
        (3, "SQL", "Database fundamentals, tables and relationships, SELECT, WHERE, GROUP BY, ORDER BY, JOINs, aggregations, subqueries, CTEs, practical SQL exercises.",
         ["Database Architecture & RDBMS", "SELECT, WHERE, ORDER BY, GROUP BY", "JOINs (INNER, LEFT, RIGHT, FULL)", "Aggregations & HAVING", "Subqueries & Common Table Expressions (CTEs)", "Practical SQL Exercises"],
         ["Writing SQL queries on multi-table e-commerce database", "Customer RFM segmentation in SQL"],
         ["Design and query relational schemas", "Extract business insights using SQL"], 16),
        (4, "Python for Data Analytics", "Python fundamentals, variables and data types, lists, tuples, sets, dictionaries, functions, NumPy, Pandas, data exploration.",
         ["Python Fundamentals & Syntax", "Variables, Data Types, Collections", "Functions & Functional Logic", "NumPy Arrays & Mathematical Operations", "Pandas DataFrames & Series", "Exploratory Data Analysis"],
         ["Exploratory data analysis of 50,000+ transaction rows", "Automated data transformation pipeline"],
         ["Clean and reshape raw data with Pandas", "Execute thorough exploratory data analysis"], 18),
        (5, "Data Cleaning & Transformation", "Advanced data wrangling, missing data imputation, anomaly detection, categorical encoding, and feature transformation.",
         ["Missing Value Imputation Strategies", "Outlier Detection & Capping", "Data Type Conversions & Date Parsing", "Feature Encoding & Scaling", "Data Quality Auditing"],
         ["Cleaning real messy multi-source datasets", "Building reusable data sanitization functions"],
         ["Clean and transform messy data reliably", "Ensure statistical integrity of sanitized datasets"], 12),
        (6, "Data Visualization", "Visualization principles, chart selection, dashboard design, business storytelling with data.",
         ["Visualization Principles & Visual Perception", "Chart Selection Matrix", "Color Theory & Aesthetic Layouts", "Dashboard Design Thinking", "Business Storytelling with Data"],
         ["Creating publication-ready charts", "Visual audit of cluttered charts and redesigning"],
         ["Apply professional data visualization standards", "Communicate insights persuasively to leadership"], 10),
        (7, "Power BI", "Data import, Power Query, data transformation, data modeling, relationships, DAX fundamentals, measures, KPIs, interactive dashboards, publishing/exporting reports.",
         ["Data Import & Power Query ETL", "Data Transformation", "Data Modeling & Relationships", "DAX Fundamentals & Calculated Columns", "Key Performance Indicators (KPIs)", "Interactive Dashboards & Publishing"],
         ["End-to-end interactive Power BI dashboard with drill-through", "Custom KPI card suite with DAX"],
         ["Build end-to-end Power BI solutions", "Write core DAX business metrics"], 18),
        (8, "Statistics & Business Intelligence", "Descriptive statistics, mean, median, mode, variance, standard deviation, correlation, business KPIs.",
         ["Descriptive Statistics (Mean, Median, Mode)", "Variance & Standard Deviation", "Correlation vs Causation", "Normal Distribution & Outliers", "Enterprise Business KPIs"],
         ["Statistical hypothesis testing on promotional data", "Outlier detection and resolution"],
         ["Apply statistical thinking to business metrics", "Interpret variance and correlation safely"], 10),
        (9, "Capstone Project", "Student creates a real analytical project using an industry dataset.",
         ["Problem Formulation & Dataset Acquisition", "Data Cleaning & Preparation", "SQL Querying & Python Transformation", "Power BI Interactive Dashboard", "Executive Findings & Actionable Recommendations"],
         ["Complete end-to-end Capstone Project Report and presentation"],
         ["Deliver complete industry-standard analytical portfolio project"], 10)
    ],
    'DM': [
        (1, "Introduction to Digital Marketing", "Digital marketing fundamentals, digital channels, customer journey, marketing funnel.",
         ["Digital Marketing Fundamentals", "Digital Channels Overview", "Customer Journey & Touchpoints", "Marketing Funnel (TOFU, MOFU, BOFU)"],
         ["Digital presence audit of a regional business", "Mapping omnichannel customer touchpoints"],
         ["Understand digital ecosystem dynamics", "Map customer purchase journeys"], 10),
        (2, "SEO", "Search engines, keyword research, on-page SEO, off-page SEO, technical SEO, local SEO, SEO audit.",
         ["Search Engine Crawling & Indexing", "Keyword Research & Search Intent", "On-Page SEO (Meta tags, headings, content)", "Off-Page SEO & Backlinks", "Technical SEO (Sitemaps, robots.txt)", "Local SEO & Google Business Profile", "SEO Audit"],
         ["Keyword research sheet for a regional service business", "Live SEO audit of website"],
         ["Execute full on-page and local SEO audit", "Optimize content for organic search ranking"], 16),
        (3, "Social Media Marketing", "Instagram, Facebook, LinkedIn, YouTube, content strategy, social media calendar, engagement.",
         ["Platform Strategies (Instagram, Facebook, LinkedIn, YouTube)", "Content Strategy & Themes", "Social Media Calendar Creation", "Engagement & Growth Tactics"],
         ["30-day multi-platform social media calendar", "Creation of engaging carousel and video briefs"],
         ["Design cohesive social media calendar", "Drive organic engagement"], 14),
        (4, "Content Marketing", "Content strategy, copywriting, blogging, creative content, AI-assisted content workflows.",
         ["Content Strategy Framework", "Persuasive Copywriting (AIDA, PAS)", "Blogging & Editorial Workflows", "Creative Visual Content", "AI-Assisted Content Workflows"],
         ["Writing landing page copy using AIDA framework", "Publishing an SEO-optimized pillar blog post"],
         ["Draft persuasive marketing copy", "Create multi-format content strategies"], 12),
        (5, "Google Ads / Paid Advertising", "Campaign structure, search campaigns, display advertising, targeting, keywords, ad copy, budgeting, campaign analysis.",
         ["Campaign Structure & Account Architecture", "Search Campaigns & Match Types", "Display Advertising & Remarketing", "Audience Targeting", "Keywords & Negative Keywords", "Ad Copywriting & Extensions", "Budgeting & Campaign Analysis"],
         ["Designing a complete Google Search Ads campaign structure", "Ad copy A/B test variations"],
         ["Set up search ad campaigns with positive ROI", "Optimize quality score and CPC"], 16),
        (6, "Email Marketing", "Email campaigns, lists, segmentation, subject lines, campaign performance.",
         ["Email Marketing Fundamentals", "Email Campaigns & Automation", "List Building & Hygiene", "Audience Segmentation", "Subject Lines & Deliverability", "Campaign Performance Metrics"],
         ["Designing an automated email nurture sequence", "Email template design and copywriting"],
         ["Build automated email marketing funnels", "Improve deliverability and engagement"], 10),
        (7, "Web Analytics", "Traffic, users, sessions, conversion tracking, campaign measurement, KPIs.",
         ["Traffic Sources & Acquisition Channels", "Users & Sessions Analysis", "Conversion Tracking Architecture", "Campaign Measurement & UTMs", "Web Analytics KPIs (GA4)"],
         ["Configuring custom GA4 exploration reports", "Building standard UTM tagging convention sheet"],
         ["Track visitor behavior and conversions accurately", "Analyze web traffic channels"], 12),
        (8, "Performance Marketing", "CPC, CPM, CTR, CPL, CPA, ROAS, campaign optimization.",
         ["Performance Marketing KPIs (CPC, CPM, CTR, CPL, CPA)", "Return on Ad Spend (ROAS) Calculation", "Customer Acquisition Cost (CAC)", "Campaign Optimization Protocols", "Scaling Winning Ad Sets"],
         ["Budget scenario planning and ROAS calculation model", "Meta Ads campaign mockup with creative variations"],
         ["Calculate unit economics and ROAS accurately", "Optimize paid campaigns based on metrics"], 12),
        (9, "AI Tools for Digital Marketing", "AI content workflows, research, creative ideation, marketing automation, responsible AI usage.",
         ["AI Content Workflows & Prompting", "AI in Market Research & Personas", "Creative Ideation & Visual Briefing", "Marketing Automation", "Responsible AI Usage"],
         ["Developing an AI-assisted marketing workflow for daily content generation"],
         ["Incorporate AI tools safely to accelerate output", "Maintain brand voice and factual accuracy"], 8),
        (10, "Capstone Project", "Student creates and documents a real digital marketing campaign/project.",
         ["Brand Selection & Market Diagnosis", "Omnichannel Growth Strategy Formulation", "SEO, Content & Social Media Blueprint", "Paid Advertising Plan & Budgeting", "Performance Tracking, KPIs & Expected ROAS", "Executive Project Report"],
         ["Complete comprehensive Digital Marketing Project Dossier and campaign roadmap"],
         ["Deliver professional digital marketing strategy dossier ready for commercial execution"], 10)
    ],
    'FS': [
        (1, "HTML5, Modern CSS3 & Responsive Design", "Semantic HTML5, CSS3 Grid/Flexbox, Tailwind CSS, Mobile-First UI, Responsive Layouts.",
         ["HTML5 Semantic Tags & Accessibility", "CSS Flexbox & CSS Grid Systems", "Tailwind CSS Utility Framework", "Responsive Breakpoints & Media Queries", "Typography, Icons & Web Assets"],
         ["Building a pixel-perfect responsive SaaS landing page", "Creating reusable responsive navbar and hero components"],
         ["Construct accessible, responsive modern web interfaces", "Master CSS Grid and Tailwind styling"], 12),
        (2, "Modern JavaScript (ES6+) & DOM APIs", "JavaScript fundamentals, ES6 modules, arrow functions, destructuring, promises, async/await, fetch API, DOM manipulation.",
         ["Scope, Closures & Execution Context", "ES6+ Modern Syntax & Destructuring", "Asynchronous JS, Promises & Async/Await", "DOM Traversal & Event Handling", "Fetch API & JSON Data Handling", "Local Storage & Session APIs"],
         ["Building an interactive data-driven task manager in vanilla JS", "API weather dashboard with async/await"],
         ["Write modern, modular and asynchronous JavaScript", "Interact seamlessly with external REST APIs"], 14),
        (3, "Frontend Engineering with React.js", "React architecture, JSX, Virtual DOM, Components, Props, State, Hooks (useState, useEffect, useMemo, useCallback).",
         ["Component Driven Architecture & Virtual DOM", "JSX Syntax & Component Lifecycle", "useState & useEffect Deep Dive", "Custom Hooks & Reusable Logic", "Forms, Controlled Components & Validation", "Component Styling & Tailwind Integration"],
         ["Building a multi-step dynamic registration portal", "E-commerce product catalog with live filtering"],
         ["Build robust, reactive Single Page Applications", "Master core React hook patterns and state flow"], 16),
        (4, "State Management & React Routing", "Client-side routing with React Router v6, Global state management (Context API, Redux Toolkit), Optimistic UI updates.",
         ["React Router DOM Setup & Nested Routes", "Protected Routes & Navigation Guards", "Context API & Global State Architecture", "Redux Toolkit (Slices, Reducers, AsyncThunks)", "Error Boundaries & Suspense"],
         ["Implementing authenticated dashboard route guards", "Building a global shopping cart state with Redux Toolkit"],
         ["Architect scalable frontend state flows", "Implement bulletproof route authentication"], 14),
        (5, "Backend Engineering with Node.js & Express.js", "Node.js runtime, event loop, file system, HTTP module, Express server architecture, routing, middleware.",
         ["Node.js Runtime & Event Loop", "NPM Ecosystem & Package Management", "Express.js Application Architecture", "Routing, Route Parameters & Query Strings", "Custom Middleware & Error Handling Handlers", "CORS, Helmet & Security Middlewares"],
         ["Building an Express.js REST API with modular controllers", "Centralized error handling and logging middleware"],
         ["Construct fast, robust Express.js backend services", "Implement industry-grade middleware pipelines"], 14),
        (6, "RESTful API Architecture & Authentication", "API design principles, CRUD operations, HTTP status codes, JWT token authentication, bcrypt password hashing.",
         ["RESTful API Design Standards & HTTP Verbs", "JWT (JSON Web Token) Architecture", "Bcrypt Password Hashing & Salts", "Authentication & Authorization Middleware", "Input Validation & Sanitization (Zod/Joi)", "Rate Limiting & API Security"],
         ["Building an end-to-end User Auth system with JWT & refresh tokens", "Secure CRUD API for enterprise resources"],
         ["Implement secure, production-ready JWT authentication", "Design standardized RESTful endpoints"], 14),
        (7, "Database Engineering with MongoDB & Mongoose", "NoSQL concepts, MongoDB Atlas, document modeling, Mongoose schemas, relationships, indexing, aggregation pipeline.",
         ["NoSQL vs Relational Databases", "MongoDB Atlas Cloud Setup & Connection", "Mongoose Schemas, Models & Validators", "Document Relationships (Referencing vs Embedding)", "Aggregation Pipeline (match, group, project)", "Indexing Strategies & Query Optimization"],
         ["Designing an enterprise multi-tenant database schema in Mongoose", "Building complex analytical aggregations for sales reports"],
         ["Model scalable NoSQL database architectures", "Execute high-performance Mongoose aggregations"], 16),
        (8, "Full Stack Integration, Testing & Deployment", "Connecting React with Express/MongoDB, environment variables, Postman testing, Dockerization, Render/Vercel deployment.",
         ["Full Stack Integration & Axios API Service", "Environment Variables (.env) Management", "Postman Automated API Test Suites", "Docker Containerization of MERN Apps", "Production Build Optimization & SPA Serving", "Continuous Deployment on Cloud Platforms"],
         ["Deploying live full stack MERN application with cloud DB", "End-to-end integration testing and CORS configuration"],
         ["Deploy production-ready full stack web applications", "Containerize and monitor cloud web services"], 10),
        (9, "Full Stack Capstone Project", "Comprehensive full-stack enterprise web application with authentication, database, UI and cloud deployment.",
         ["System Design & Architecture Specification", "Frontend SPA Implementation with React", "Backend REST API with Express & MongoDB", "Authentication & Role-Based Access Control", "Production Deployment & Documentation"],
         ["Complete Full Stack Web Application source code and live deployed URL"],
         ["Deliver end-to-end production web application portfolio project"], 10)
    ],
    'AI': [
        (1, "Advanced Python Programming for AI", "Python syntax, OOPs, decorators, generators, file I/O, regex, virtual environments, package management.",
         ["Pythonic Code & Clean Coding Standards", "Object-Oriented Programming (Inheritance, Polymorphism)", "Functional Programming, Lambda, Map, Filter", "Decorators, Generators & Context Managers", "Exception Handling & Modular Code Architecture"],
         ["Building a modular Python package for automated data processing", "OOP-based pipeline class architecture"],
         ["Write clean, maintainable, object-oriented Python code", "Build custom utility modules and pipelines"], 12),
        (2, "Scientific Computing with NumPy & Pandas", "Vectorized arrays, multi-dimensional slicing, broadcasting, Pandas DataFrames, time series, merging, grouping.",
         ["NumPy N-Dimensional Arrays & Slicing", "Vectorized Operations & Array Broadcasting", "Pandas DataFrames, Series & Indexing", "Data Merging, Joining & Concatenation", "GroupBy Aggregations & Pivot Tables", "Time Series Handling & Date Resampling"],
         ["High-speed vectorized matrix computations in NumPy", "Wrangling 100,000+ row financial transactions in Pandas"],
         ["Perform high-speed vectorized data operations", "Manipulate complex multi-index DataFrames"], 16),
        (3, "Exploratory Data Analysis & Visualization", "Data visualization with Matplotlib and Seaborn, statistical plots, correlation heatmaps, distribution analysis.",
         ["Matplotlib Core Architecture & Subplots", "Seaborn Statistical Visualizations", "Distribution Plots, Histograms & KDEs", "Categorical Plots (Box, Violin, Bar)", "Correlation Matrices & Heatmaps", "Storytelling & Visual Insights Extraction"],
         ["Complete exploratory data analysis dossier on health dataset", "Automated distribution anomaly detection charts"],
         ["Uncover hidden data distributions and correlations", "Produce publication-quality statistical charts"], 12),
        (4, "Statistical Foundations & Feature Engineering", "Probability distributions, hypothesis testing, missing value handling, scaling, one-hot encoding, PCA.",
         ["Probability Distributions (Normal, Binomial, Poisson)", "Hypothesis Testing (t-test, Chi-Square, ANOVA)", "Missing Value Imputation & Outlier Truncation", "Feature Scaling (StandardScaler, MinMaxScaler)", "Categorical Encoding (One-Hot, Target, Label)", "Principal Component Analysis (PCA)"],
         ["Building an automated feature transformation pipeline", "Dimensionality reduction of high-dimensional dataset"],
         ["Apply rigorous statistical tests to hypotheses", "Engineer clean, leak-free feature pipelines"], 14),
        (5, "Supervised Learning: Regression & Classification", "Linear/Logistic Regression, Decision Trees, Random Forests, Gradient Boosting (XGBoost, LightGBM).",
         ["Linear Regression, Cost Functions & Gradient Descent", "Logistic Regression & Odds Ratio", "Decision Trees, Gini Impurity & Entropy", "Ensemble Methods: Random Forests & Bagging", "Gradient Boosting: XGBoost & LightGBM", "Hyperparameter Tuning with GridSearchCV"],
         ["Predicting housing market prices using XGBoost regression", "Customer churn classification with Random Forest"],
         ["Train and optimize high-accuracy regression models", "Implement robust classification architectures"], 18),
        (6, "Unsupervised Learning & Clustering", "K-Means clustering, hierarchical clustering, DBSCAN, silhouette analysis, customer segmentation.",
         ["K-Means Algorithm & Elbow Method", "Hierarchical Clustering & Dendrograms", "DBSCAN Density-Based Clustering", "Silhouette Analysis & Cluster Evaluation", "Anomaly Detection via Isolation Forests"],
         ["Unsupervised customer behavioral segmentation model", "Fraudulent transaction anomaly detection"],
         ["Segment unstructured data into meaningful clusters", "Identify outliers and anomalies unsupervised"], 12),
        (7, "Deep Learning & Neural Networks Fundamentals", "Perceptrons, multi-layer neural networks, activation functions, backpropagation, TensorFlow/Keras.",
         ["Biological vs Artificial Neurons", "Activation Functions (ReLU, Sigmoid, Softmax)", "Backpropagation & Loss Optimization (Adam, SGD)", "Building Neural Networks with TensorFlow / Keras", "Overfitting Prevention (Dropout, EarlyStopping)", "Introduction to Computer Vision (CNN) & NLP"],
         ["Building a multi-layer deep neural network for image classification", "Implementing custom loss and callback functions"],
         ["Design and train multi-layer neural networks in Keras", "Prevent neural network overfitting effectively"], 16),
        (8, "Model Evaluation, MLOps & API Deployment", "Confusion matrix, ROC-AUC, cross-validation, model serialization (joblib/pickle), FastAPI model serving.",
         ["Evaluation Metrics (Precision, Recall, F1, ROC-AUC)", "K-Fold Cross-Validation & Stratification", "Model Serialization & Versioning (Joblib/Pickle)", "FastAPI Microservice for Live Model Inference", "Dockerizing AI Services & Cloud Deployment", "Responsible AI, Bias & Explainability (SHAP)"],
         ["Deploying a trained machine learning model as a REST API", "Building interactive model inference UI with Streamlit/React"],
         ["Evaluate models rigorously using standard metrics", "Deploy trained models as production REST microservices"], 10),
        (9, "Applied AI Capstone Project", "End-to-end machine learning / AI project with dataset preparation, model training, evaluation, and REST API deployment.",
         ["Problem Definition & Dataset Ingestion", "Feature Engineering & Preprocessing Pipeline", "Model Experimentation & Hyperparameter Tuning", "Evaluation, Validation & Explainability Analysis", "Deployment as Interactive Prediction Web App"],
         ["Complete Applied AI Project Report, trained model artifacts, and source code"],
         ["Deliver end-to-end production AI portfolio project"], 10)
    ],
    'CS': [
        (1, "Fundamentals of Cyber Security & Threat Landscapes", "CIA Triad, attack vectors, threat actors, malware types, social engineering, security governance.",
         ["Confidentiality, Integrity & Availability (CIA Triad)", "Threat Actor Types & Attack Vectors", "Malware Analysis (Ransomware, Trojans, Rootkits)", "Social Engineering & Phishing Tactics", "Security Frameworks (NIST, ISO/IEC 27001)"],
         ["Threat modeling analysis of enterprise banking system", "Simulating phishing attack identification and remediation"],
         ["Analyze enterprise attack vectors and threat surfaces", "Apply NIST cybersecurity framework principles"], 12),
        (2, "Network Security & Packet Analysis", "OSI & TCP/IP security, subnetting, port scanning, Wireshark packet capture, protocol vulnerabilities.",
         ["TCP/IP & OSI Model Security Analysis", "DNS, DHCP, ARP, HTTP/HTTPS Vulnerabilities", "Packet Sniffing & Deep Inspection with Wireshark", "Port Scanning & Network Mapping with Nmap", "Man-in-the-Middle (MITM) & ARP Spoofing Defense"],
         ["Capturing and analyzing malicious network traffic pcaps in Wireshark", "Complete Nmap reconnaissance of target subnet"],
         ["Inspect network traffic for anomalies with Wireshark", "Detect and mitigate ARP spoofing and MITM attacks"], 16),
        (3, "Linux Security & System Administration", "Linux file permissions, sudoers, SSH hardening, iptables/UFW firewalls, log auditing.",
         ["Linux File System & Permission Architecture", "User Management, Groups & Sudo Hardening", "SSH Key Authentication & Configuration Hardening", "Linux Firewalls (UFW, IPTables)", "System Logging & Auditd Log Analysis", "Bash Scripting for Security Automation"],
         ["Hardening a bare Linux server according to CIS benchmarks", "Automated Bash script for failed login auditing"],
         ["Harden Linux server configurations securely", "Automate security log auditing using shell scripts"], 14),
        (4, "Information Gathering & Vulnerability Scanning", "OSINT techniques, reconnaissance, passive/active scanning, Nessus, OpenVAS, CVE databases.",
         ["Open Source Intelligence (OSINT) Methodologies", "Passive vs Active Reconnaissance Techniques", "Vulnerability Scanning with Nessus & OpenVAS", "Common Vulnerabilities and Exposures (CVE/NVD)", "CVSS Scoring & Risk Prioritization"],
         ["Conducting an authorized vulnerability scan using OpenVAS", "Compiling an executive vulnerability remediation report"],
         ["Execute structured vulnerability assessments", "Calculate CVSS risk scores and prioritize patches"], 14),
        (5, "Web Application Security & OWASP Top 10", "SQL Injection, Cross-Site Scripting (XSS), CSRF, IDOR, Broken Auth, Burp Suite intercepting proxy.",
         ["OWASP Top 10 Vulnerability Deep Dive", "SQL Injection (SQLi) Detection & Parameterization", "Cross-Site Scripting (XSS: Stored, Reflected, DOM)", "Broken Authentication & Session Hijacking", "Insecure Direct Object References (IDOR)", "Burp Suite Intercepting Proxy & Repeater Workflows"],
         ["Exploiting and remediating SQLi and XSS in controlled lab environment", "Intercepting and manipulating HTTP requests in Burp Suite"],
         ["Identify and patch OWASP Top 10 web vulnerabilities", "Master web penetration testing with Burp Suite"], 18),
        (6, "Cryptography, PKI & Secure Communications", "Symmetric/Asymmetric encryption, AES, RSA, ECC, hashing (SHA-256), digital certificates, TLS 1.3.",
         ["Symmetric Encryption (AES, DES) & Block Ciphers", "Asymmetric Cryptography (RSA, ECC, Diffie-Hellman)", "Cryptographic Hash Functions (SHA-256, SHA-3)", "Public Key Infrastructure (PKI) & X.509 Certificates", "TLS 1.3 Protocol & Handshake Security", "Zero Knowledge Proofs Basics"],
         ["Implementing AES-256 file encryption in Python", "Setting up custom SSL/TLS Certificate Authority (CA)"],
         ["Implement cryptographic algorithms and secure handshakes", "Configure PKI and digital certificates properly"], 14),
        (7, "Network Defense, Firewalls & IDS/IPS", "Next-Gen Firewalls, Snort IDS/IPS, SIEM platforms, threat hunting, honeypots.",
         ["Stateful vs Next-Gen Firewall Architectures", "Intrusion Detection/Prevention Systems (Snort, Suricata)", "Writing Custom Snort Rules for Attack Signatures", "Security Information & Event Management (SIEM / Splunk / Wazuh)", "Honeypot Deployment & Threat Intelligence"],
         ["Deploying Snort IDS and writing rules to alert on port scans", "Setting up centralized log monitoring in Wazuh SIEM"],
         ["Configure and tune Network IDS/IPS systems", "Investigate security alerts in enterprise SIEM dashboards"], 12),
        (8, "Incident Response & Digital Forensics", "Incident handling lifecycle, evidence acquisition, memory forensics, Autopsy, Volatility.",
         ["NIST Incident Response Lifecycle (PICERL)", "Digital Evidence Acquisition & Chain of Custody", "Disk Image Forensics with Autopsy", "RAM / Memory Forensics with Volatility", "Log Correlation & Timeline Reconstruction"],
         ["Analyzing a compromised disk image to reconstruct intrusion timeline", "Extracting memory artifacts and injected DLLs in Volatility"],
         ["Handle security incidents following NIST protocols", "Extract digital forensic evidence from memory and disk"], 10),
        (9, "Cyber Security Capstone Project", "Comprehensive Vulnerability Assessment and Penetration Testing (VAPT) audit of enterprise infrastructure.",
         ["Scope Definition & Rules of Engagement", "Reconnaissance & Automated Scanning", "Manual Exploitation Verification", "Risk Assessment & CVSS Mapping", "Executive & Technical Remediation Deliverables"],
         ["Complete Enterprise VAPT Audit Report and remediation guidelines"],
         ["Deliver professional penetration testing audit dossier"], 10)
    ],
    'CC': [
        (1, "Cloud Computing Foundations & AWS Architecture", "Cloud paradigms, virtualization, AWS Global Infrastructure, IAM security, cost management.",
         ["Cloud Service Models (IaaS, PaaS, SaaS)", "AWS Global Infrastructure (Regions, AZs, Edge Locations)", "Identity & Access Management (IAM Policies, Roles, MFA)", "AWS Organizations & Cost Management", "Cloud Architecture Best Practices"],
         ["Setting up secure AWS IAM root and least-privilege role policies", "Configuring billing alerts and budgets in AWS"],
         ["Understand enterprise cloud computing architectures", "Enforce strict IAM security policies in AWS"], 12),
        (2, "Core Cloud Compute & Virtual Private Cloud (VPC)", "Amazon EC2, AMIs, Instance types, VPC networking, subnets, route tables, internet gateways.",
         ["Amazon EC2 Instance Types & Lifecycle", "Custom AMIs & User Data Automation Scripts", "VPC Architecture, Public & Private Subnets", "Internet Gateways, NAT Gateways & Route Tables", "Security Groups vs Network ACLs"],
         ["Designing a high-availability multi-AZ VPC architecture", "Provisioning auto-configured web servers via EC2 User Data"],
         ["Design custom isolated VPC network topologies", "Deploy and secure EC2 compute instances"], 16),
        (3, "Cloud Storage, Databases & Content Delivery", "Amazon S3, EBS, EFS, RDS (PostgreSQL/MySQL), DynamoDB, CloudFront CDN, Route 53.",
         ["Amazon S3 Storage Classes, Bucket Policies & Lifecycle Rules", "Elastic Block Store (EBS) & Elastic File System (EFS)", "Relational Database Service (RDS) Multi-AZ & Read Replicas", "DynamoDB NoSQL Architecture", "Amazon CloudFront Global CDN & Route 53 DNS"],
         ["Hosting a secure static website on S3 with CloudFront CDN and SSL", "Deploying a highly available PostgreSQL database in RDS"],
         ["Configure cloud storage with proper lifecycle policies", "Deploy resilient multi-AZ managed cloud databases"], 16),
        (4, "Linux Administration & Git Workflows for DevOps", "Linux CLI, shell automation, SSH, cron jobs, Git branching strategies, GitHub workflows.",
         ["Linux Shell Scripting & Automation", "Process Management, Systemd Services & Cron Jobs", "SSH Key Management & Remote Server Administration", "Git Branching Models (Gitflow, Trunk-Based)", "Git Hooks & Merge Conflict Resolution"],
         ["Writing automated backup scripts and cron jobs on Linux", "Setting up a multi-branch Git collaborative workflow"],
         ["Master Linux sysadmin tasks for DevOps engineers", "Implement structured Git branching strategies"], 14),
        (5, "Containerization with Docker", "Container architecture, Dockerfile, image layering, multi-stage builds, Docker Compose, Docker Hub.",
         ["Virtual Machines vs Containers", "Docker Engine Architecture & Docker CLI", "Writing Production Dockerfiles & Multi-Stage Builds", "Docker Image Layer Optimization & Caching", "Docker Compose for Multi-Container Apps", "Docker Volume Persistence & Networking"],
         ["Containerizing a React + Node + Mongo full stack app with Docker Compose", "Building minimal footprint multi-stage Docker images"],
         ["Containerize complex multi-tier applications with Docker", "Optimize Docker image sizes for production deployment"], 16),
        (6, "CI/CD Automation with GitHub Actions", "Continuous Integration, Continuous Delivery, pipelines, automated testing, secret management.",
         ["CI/CD Principles & Automation Benefits", "GitHub Actions Workflow Syntax (YAML)", "Automated Linting, Testing & Security Scanning", "Building & Pushing Docker Images to Registry", "Automated SSH & Cloud Deployment Steps", "Secrets Management in CI/CD"],
         ["Building an automated CI/CD pipeline that tests, builds and deploys a web app on push", "Integrating SonarQube code quality scan"],
         ["Automate software delivery pipelines from commit to cloud", "Manage deployment secrets securely in CI/CD workflows"], 14),
        (7, "Container Orchestration with Kubernetes", "Kubernetes architecture, Pods, Deployments, Services, Ingress, ConfigMaps, Secrets, Helm.",
         ["Kubernetes Architecture (Control Plane vs Worker Nodes)", "Pods, ReplicaSets & Declarative Deployments", "ClusterIP, NodePort & LoadBalancer Services", "Ingress Controllers & SSL Termination", "ConfigMaps, Secrets & Persistent Volumes", "Helm Package Manager Basics"],
         ["Deploying a resilient, auto-scaling web application on Kubernetes cluster", "Configuring Ingress routing with automated TLS certificates"],
         ["Orchestrate containers with Kubernetes deployments and services", "Manage application configuration and secrets in k8s"], 12),
        (8, "Infrastructure as Code (IaC) & Cloud Monitoring", "Terraform basics, state management, AWS CloudWatch, Prometheus, Grafana, alerts.",
         ["Infrastructure as Code (IaC) Principles", "Terraform Syntax (HCL), Providers & Resources", "Terraform State Management & Modules", "AWS CloudWatch Metrics, Alarms & Logs", "Prometheus & Grafana Observability Dashboards"],
         ["Automating VPC and EC2 provisioning using Terraform HCL", "Building a live Grafana dashboard for server CPU/RAM metrics"],
         ["Provision cloud infrastructure declaratively with Terraform", "Monitor infrastructure health with CloudWatch and Grafana"], 10),
        (9, "Cloud & DevOps Capstone Project", "End-to-end automated multi-tier cloud infrastructure with Docker, CI/CD, Terraform and AWS hosting.",
         ["Architecture Blueprint & Capacity Planning", "Terraform IaC Infrastructure Provisioning", "Containerization & Multi-Container Compose", "GitHub Actions CI/CD Pipeline Automation", "Monitoring, Alerting & Executive Dossier"],
         ["Complete Cloud & DevOps Project Architecture Dossier and IaC repository"],
         ["Deliver production-grade cloud DevOps infrastructure portfolio project"], 10)
    ],
    'JV': [
        (1, "Core Java Programming & OOPs Mastery", "Java architecture, JVM, memory model, classes, inheritance, polymorphism, encapsulation, interfaces.",
         ["JVM Architecture, Bytecode & ClassLoaders", "Primitive Types, Operators & Control Flow", "Object-Oriented Programming (Classes, Objects, Inheritance)", "Polymorphism, Abstraction & Interface Design", "Encapsulation & Package Architecture", "Exception Handling (Checked vs Unchecked)"],
         ["Building a comprehensive bank account management system in Core Java", "Custom exception hierarchy and logging"],
         ["Master Java OOPs principles and inheritance design", "Implement robust exception handling strategies"], 14),
        (2, "Java Collections Framework & Streams API", "List, Set, Map, Queue, Generics, Lambdas, Functional Interfaces, Streams API, Optional.",
         ["Generics & Type Safety in Java", "List Implementations (ArrayList, LinkedList)", "Set Implementations (HashSet, TreeSet)", "Map Implementations (HashMap, TreeMap, ConcurrentHashMap)", "Lambda Expressions & Functional Interfaces", "Java 8+ Streams API (Filter, Map, Reduce, Collect)"],
         ["Building high-performance data processing pipelines with Java Streams", "Implementing custom comparator and sorting logic"],
         ["Utilize the Java Collections framework with maximum performance", "Write clean, declarative functional code with Java Streams"], 16),
        (3, "Relational Database Design & JDBC Connectivity", "RDBMS principles, complex SQL, Transactions, ACID properties, JDBC API, PreparedStatement.",
         ["RDBMS Schema Design & Normalization (3NF)", "Complex SQL (JOINs, Subqueries, Aggregations)", "ACID Properties & Database Transactions", "Java Database Connectivity (JDBC) Architecture", "PreparedStatement & SQL Injection Prevention", "Connection Pooling with HikariCP"],
         ["Building a complete JDBC DAO layer with connection pooling", "Transaction management with commit/rollback logic"],
         ["Connect Java applications to relational databases securely", "Manage ACID database transactions in Java code"], 14),
        (4, "Spring Boot Framework Fundamentals", "Inversion of Control (IoC), Dependency Injection (DI), Spring Boot starters, application.properties, REST controllers.",
         ["Spring Framework Core & Inversion of Control (IoC)", "Dependency Injection (@Autowired, Constructor Injection)", "Spring Boot Starters & Auto-Configuration", "Building RESTful Web Services with @RestController", "Request Mapping, PathVariables & RequestBodies", "Application Properties & Profiles (Dev/Prod)"],
         ["Building a Spring Boot REST API for product catalog management", "Configuring custom profiles and environment properties"],
         ["Build production REST APIs with Spring Boot", "Master Spring Dependency Injection and IoC container"], 16),
        (5, "Spring Data JPA & Hibernate ORM", "ORM concepts, JPA annotations, Entity mappings (@OneToMany, @ManyToMany), JpaRepository, custom queries.",
         ["Object-Relational Mapping (ORM) Principles", "JPA Entity Annotations (@Entity, @Table, @Id)", "Relationship Mappings (@OneToMany, @ManyToOne, @ManyToMany)", "Spring Data JpaRepository & Derived Query Methods", "JPQL & Native SQL Queries with @Query", "Pagination, Sorting & Auditing Support"],
         ["Designing an enterprise e-commerce entity relationship model in JPA", "Writing complex JPQL queries with pagination and sorting"],
         ["Map relational databases to Java entities effortlessly", "Write expressive database queries using Spring Data JPA"], 16),
        (6, "Enterprise Security with Spring Security & JWT", "Authentication vs Authorization, Spring Security filter chain, UserDetailsService, JWT token generation & validation.",
         ["Spring Security Architecture & Filter Chain", "UserDetailsService & PasswordEncoder (BCrypt)", "Role-Based Access Control (@PreAuthorize)", "JWT Token Generation, Signing & Validation", "Stateless Authentication Filter Implementation", "CORS & CSRF Configuration in Spring Security"],
         ["Implementing a complete Spring Boot JWT authentication microservice", "Role-based endpoint access control (Admin, User, Manager)"],
         ["Secure Spring Boot APIs with industry-standard JWT tokens", "Implement robust role-based access control"], 14),
        (7, "Frontend Integration with React.js & TypeScript", "Connecting React UI with Spring Boot REST API, Axios, TypeScript models, error handling.",
         ["Frontend SPA Architecture with React & TypeScript", "Axios HTTP Client & Interceptor for JWT Bearer Tokens", "TypeScript Interfaces Matching Java DTOs", "Form Validation, Notification Banners & Loading States", "Full Stack CRUD Integration"],
         ["Building a responsive React TypeScript administration dashboard connecting to Spring Boot backend", "JWT token auto-refresh flow"],
         ["Connect modern React TypeScript frontends to Java backends", "Handle full-stack errors and tokens smoothly"], 12),
        (8, "Unit Testing, Microservices & Docker Deployment", "JUnit 5, Mockito, microservices overview, Docker containerization, Maven build lifecycle.",
         ["Unit Testing with JUnit 5 & Mockito", "Integration Testing with @SpringBootTest", "Microservices Architecture Principles & Service Discovery", "Maven Build Lifecycle & Multi-Module Projects", "Dockerizing Spring Boot Applications", "Cloud Deployment on Render / AWS"],
         ["Writing 90%+ code coverage unit test suites with JUnit 5 and Mockito", "Dockerizing a full stack Spring Boot + React application"],
         ["Write comprehensive unit and integration test suites", "Containerize and deploy enterprise Java applications"], 10),
        (9, "Java Full Stack Capstone Project", "Complete enterprise-grade full-stack web application built with Spring Boot, JPA, MySQL, React and JWT security.",
         ["Enterprise System Requirement Specification", "Backend REST API with Spring Boot & Hibernate", "Database Schema & Migration Scripts", "Frontend User Interface with React & TypeScript", "Security Hardening, Unit Tests & Deployment"],
         ["Complete Java Full Stack Enterprise Project Report, source code, and live demo"],
         ["Deliver production enterprise Java full-stack portfolio project"], 10)
    ],
    'BI': [
        (1, "Introduction to Computational Biology & Biological Databases", "Central dogma of molecular biology, genomics, proteomics, NCBI, UniProt, PDB, Ensembl.",
         ["Central Dogma & Molecular Biology Fundamentals", "Genomics, Transcriptomics & Proteomics Concepts", "NCBI Entrez System & GenBank Databases", "UniProt Protein Knowledgebase", "Protein Data Bank (PDB) & 3D Structures", "Ensembl Genome Browser"],
         ["Retrieving and analyzing gene/protein records from NCBI and UniProt", "Performing comprehensive biological database queries"],
         ["Navigate and query world biological databases effectively", "Understand molecular data structures and accession formats"], 12),
        (2, "Python Programming for Life Sciences", "Python basics, BioPython library, sequence parsing (FASTA, GenBank), GC content, translation.",
         ["Python Fundamentals & Scientific Data Structures", "BioPython Library Overview & Installation", "Parsing FASTA and GenBank File Formats with SeqIO", "GC Content Calculation, Transcription & Translation", "Motif Searching & Regular Expressions in DNA/RNA", "Handling Large Sequence Files Efficiently"],
         ["Building an automated DNA sequence quality analysis script", "Translating open reading frames (ORFs) from raw FASTA files"],
         ["Parse and manipulate biological sequences in Python", "Calculate statistical sequence metrics automatically"], 14),
        (3, "Sequence Alignment Algorithms & BLAST", "Pairwise alignment, Dot plot, Needleman-Wunsch global, Smith-Waterman local, BLAST querying.",
         ["Pairwise Sequence Alignment Principles", "Dot Matrix Methods for Sequence Comparison", "Needleman-Wunsch Global Alignment Algorithm", "Smith-Waterman Local Alignment Algorithm", "Substitution Matrices (PAM, BLOSUM62)", "BLAST (Basic Local Alignment Search Tool) & E-values"],
         ["Implementing Needleman-Wunsch dynamic programming in Python", "Running remote and local BLAST searches for homologous genes"],
         ["Execute global and local sequence alignment algorithms", "Interpret BLAST statistical E-values and alignments"], 16),
        (4, "Multiple Sequence Alignment & Phylogenetics", "Multiple sequence alignment (Clustal Omega, MUSCLE), phylogenetic trees, evolutionary distance.",
         ["Multiple Sequence Alignment (MSA) Theory", "Progressive & Iterative MSA Tools (Clustal Omega, MUSCLE)", "Phylogenetic Tree Construction (Neighbor-Joining, UPGMA)", "Bootstrapping & Tree Reliability", "Bio.Phylo Module for Tree Visualization", "Evolutionary Conservation Analysis"],
         ["Constructing a phylogenetic tree of evolutionary conserved proteins", "Identifying catalytic residue conservation across species"],
         ["Build and visualize evolutionary phylogenetic trees", "Detect conserved functional domains across species"], 14),
        (5, "Structural Bioinformatics & Molecular Modeling", "Protein secondary/tertiary structure, Ramachandran plot, PyMOL visualization, PDB parsing.",
         ["Protein Structure Hierarchy (Primary, Secondary, Tertiary, Quaternary)", "PDB File Format Anatomy & Atom Coordinates", "Ramachandran Plot Analysis for Backbone Conformation", "3D Molecular Visualization with PyMOL / Bio.PDB", "Ligand-Protein Binding Site Identification", "Homology Modeling Principles"],
         ["Parsing PDB files to calculate C-alpha distance matrices in Python", "Generating 3D molecular renders of enzyme active sites"],
         ["Analyze and render 3D macromolecular structures", "Evaluate protein conformational quality and active sites"], 16),
        (6, "Genomic Data Analysis & Next-Generation Sequencing", "NGS technologies, FASTQ quality control, SAM/BAM formats, variant calling, mutation analysis.",
         ["Next-Generation Sequencing (NGS) Technologies (Illumina, Nanopore)", "FASTQ Format & FastQC Quality Control", "Read Alignment & SAM/BAM File Processing", "Variant Calling & VCF (Variant Call Format)", "Single Nucleotide Polymorphisms (SNPs) & InDels", "Functional Annotation of Genomic Variants"],
         ["Executing a quality control pipeline on raw FASTQ sequencing reads", "Parsing VCF files to identify disease-associated mutations"],
         ["Process and quality-filter next-generation sequencing data", "Identify and annotate genetic variants and mutations"], 16),
        (7, "Gene Expression Analytics & Biostatistics", "Microarray & RNA-Seq data analysis, differential expression, volcano plots, PCA of expression profiles.",
         ["Gene Expression Profiling & RNA-Seq Workflow", "Normalization Methods (RPKM, FPKM, TPM)", "Differential Expression Analysis (p-value, log2 fold-change)", "Statistical Volcano Plots & Heatmaps", "Principal Component Analysis (PCA) of Samples", "Gene Ontology (GO) & Pathway Enrichment (KEGG)"],
         ["Analyzing a cancer vs control RNA-Seq dataset for differentially expressed genes", "Generating interactive heatmaps and volcano plots"],
         ["Perform differential gene expression analysis accurately", "Interpret functional pathway enrichment results"], 12),
        (8, "Machine Learning in Bioinformatics", "Classifying biological sequences, predicting protein secondary structure, biomarker discovery.",
         ["Machine Learning Applications in Molecular Biology", "Feature Extraction from Biological Sequences (k-mers, amino acid properties)", "Supervised Classification of Disease Biomarkers", "Predicting Subcellular Localization & Structure", "Model Evaluation & Biological Cross-Validation"],
         ["Training a Random Forest classifier to predict antimicrobial peptides", "Feature importance evaluation for cancer biomarkers"],
         ["Apply machine learning algorithms to biological datasets", "Extract meaningful features from genetic and protein sequences"], 10),
        (9, "Bioinformatics Capstone Project", "Comprehensive computational biology / bioinformatics research pipeline with sequence analysis, modeling, and findings.",
         ["Biological Question Formulation & Dataset Selection", "Automated BioPython Pipeline & Alignment", "Structural or Gene Expression Analysis", "Statistical Validation & Interpretation", "Formal Research Dossier & Visualizations"],
         ["Complete Bioinformatics Project Report, sequence analysis scripts, and publication-ready figures"],
         ["Deliver professional computational biology portfolio research project"], 10)
    ],
    'AD': [
        (1, "Mobile App Ecosystem & Kotlin Fundamentals", "Android OS architecture, Kotlin syntax, variables, null safety, OOPs, collections, lambda expressions.",
         ["Android OS Architecture & Ecosystem", "Kotlin Fundamentals & Null Safety (? / !!)", "Classes, Data Classes, Objects & Inheritance in Kotlin", "Kotlin Collections & Higher-Order Functions", "Extension Functions & Scope Functions (let, apply, also)", "Android Studio Setup & Gradle Configuration"],
         ["Building interactive Kotlin console applications demonstrating OOPs and collections", "Configuring Gradle dependencies for modern Android"],
         ["Master Kotlin programming and null safety paradigms", "Configure modern Android Studio development environments"], 14),
        (2, "Android Project Architecture & Lifecycle", "Activity lifecycle, Fragment lifecycle, AndroidManifest.xml, intent communication, resources.",
         ["Android Application Architecture Overview", "Activity Lifecycle & State Management", "Explicit & Implicit Intents with Parcelable Data", "Android Resources (Strings, Drawables, Themes, Dimens)", "Runtime Permissions Handling", "Configuration Changes & ViewModel Basics"],
         ["Building a multi-screen application with intent data passing", "Handling orientation and runtime permission flows properly"],
         ["Manage Activity lifecycles without data loss or memory leaks", "Implement secure Android runtime permission requests"], 14),
        (3, "Declarative UI with Jetpack Compose & Material 3", "Composable functions, state, modifiers, layouts (Column, Row, Box), Material Design 3 components.",
         ["Imperative Views vs Declarative Jetpack Compose", "@Composable Functions & Compose Compiler", "State in Compose (remember, mutableStateOf)", "Layout Components (Column, Row, Box, Scaffold)", "Material Design 3 Theming, Color Schemes & Typography", "Custom Modifiers, Animations & Recomposition"],
         ["Building a modern, animated Material 3 user profile and onboarding flow", "Creating reusable custom Composable UI component libraries"],
         ["Construct beautiful declarative mobile UIs with Jetpack Compose", "Master state management and recomposition in Compose"], 16),
        (4, "Advanced Compose Layouts & Navigation", "LazyColumn, LazyRow, Cards, TopAppBar, BottomNavigation, Navigation Compose with typed arguments.",
         ["Efficient Lists with LazyColumn & LazyRow", "Custom Cards, Surface, Badges & FloatingActionButtons", "Navigation Component in Jetpack Compose", "Passing Safe Arguments Between Screens", "Bottom Navigation Bar & Drawer Navigation", "Deep Linking Support in Mobile Apps"],
         ["Building an interactive e-commerce product catalog with animated bottom navigation", "Implementing type-safe nested navigation graph"],
         ["Build high-performance scrollable lists in Jetpack Compose", "Implement clean multi-screen navigation architectures"], 14),
        (5, "Local Data Persistence with Room SQLite Database", "Room architecture, Entities, DAOs, RoomDatabase, Flow/LiveData observation, DataStore preferences.",
         ["Local Data Persistence Strategies in Android", "Room Database Architecture (@Entity, @Dao, @Database)", "Type Converters & Database Migrations", "Reactive Queries with Kotlin Coroutine Flow", "DataStore Preferences for App Settings", "Repository Pattern for Data Abstraction"],
         ["Building a complete offline-capable personal expense tracker with Room DB and Flow", "Storing encrypted user preferences in DataStore"],
         ["Persist structured data locally with Room SQLite database", "Build reactive offline-first mobile data layers"], 16),
        (6, "Networking, REST APIs & Coroutines with Retrofit", "Kotlin Coroutines, Dispatchers, Retrofit HTTP client, Moshi/Gson JSON parsing, Coil image loading.",
         ["Kotlin Coroutines (launch, async, Dispatchers.IO/Main)", "Exception Handling in Coroutines & Structured Concurrency", "Retrofit 2 HTTP Client Configuration", "JSON Parsing with Moshi / Kotlinx Serialization", "Handling HTTP Errors & Network Status Monitoring", "Asynchronous Image Loading with Coil"],
         ["Connecting the Android app to a live REST API with Retrofit and Coroutines", "Building dynamic news feed with pagination and image caching"],
         ["Consume RESTful APIs asynchronously using Retrofit and Coroutines", "Handle network connectivity states and errors gracefully"], 16),
        (7, "Firebase Backend Integration & Push Notifications", "Firebase Auth, Cloud Firestore, Cloud Storage, Firebase Cloud Messaging (FCM).",
         ["Firebase Ecosystem for Android Apps", "Firebase Authentication (Email/Password, Google Sign-In)", "Cloud Firestore Real-Time NoSQL Database", "Uploading & Caching Images with Cloud Storage", "Firebase Cloud Messaging (FCM) Push Notifications", "Crashlytics for Live Crash Reporting"],
         ["Building an end-to-end real-time chat / notice board application with Firestore", "Configuring background push notification handlers"],
         ["Integrate cloud authentication and real-time databases", "Handle push notifications and remote crash analytics"], 12),
        (8, "Architecture (MVVM), Testing & Play Store Release", "MVVM architecture, Dependency Injection (Hilt/Koin), Unit testing, ProGuard, APK/AAB generation.",
         ["Model-View-ViewModel (MVVM) Clean Architecture", "Dependency Injection with Hilt / Koin", "Unit Testing ViewModels with MockK and JUnit", "Code Obfuscation with ProGuard / R8", "Generating Signed App Bundles (AAB)", "Google Play Console Submission Checklist"],
         ["Refactoring application into modular MVVM with Hilt dependency injection", "Building and signing a production release Android App Bundle"],
         ["Architect scalable mobile codebases using MVVM and Hilt", "Prepare and sign Android apps for Google Play Store publication"], 10),
        (9, "Android Capstone Project", "Full-featured production Android application with Jetpack Compose, Room DB, Retrofit API, MVVM, and Firebase.",
         ["App Concept & User Flow Wireframing", "Declarative UI Implementation in Jetpack Compose", "Offline-First Room DB & Retrofit Cloud Sync", "MVVM Architecture & State Management", "Production Signed AAB Build & Technical Dossier"],
         ["Complete Android Mobile App Project Report, source code repository, and installable APK"],
         ["Deliver production native Android mobile application portfolio project"], 10)
    ]
}

def ensure_all_courses(cursor, conn):
    print("Ensuring all 9 industry courses, modules and batches are populated...")

    # 1. Update / Insert Centre Settings default verification base URL
    cursor.execute("""
    UPDATE centre_settings 
    SET verification_base_url = 'https://technoglobe-certificates.onrender.com'
    WHERE id = 1 AND (verification_base_url LIKE '%192.168.%' OR verification_base_url LIKE '%localhost%')
    """)

    # 2. Insert or update courses
    course_id_map = {}
    for code, name, title, desc, weeks, hours, mode in COURSES_CATALOG:
        cursor.execute("SELECT id FROM courses WHERE code = ?", (code,))
        row = cursor.fetchone()
        if row:
            c_id = row[0]
            cursor.execute("""
            UPDATE courses SET name = ?, title = ?, description = ?, duration_weeks = ?, total_hours = ?, default_mode = ?
            WHERE id = ?
            """, (name, title, desc, weeks, hours, mode, c_id))
        else:
            cursor.execute("""
            INSERT INTO courses (code, name, title, description, duration_weeks, total_hours, default_mode)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (code, name, title, desc, weeks, hours, mode))
            c_id = cursor.lastrowid
        course_id_map[code] = c_id

    # 3. Insert or update modules for all courses
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

    # 4. Batches for all courses
    for code, c_id in course_id_map.items():
        batch_code = f"{code}-2026-B1"
        cursor.execute("SELECT id FROM batches WHERE course_id = ?", (c_id,))
        if not cursor.fetchone():
            m_id = 1 if code in ['DA', 'AI', 'FS', 'JV', 'CS', 'CC', 'AD', 'BI'] else 2
            cursor.execute("""
            INSERT INTO batches (course_id, batch_code, name, start_date, end_date, mentor_id, max_students)
            VALUES (?, ?, ?, '2026-06-01', '2026-07-12', ?, 35)
            """, (c_id, batch_code, f"Summer Internship 2026 - {code}", m_id))

    print("All 9 courses, 75+ modules, and batches successfully verified and synchronized.")

def _seed_base_data(cursor, conn):
    print("Seeding TechnoGlobe Bharatpur Centre Base Config & Courses...")

    # 1. Users
    users = [
        ("Nitin Sir (Head)", "nitin@pctm", hash_password("nitin321"), "SUPER_ADMIN"),
        ("Prof. Krishlay Sharma", "krishlay@pctm", hash_password("krishlay321"), "SUPER_ADMIN"),
        ("Prof. Rahul Bhatnagar", "rahul@pctm", hash_password("rahul321"), "SUPER_ADMIN"),
        ("Centre Administrator", "admin@technoglobe.co.in", hash_password("admin123"), "CENTRE_ADMIN"),
        ("System Super Admin", "superadmin@technoglobe.co.in", hash_password("super123"), "SUPER_ADMIN"),
    ]
    cursor.executemany("INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?)", users)

    # 2. Centre Settings
    cursor.execute("""
    INSERT INTO centre_settings (
        id, org_name, centre_name, centre_code, default_college, address, phone, email, website, auth_ref,
        signatory_name, signatory_designation, logo_url, signature_url, stamp_url,
        show_digital_signature, show_digital_stamp, cert_prefix, doc_prefix,
        default_required_hours, default_required_attendance_pct, verification_base_url
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
        'Nitin Sir',
        'Centre Head & Authorized Signatory',
        '', '', '',
        0, 0,
        'TG-BPT', 'TG/BPT',
        120, 75.0,
        'https://technoglobe-certificates.onrender.com'
    );
    """)

    # 3. Mentors
    mentors = [
        ("Prof. Krishlay Sharma", "Professor", "krishlay@pctm", "+91 98290 12345", "Professor & Supervising Faculty for Data Analytics, Computing, AI & Emerging Technologies.", 1),
        ("Prof. Rahul Bhatnagar", "Professor", "rahul@pctm", "+91 94140 33221", "Professor & Supervising Faculty for Digital Marketing, Information Technology & Digital Media.", 1)
    ]
    cursor.executemany("INSERT INTO mentors (name, designation, email, phone, bio, is_active) VALUES (?, ?, ?, ?, ?, ?)", mentors)

    # 4. Courses & Modules
    ensure_all_courses(cursor, conn)

    # 5. Document Templates (Visual Block Customizer)
    templates = [
        ("offer_letter", "Internship Enrollment & Offer Letter", json.dumps([
            {"id": "header", "label": "Franchise Header & Logo", "enabled": True},
            {"id": "doc_ref", "label": "Document Reference & Date", "enabled": True},
            {"id": "recipient", "label": "Student Academic Information", "enabled": True},
            {"id": "subject", "label": "Offer Letter Subject", "enabled": True},
            {"id": "body", "label": "Terms & Training Conditions", "enabled": True},
            {"id": "signatures", "label": "Authorized Signatures", "enabled": True}
        ])),
        ("completion_certificate", "Official Internship Completion Certificate", json.dumps([
            {"id": "borders", "label": "Double Security Borders & Crest", "enabled": True},
            {"id": "header", "label": "TechnoGlobe Official Emblem", "enabled": True},
            {"id": "cert_title", "label": "Certificate Title", "enabled": True},
            {"id": "student_name", "label": "Student Name Highlight", "enabled": True},
            {"id": "citation", "label": "Completion Citation & Dates", "enabled": True},
            {"id": "qr_block", "label": "Live Verification QR Block", "enabled": True},
            {"id": "signatures", "label": "Dual Authorized Signatories", "enabled": True}
        ]))
    ]
    cursor.executemany("INSERT INTO document_templates (template_key, name, layout_config_json) VALUES (?, ?, ?)", templates)

def apply_faculty_updates(cursor, conn):
    # 1. Update Head in centre_settings
    cursor.execute("""
    UPDATE centre_settings 
    SET signatory_name = 'Nitin Sir', 
        signatory_designation = 'Centre Head & Authorized Signatory',
        verification_base_url = 'https://technoglobe-certificates.onrender.com'
    WHERE id = 1
    """)

    # 2. Update / Insert Mentors (Prof. Krishlay Sharma & Prof. Rahul Bhatnagar)
    cursor.execute("""
    INSERT INTO mentors (id, name, designation, email, phone, bio, is_active)
    VALUES 
    (1, 'Prof. Krishlay Sharma', 'Professor', 'krishlay@pctm', '+91 98290 12345', 'Professor & Supervising Faculty for Data Analytics, Computing, AI & Emerging Technologies.', 1),
    (2, 'Prof. Rahul Bhatnagar', 'Professor', 'rahul@pctm', '+91 94140 33221', 'Professor & Supervising Faculty for Digital Marketing, Information Technology & Digital Media.', 1)
    ON CONFLICT(id) DO UPDATE SET
        name = excluded.name,
        designation = excluded.designation,
        email = excluded.email,
        phone = excluded.phone,
        bio = excluded.bio,
        is_active = 1
    """)

    # 3. Clean up legacy users & ensure faculties
    cursor.execute("DELETE FROM users WHERE email IN ('vikas@technoglobe.co.in', 'viewer@technoglobe.co.in')")
    
    # Ensure Nitin Sir (Head)
    cursor.execute("SELECT id FROM users WHERE email = 'nitin@pctm'")
    if cursor.fetchone():
        cursor.execute("UPDATE users SET name = 'Nitin Sir (Head)', role = 'SUPER_ADMIN' WHERE email = 'nitin@pctm'")
    else:
        cursor.execute("INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?)",
                       ('Nitin Sir (Head)', 'nitin@pctm', hash_password('nitin321'), 'SUPER_ADMIN'))

    # Ensure Prof. Krishlay Sharma
    cursor.execute("SELECT id FROM users WHERE email = 'krishlay@pctm'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?)",
                       ('Prof. Krishlay Sharma', 'krishlay@pctm', hash_password('krishlay321'), 'SUPER_ADMIN'))

    # Ensure Prof. Rahul Bhatnagar
    cursor.execute("SELECT id FROM users WHERE email = 'rahul@pctm'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?)",
                       ('Prof. Rahul Bhatnagar', 'rahul@pctm', hash_password('rahul321'), 'SUPER_ADMIN'))

    # 4. Ensure all 9 courses and their modules exist
    ensure_all_courses(cursor, conn)

def seed():
    init_db()
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM centre_settings")
    if cursor.fetchone()[0] == 0:
        _seed_base_data(cursor, conn)
    else:
        apply_faculty_updates(cursor, conn)

    conn.commit()
    conn.close()
    print("Database seeding, course catalog and faculty updates complete.")

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
    VALUES (1, 'Faculty / Admin', 'DELETE_DEMO_DATA', 'STUDENTS', 0, '{"message": "Demo student records purged"}')
    """)
    conn.commit()
    conn.close()
    print("Demo data purged cleanly.")

if __name__ == '__main__':
    seed()
