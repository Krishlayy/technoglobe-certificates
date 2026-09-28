import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { 
  Wand2, CheckCircle2, ArrowRight, ArrowLeft, Download, 
  FileText, Award, Calendar, BookOpen, ShieldCheck, UserCheck, 
  GraduationCap, AlertCircle, RefreshCw, Printer, Sparkles, Building2,
  Globe, Eye, Check, ExternalLink, Edit3, X, User, CheckCircle
} from 'lucide-react';
import { api } from '../services/api';
import { useInstitution } from '../contexts/InstitutionContext';

const COURSE_TRACKS = [
  {
    code: 'DA',
    institutionId: 1,
    title: 'Data Analytics & Business Intelligence',
    badge: 'Python, SQL & Power BI',
    desc: 'Advanced Excel, SQL Queries, Python (Pandas/NumPy), Power BI Interactive Dashboards, DAX Modeling, and Executive Analytics Reporting.',
    project: 'Enterprise Executive KPI Analytics & Automated Business Intelligence Dashboard',
    color: 'blue'
  },
  {
    code: 'FS',
    institutionId: 1,
    title: 'Full Stack Web Development (MERN Stack)',
    badge: 'React.js & Node.js',
    desc: 'Modern React.js 18, Node.js, Express.js, MongoDB Atlas, RESTful APIs, JWT Authentication, Tailwind CSS, and Cloud Deployment.',
    project: 'Full Stack SaaS Cloud Management & Records Platform with Real-Time Interactivity',
    color: 'emerald'
  },
  {
    code: 'AI',
    institutionId: 1,
    title: 'Python Programming & Applied Artificial Intelligence',
    badge: 'Machine Learning & AI',
    desc: 'Python 3.11, Scikit-Learn, TensorFlow/PyTorch, Supervised/Unsupervised ML, Neural Networks, Computer Vision, and FastAPI Model Serving.',
    project: 'Applied Machine Learning Predictive Analytics & Real-Time Computer Vision System',
    color: 'indigo'
  },
  {
    code: 'CS',
    institutionId: 1,
    title: 'Cyber Security & Ethical Hacking',
    badge: 'VAPT & Threat Defense',
    desc: 'Network Protocol Analysis (Wireshark), Linux Administration, OWASP Top 10 Web Security, Metasploit, Cryptography, and VAPT Auditing.',
    project: 'Enterprise Vulnerability Assessment, Penetration Testing & Defensive Security Hardening',
    color: 'rose'
  },
  {
    code: 'JV',
    institutionId: 1,
    title: 'Enterprise Java & Spring Boot Development',
    badge: 'Spring Boot & Microservices',
    desc: 'Java LTS, Object-Oriented Architecture, Spring Boot 3, Spring Data JPA, Hibernate ORM, MySQL, and REST Microservices.',
    project: 'Enterprise Transactional Banking & Distributed Microservices Architecture',
    color: 'amber'
  },
  {
    code: 'CC',
    institutionId: 1,
    title: 'Cloud Computing & DevOps Engineering',
    badge: 'AWS, Docker & CI/CD',
    desc: 'AWS Cloud Infrastructure (EC2, S3, RDS, VPC), Docker Containerization, Kubernetes Clusters, GitHub Actions CI/CD, and Terraform IaC.',
    project: 'Automated Multi-Tier Cloud Deployment Infrastructure with Docker & Kubernetes CI/CD',
    color: 'sky'
  },
  {
    code: 'AD',
    institutionId: 1,
    title: 'Android & Mobile App Development (Kotlin)',
    badge: 'Kotlin & Jetpack Compose',
    desc: 'Native Android Kotlin, Jetpack Compose UI, MVVM Clean Architecture, Room Database, Retrofit REST Clients, and Firebase Integration.',
    project: 'Native Android Mobile Telemedicine & Real-Time Service Tracking Application',
    color: 'violet'
  },
  {
    code: 'DM',
    institutionId: 1,
    title: 'Digital Marketing & Growth Strategies',
    badge: 'SEO, SEM & Meta Ads',
    desc: 'Search Engine Optimization (SEO), Social Media Marketing (SMM), Google Search Ads, Meta Campaigns, GA4 Analytics, and Growth Funnels.',
    project: 'Omnichannel Digital Performance Marketing & High-Converting Lead Generation Funnel',
    color: 'purple'
  }
];

const DOSSIER_FILES_15 = [
  { id: 'offer', name: '1. Offer Letter of Internship', code: 'OFF-01', desc: 'Formal corporate induction and terms of internship agreement.', icon: FileText, tag: 'Induction' },
  { id: 'joining', name: '2. Joining & Acceptance Letter', code: 'JON-02', desc: 'Candidate confirmation of joining and reporting protocols.', icon: UserCheck, tag: 'Reporting' },
  { id: 'syllabus', name: '3. Curriculum Blueprint & Syllabus', code: 'SYL-03', desc: 'Comprehensive module breakdown, theory, and laboratory outcomes.', icon: BookOpen, tag: 'Syllabus' },
  { id: 'schedule', name: '4. Technical Training Schedule', code: 'SCH-04', desc: 'Curriculum milestones, weekly lab schedule, and classroom roadmap.', icon: Calendar, tag: 'Roadmap' },
  { id: 'attendance_sheet', name: '5. Daily Attendance Register', code: 'ATT-05', desc: '36 working days roll-call register with punch-in/out timestamps.', icon: Calendar, tag: '36 Days' },
  { id: 'attendance_summary', name: '6. Attendance Summary Register', code: 'SUM-06', desc: 'Executive summary with percentage and authorized leaves analysis.', icon: CheckCircle2, tag: 'Summary' },
  { id: 'daily_log', name: '7. Student Daily Logbook', code: 'LOG-07', desc: 'Day-by-day practical task reflections, tools used, and topics covered.', icon: BookOpen, tag: 'Logbook' },
  { id: 'weekly_report', name: '8. Weekly Progress Appraisal', code: 'WKR-08', desc: '6 weekly supervisor assessments and milestone completions.', icon: FileText, tag: 'Weekly' },
  { id: 'project_assignment', name: '9. Project Assignment & Synopsis', code: 'PRJ-09', desc: 'Capstone problem statement, architectural requirements, and design scope.', icon: Sparkles, tag: 'Project' },
  { id: 'project_report', name: '10. Detailed Project Report', code: 'REP-10', desc: 'Technical documentation of system architecture, implementation, and deliverables.', icon: FileText, tag: 'Report' },
  { id: 'evaluation', name: '11. Mentor Rubrics Evaluation', code: 'EVL-11', desc: '100-point multi-criteria performance grading and supervisor feedback.', icon: Award, tag: 'Grading' },
  { id: 'performance', name: '12. Comprehensive Performance Report', code: 'PRF-12', desc: 'Standardized evaluation sheet detailing competencies and grade bands.', icon: CheckCircle2, tag: 'Appraisal' },
  { id: 'feedback', name: '13. Candidate Feedback Form', code: 'FDB-12', desc: 'Student reflection on facilities, mentorship, and practical training.', icon: UserCheck, tag: 'Feedback' },
  { id: 'completion_cert', name: '14. Certificate of Training Completion', code: 'CRT-14', desc: 'Prestigious official completion certificate with cryptographic QR code.', icon: Award, tag: 'Certificate' },
  { id: 'experience_cert', name: '15. Experience & Clearance Certificate', code: 'EXP-15', desc: 'Formal recommendation and experience clearance verification letter.', icon: FileText, tag: 'Clearance' }
];

export const StepByStepWizardPage: React.FC = () => {
  const { activeInstitution } = useInstitution();
  const navigate = useNavigate();

  const [currentStep, setCurrentStep] = useState(1);
  const [generating, setGenerating] = useState(false);
  const [generationResult, setGenerationResult] = useState<any>(null);
  const [error, setError] = useState('');
  const [previewModalOpen, setPreviewModalOpen] = useState(false);

  // Form State
  const [formData, setFormData] = useState({
    institution_id: 1,
    full_name: 'Aryan Sharma',
    father_mother_name: 'Rajesh Sharma',
    dob: '2004-05-15',
    gender: 'Male',
    mobile: '9876543210',
    email: 'aryan.sharma@example.com',
    address: 'Near SP Office, Bharatpur (Raj.)',
    city: 'Bharatpur',
    state: 'Rajasthan',
    college_name: 'TechnoGlobe Institute of Information Technology, Bharatpur',
    degree: 'BCA',
    branch: 'Computer Science',
    semester_year: '6th Semester',
    academic_session: '2025-2026',
    course_track: 'DA',
    start_date: '2026-06-01',
    end_date: '2026-07-12',
    total_days: 36,
    total_hours: 120,
    custom_project_title: 'Enterprise Executive KPI Analytics & Automated Business Intelligence Dashboard',
    custom_faculty_name: '', // Optional faculty
    custom_faculty_designation: 'Technical Trainer / Faculty Guide'
  });

  const handleFillSample = () => {
    setFormData({
      institution_id: 1,
      full_name: 'Aryan Sharma',
      father_mother_name: 'Rajesh Sharma',
      dob: '2004-05-15',
      gender: 'Male',
      mobile: '9876543210',
      email: 'aryan.sharma@example.com',
      address: 'Civil Lines, Bharatpur (Raj.)',
      city: 'Bharatpur',
      state: 'Rajasthan',
      college_name: 'TechnoGlobe Institute of Information Technology, Bharatpur',
      degree: 'BCA',
      branch: 'Computer Science',
      semester_year: '6th Semester',
      academic_session: '2025-2026',
      course_track: 'DA',
      start_date: '2026-06-01',
      end_date: '2026-07-12',
      total_days: 36,
      total_hours: 120,
      custom_project_title: 'Enterprise Executive KPI Analytics & Automated Business Intelligence Dashboard',
      custom_faculty_name: '',
      custom_faculty_designation: 'Technical Trainer / Faculty Guide'
    });
  };

  const handleTrackChange = (code: string) => {
    const trk = COURSE_TRACKS.find(t => t.code === code);
    setFormData(prev => ({
      ...prev,
      course_track: code,
      custom_project_title: trk ? trk.project : prev.custom_project_title
    }));
  };

  const handleGenerateAll = async () => {
    try {
      setGenerating(true);
      setError('');
      
      const payload = {
        institution_id: 1,
        full_name: formData.full_name.trim(),
        father_mother_name: formData.father_mother_name.trim(),
        dob: formData.dob,
        gender: formData.gender,
        mobile: formData.mobile.trim(),
        email: formData.email.trim(),
        address: formData.address.trim(),
        city: formData.city.trim(),
        state: formData.state.trim(),
        college_name: formData.college_name.trim(),
        degree: formData.degree.trim(),
        branch: formData.branch.trim(),
        semester_year: formData.semester_year,
        academic_session: formData.academic_session,
        course_track: formData.course_track,
        start_date: formData.start_date,
        end_date: formData.end_date,
        custom_project_title: formData.custom_project_title.trim(),
        custom_faculty_name: formData.custom_faculty_name.trim(),
        custom_faculty_designation: formData.custom_faculty_designation.trim()
      };

      const res = await api.quickGenerateInternship(payload);
      setGenerationResult(res);
      setCurrentStep(5); // Download step
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to generate documentation.');
    } finally {
      setGenerating(false);
    }
  };

  const currentTrackObj = COURSE_TRACKS.find(t => t.code === formData.course_track) || COURSE_TRACKS[0];

  const steps = [
    { num: 1, label: '1. Candidate Profile', desc: 'Student Details & College' },
    { num: 2, label: '2. Course & Mentorship', desc: 'IT Track & Optional Faculty' },
    { num: 3, label: '3. Schedule & Project', desc: '36 Working Days & Capstone' },
    { num: 4, label: '4. 15-Doc Pre-Review', desc: 'Review & Verify Dossier' },
    { num: 5, label: '5. Download Dossier', desc: 'Instant ZIP & Certificates' }
  ];

  const inputStyle = "w-full px-4 py-3 text-sm font-bold text-slate-900 bg-white border-2 border-slate-300 rounded-xl shadow-xs focus:border-blue-600 focus:ring-4 focus:ring-blue-100 transition-all placeholder:text-slate-400";
  const labelStyle = "block text-xs font-bold uppercase tracking-wider text-slate-800 mb-1.5";

  return (
    <div className="max-w-5xl mx-auto space-y-6 pb-16">
      {/* Top Banner */}
      <div className="bg-gradient-to-r from-[#0A2540] via-[#0F2942] to-[#1E3A8A] text-white p-6 sm:p-8 rounded-3xl shadow-xl border border-blue-900 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-80 h-80 bg-amber-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="relative z-10 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div className="space-y-1.5">
            <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-amber-400/20 text-amber-300 border border-amber-400/30 text-xs font-bold uppercase tracking-wider">
              <Sparkles className="w-3.5 h-3.5 text-amber-400" />
              <span>TechnoGlobe Bharatpur Dossier Engine</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-serif font-black tracking-tight text-white">
              15-Document Dossier & Certificate Wizard
            </h1>
            <p className="text-xs sm:text-sm text-slate-300 max-w-2xl leading-relaxed">
              Enter candidate details once. The engine will generate all <b>15 official dossier documents</b>, 36-day attendance logbook, project report, evaluation rubrics, and scannable certificate with authentic signatures and official seal.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleFillSample}
              className="px-3.5 py-2.5 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 text-xs font-black transition-all cursor-pointer shadow-md flex items-center space-x-1.5"
            >
              <Sparkles className="w-3.5 h-3.5" />
              <span>Pre-fill Sample</span>
            </button>
          </div>
        </div>
      </div>

      {/* Wizard Step Progress Bar */}
      <div className="bg-white p-4 sm:p-6 rounded-2xl shadow-xs border border-slate-200">
        <div className="grid grid-cols-2 md:grid-cols-5 gap-2 sm:gap-3">
          {steps.map((s) => {
            const isActive = currentStep === s.num;
            const isCompleted = currentStep > s.num;
            return (
              <button
                key={s.num}
                onClick={() => isCompleted && setCurrentStep(s.num)}
                disabled={!isCompleted && !isActive}
                className={`flex flex-col p-3 rounded-xl text-left border transition-all ${
                  isActive
                    ? 'bg-blue-900 border-blue-900 text-white shadow-md'
                    : isCompleted
                    ? 'bg-emerald-50 border-emerald-300 text-emerald-950 cursor-pointer'
                    : 'bg-slate-50 border-slate-200 text-slate-400'
                }`}
              >
                <div className="flex items-center justify-between text-[11px] font-black uppercase tracking-wider">
                  <span>Step {s.num}</span>
                  {isCompleted && <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />}
                </div>
                <div className={`text-xs font-black mt-1 ${isActive ? 'text-white' : isCompleted ? 'text-emerald-900' : 'text-slate-600'}`}>
                  {s.label.split('. ')[1]}
                </div>
                <div className={`text-[10px] mt-0.5 truncate ${isActive ? 'text-blue-200' : 'text-slate-500'}`}>
                  {s.desc}
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {error && (
        <div className="p-4 bg-rose-50 border-2 border-rose-300 rounded-2xl text-rose-800 text-xs font-bold flex items-center space-x-2">
          <AlertCircle className="w-5 h-5 text-rose-600 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* STEP 1: Candidate Profile */}
      {currentStep === 1 && (
        <div className="bg-white p-6 sm:p-8 rounded-3xl shadow-xs border border-slate-200 space-y-6 text-left">
          <div className="border-b border-slate-100 pb-4">
            <h2 className="text-lg font-black text-slate-900">Step 1: Student Information & Academic Profile</h2>
            <p className="text-xs text-slate-500">Provide the candidate's personal details and college enrollment information.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className={labelStyle}>Full Candidate Name *</label>
              <input
                type="text"
                value={formData.full_name}
                onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                className={inputStyle}
                placeholder="e.g. Aryan Sharma"
                required
              />
            </div>

            <div>
              <label className={labelStyle}>Father's / Mother's Name *</label>
              <input
                type="text"
                value={formData.father_mother_name}
                onChange={(e) => setFormData({ ...formData, father_mother_name: e.target.value })}
                className={inputStyle}
                placeholder="e.g. Rajesh Sharma"
                required
              />
            </div>

            <div>
              <label className={labelStyle}>Mobile Number *</label>
              <input
                type="text"
                value={formData.mobile}
                onChange={(e) => setFormData({ ...formData, mobile: e.target.value })}
                className={inputStyle}
                placeholder="e.g. 9876543210"
                required
              />
            </div>

            <div>
              <label className={labelStyle}>Email Address *</label>
              <input
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                className={inputStyle}
                placeholder="e.g. aryan.sharma@example.com"
                required
              />
            </div>

            <div>
              <label className={labelStyle}>College / University Name *</label>
              <input
                type="text"
                value={formData.college_name}
                onChange={(e) => setFormData({ ...formData, college_name: e.target.value })}
                className={inputStyle}
                placeholder="e.g. TechnoGlobe Institute of Information Technology, Bharatpur"
                required
              />
            </div>

            <div>
              <label className={labelStyle}>Degree / Program *</label>
              <input
                type="text"
                value={formData.degree}
                onChange={(e) => setFormData({ ...formData, degree: e.target.value })}
                className={inputStyle}
                placeholder="e.g. BCA / B.Tech / B.Sc IT"
                required
              />
            </div>

            <div>
              <label className={labelStyle}>Branch / Specialization *</label>
              <input
                type="text"
                value={formData.branch}
                onChange={(e) => setFormData({ ...formData, branch: e.target.value })}
                className={inputStyle}
                placeholder="e.g. Computer Science"
                required
              />
            </div>

            <div>
              <label className={labelStyle}>Semester & Session</label>
              <div className="grid grid-cols-2 gap-2">
                <input
                  type="text"
                  value={formData.semester_year}
                  onChange={(e) => setFormData({ ...formData, semester_year: e.target.value })}
                  className={inputStyle}
                  placeholder="6th Semester"
                />
                <input
                  type="text"
                  value={formData.academic_session}
                  onChange={(e) => setFormData({ ...formData, academic_session: e.target.value })}
                  className={inputStyle}
                  placeholder="2025-2026"
                />
              </div>
            </div>
          </div>

          <div className="pt-4 flex justify-end">
            <button
              type="button"
              onClick={() => setCurrentStep(2)}
              className="px-6 py-3 bg-blue-900 hover:bg-blue-800 text-white font-black text-xs uppercase tracking-wider rounded-xl shadow-md flex items-center space-x-2 cursor-pointer transition-all"
            >
              <span>Proceed to Course & Faculty</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* STEP 2: Course Track & Optional Faculty */}
      {currentStep === 2 && (
        <div className="bg-white p-6 sm:p-8 rounded-3xl shadow-xs border border-slate-200 space-y-6 text-left">
          <div className="border-b border-slate-100 pb-4">
            <h2 className="text-lg font-black text-slate-900">Step 2: Technical Course Track & Authority Signatures</h2>
            <p className="text-xs text-slate-500">Select the TechnoGlobe training curriculum and configure optional supervising faculty.</p>
          </div>

          {/* Curriculums Grid */}
          <div>
            <label className={labelStyle}>Select TechnoGlobe IT Course Track *</label>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mt-2">
              {COURSE_TRACKS.map((t) => {
                const isSelected = formData.course_track === t.code;
                return (
                  <button
                    key={t.code}
                    type="button"
                    onClick={() => handleTrackChange(t.code)}
                    className={`p-4 rounded-2xl border-2 text-left transition-all cursor-pointer ${
                      isSelected
                        ? 'border-blue-900 bg-blue-50/60 shadow-xs ring-2 ring-blue-900/20'
                        : 'border-slate-200 bg-white hover:border-slate-300'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-xs px-2.5 py-0.5 rounded-full bg-blue-900 text-white font-black">
                        {t.code}
                      </span>
                      <span className="text-[11px] font-bold text-blue-900 bg-blue-100 px-2 py-0.5 rounded-md">
                        {t.badge}
                      </span>
                    </div>
                    <div className="font-black text-sm text-slate-900 mt-2">{t.title}</div>
                    <p className="text-[11px] text-slate-500 mt-1 leading-relaxed line-clamp-2">{t.desc}</p>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Optional Faculty Section */}
          <div className="p-5 bg-slate-50 rounded-2xl border border-slate-200 space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-xs font-black uppercase tracking-wider text-slate-900">Supervising Faculty (Strictly Optional)</h3>
                <p className="text-[11px] text-slate-500">If left blank, documents will render a prominent single authority signature for <b>Nitin Agarwal</b> (Director / Center Head).</p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className={labelStyle}>Faculty Name (Optional)</label>
                <input
                  type="text"
                  value={formData.custom_faculty_name}
                  onChange={(e) => setFormData({ ...formData, custom_faculty_name: e.target.value })}
                  className={inputStyle}
                  placeholder="Leave empty for single authority Nitin Agarwal"
                />
              </div>

              <div>
                <label className={labelStyle}>Faculty Designation (Optional)</label>
                <input
                  type="text"
                  value={formData.custom_faculty_designation}
                  onChange={(e) => setFormData({ ...formData, custom_faculty_designation: e.target.value })}
                  className={inputStyle}
                  placeholder="e.g. Technical Trainer / Faculty Guide"
                />
              </div>
            </div>
          </div>

          <div className="pt-4 flex justify-between">
            <button
              type="button"
              onClick={() => setCurrentStep(1)}
              className="px-6 py-3 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs uppercase tracking-wider rounded-xl cursor-pointer"
            >
              <ArrowLeft className="w-4 h-4 inline mr-1" /> Back
            </button>
            <button
              type="button"
              onClick={() => setCurrentStep(3)}
              className="px-6 py-3 bg-blue-900 hover:bg-blue-800 text-white font-black text-xs uppercase tracking-wider rounded-xl shadow-md flex items-center space-x-2 cursor-pointer"
            >
              <span>Proceed to Schedule & Project</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* STEP 3: Schedule & Capstone Project */}
      {currentStep === 3 && (
        <div className="bg-white p-6 sm:p-8 rounded-3xl shadow-xs border border-slate-200 space-y-6 text-left">
          <div className="border-b border-slate-100 pb-4">
            <h2 className="text-lg font-black text-slate-900">Step 3: Training Timeline & Capstone Project</h2>
            <p className="text-xs text-slate-500">Configure the 6-week training duration and custom capstone project title.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className={labelStyle}>Start Date *</label>
              <input
                type="date"
                value={formData.start_date}
                onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
                className={inputStyle}
                required
              />
            </div>

            <div>
              <label className={labelStyle}>End Date *</label>
              <input
                type="date"
                value={formData.end_date}
                onChange={(e) => setFormData({ ...formData, end_date: e.target.value })}
                className={inputStyle}
                required
              />
            </div>
          </div>

          <div>
            <label className={labelStyle}>Capstone Project Title *</label>
            <textarea
              rows={2}
              value={formData.custom_project_title}
              onChange={(e) => setFormData({ ...formData, custom_project_title: e.target.value })}
              className={inputStyle}
              placeholder="e.g. Enterprise Executive KPI Analytics & Automated Business Intelligence Dashboard"
              required
            />
          </div>

          <div className="pt-4 flex justify-between">
            <button
              type="button"
              onClick={() => setCurrentStep(2)}
              className="px-6 py-3 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs uppercase tracking-wider rounded-xl cursor-pointer"
            >
              <ArrowLeft className="w-4 h-4 inline mr-1" /> Back
            </button>
            <button
              type="button"
              onClick={() => setCurrentStep(4)}
              className="px-6 py-3 bg-blue-900 hover:bg-blue-800 text-white font-black text-xs uppercase tracking-wider rounded-xl shadow-md flex items-center space-x-2 cursor-pointer"
            >
              <span>Proceed to 15-Doc Pre-Review</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* STEP 4: 15-Doc Pre-Generation Review */}
      {currentStep === 4 && (
        <div className="bg-white p-6 sm:p-8 rounded-3xl shadow-xs border border-slate-200 space-y-6 text-left">
          <div className="border-b border-slate-100 pb-4 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div>
              <h2 className="text-lg font-black text-slate-900">Step 4: Pre-Generation Dossier Review (All 15 Documents)</h2>
              <p className="text-xs text-slate-500">Verify candidate details and review the list of 15 documents ready for generation.</p>
            </div>
            <span className="text-xs px-3 py-1 bg-emerald-100 text-emerald-900 font-black rounded-full self-start">
              15 Documents Verified
            </span>
          </div>

          {/* Candidate Summary Card */}
          <div className="p-4 bg-blue-50/70 border border-blue-200 rounded-2xl grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
            <div>
              <span className="text-slate-500 block">Candidate:</span>
              <span className="font-black text-slate-900">{formData.full_name}</span>
            </div>
            <div>
              <span className="text-slate-500 block">Course Track:</span>
              <span className="font-black text-blue-900">{currentTrackObj.title}</span>
            </div>
            <div>
              <span className="text-slate-500 block">Duration:</span>
              <span className="font-black text-slate-900">6 Weeks (120 Hours)</span>
            </div>
            <div>
              <span className="text-slate-500 block">Authority Signatory:</span>
              <span className="font-black text-slate-900">
                {formData.custom_faculty_name ? `Dual (${formData.custom_faculty_name} + Nitin Agarwal)` : 'Nitin Agarwal (Director)'}
              </span>
            </div>
          </div>

          {/* 15 Files Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-2.5">
            {DOSSIER_FILES_15.map((f, idx) => {
              const Icon = f.icon;
              return (
                <div key={f.id} className="p-3 bg-slate-50 rounded-xl border border-slate-200 flex items-start space-x-3">
                  <div className="w-7 h-7 rounded-lg bg-blue-900 text-white flex items-center justify-center font-black text-xs shrink-0 mt-0.5">
                    {idx + 1}
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="text-xs font-black text-slate-900 truncate">{f.name.split('. ')[1]}</div>
                    <p className="text-[10px] text-slate-500 line-clamp-1">{f.desc}</p>
                  </div>
                  <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-1" />
                </div>
              );
            })}
          </div>

          <div className="pt-4 flex justify-between">
            <button
              type="button"
              onClick={() => setCurrentStep(3)}
              className="px-6 py-3 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs uppercase tracking-wider rounded-xl cursor-pointer"
            >
              <ArrowLeft className="w-4 h-4 inline mr-1" /> Back
            </button>
            <button
              type="button"
              onClick={handleGenerateAll}
              disabled={generating}
              className="px-8 py-3.5 bg-emerald-600 hover:bg-emerald-500 text-white font-black text-sm uppercase tracking-wider rounded-xl shadow-lg flex items-center space-x-2 cursor-pointer disabled:opacity-50 transition-all"
            >
              {generating ? (
                <span>Assembling 15-Doc Dossier...</span>
              ) : (
                <>
                  <Wand2 className="w-5 h-5" />
                  <span>Generate Full 15-Doc Dossier & ZIP</span>
                </>
              )}
            </button>
          </div>
        </div>
      )}

      {/* STEP 5: Download Package */}
      {currentStep === 5 && generationResult && (
        <div className="bg-white p-6 sm:p-8 rounded-3xl shadow-xs border border-slate-200 space-y-6 text-center">
          <div className="w-16 h-16 bg-emerald-100 text-emerald-700 rounded-full flex items-center justify-center mx-auto shadow-md">
            <CheckCircle2 className="w-10 h-10" />
          </div>

          <div className="space-y-1">
            <h2 className="text-2xl font-serif font-black text-slate-900">
              Dossier Successfully Generated!
            </h2>
            <p className="text-xs text-slate-500 max-w-md mx-auto">
              All 15 documents and the completion certificate for <b>{formData.full_name}</b> have been compiled and cryptographically signed.
            </p>
          </div>

          {/* Action Download Buttons */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 max-w-xl mx-auto pt-2">
            <a
              href={`/api/internships/${generationResult.internship_id}/zip`}
              target="_blank"
              rel="noreferrer"
              className="p-5 bg-blue-900 hover:bg-blue-800 text-white rounded-2xl shadow-lg flex flex-col items-center justify-center space-y-2 font-black text-sm transition-all"
            >
              <Download className="w-7 h-7 text-amber-300" />
              <span>Download Complete 15-Doc ZIP</span>
              <span className="text-[10px] text-blue-200 font-normal">All 15 Individual PDFs in ZIP Bundle</span>
            </a>

            <a
              href={`/api/internships/${generationResult.internship_id}/documents/completion_certificate/pdf`}
              target="_blank"
              rel="noreferrer"
              className="p-5 bg-amber-500 hover:bg-amber-400 text-slate-950 rounded-2xl shadow-lg flex flex-col items-center justify-center space-y-2 font-black text-sm transition-all"
            >
              <Award className="w-7 h-7 text-slate-950" />
              <span>Download Completion Certificate</span>
              <span className="text-[10px] text-slate-900 font-medium">Landscape A4 High-Res PDF</span>
            </a>
          </div>

          <div className="pt-4 flex justify-center space-x-3">
            <button
              onClick={() => {
                setGenerationResult(null);
                setCurrentStep(1);
              }}
              className="px-6 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold rounded-xl"
            >
              Create Another Student Dossier
            </button>
            <Link
              to="/"
              className="px-6 py-2.5 bg-slate-900 hover:bg-slate-800 text-white text-xs font-bold rounded-xl"
            >
              Back to Admin Dashboard
            </Link>
          </div>
        </div>
      )}
    </div>
  );
};

export default StepByStepWizardPage;
