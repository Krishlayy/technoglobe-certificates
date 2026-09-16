import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { 
  Wand2, CheckCircle2, ArrowRight, ArrowLeft, Download, 
  FileText, Award, Calendar, BookOpen, ShieldCheck, UserCheck, 
  GraduationCap, AlertCircle, RefreshCw, Printer, Sparkles, Building2,
  Sun, Globe, Eye, Check, ExternalLink, Edit3, X
} from 'lucide-react';
import { api } from '../services/api';
import { useInstitution } from '../contexts/InstitutionContext';

const COURSE_TRACKS = [
  // --- Poswal Developers Tracks (Solar & Industrial) ---
  {
    code: 'SOL-01',
    institutionId: 2,
    title: 'Rooftop Solar PV Installation & Building Integration (BIPV)',
    badge: 'Solar & BIPV',
    desc: 'Civil rooftop structural evaluation, shadow modeling, monocrystalline module mounting, aluminum rail racking, waterproof roof penetrations, string sizing, and DC cable dressing.',
    project: '50 kWp Commercial Rooftop Solar PV & Building-Integrated (BIPV) System Installation',
    color: 'amber',
    defaultMentor: 'Mahesh Chand Saini'
  },
  {
    code: 'SOL-02',
    institutionId: 2,
    title: 'Solar Structure Fitting, Panel Mounting & Civil Layout',
    badge: 'Structure Fitting',
    desc: 'Hot-dip galvanized (HDG) mounting structure assembly, tilt angle optimization, torque specifications, foundation civil work, wind-load anchoring, and module stringing.',
    project: '100 kWp Ground-Mounted Fixed-Tilt Solar Array Structural Layout & Alignment',
    color: 'orange',
    defaultMentor: 'Mahesh Chand Saini'
  },
  {
    code: 'SOL-03',
    institutionId: 2,
    title: 'Solar Electrical Systems, Inverters & Grid-Tied Technology',
    badge: 'Electrical & Inverter',
    desc: 'String & central inverters, MPPT tracking, DC/AC distribution boxes, SPD surge protection, AC combiner boxes, LT panel integration, and grid synchronization.',
    project: 'Grid-Connected 25 kW Solar Inverter & Net-Metering Synchronization Facility',
    color: 'yellow',
    defaultMentor: 'Mahesh Chand Saini'
  },
  {
    code: 'SOL-04',
    institutionId: 2,
    title: 'Industrial Solar Power Plant Operations & Maintenance (O&M)',
    badge: 'Industrial Solar O&M',
    desc: 'Thermal imaging inspections, IV-curve tracing, degradation analysis, soiling loss mitigation, SCADA telemetry monitoring, and preventive maintenance protocols.',
    project: 'Preventive O&M Audit & SCADA Telemetry Protocol for 500 kWp Industrial Plant',
    color: 'emerald',
    defaultMentor: 'Mahesh Chand Saini'
  },
  {
    code: 'SOL-05',
    institutionId: 2,
    title: 'Solar Water Heating & Agricultural Pumping Systems',
    badge: 'Pumps & Thermal',
    desc: 'Evacuated tube collectors (ETC), flat plate collectors (FPC), solar VFD pump controllers, brushless DC surface/submersible pumps, and piping layout.',
    project: '7.5 HP Solar Agricultural Irrigation Pumping & Micro-Grid Distribution',
    color: 'teal',
    defaultMentor: 'Mahesh Chand Saini'
  },
  {
    code: 'SOL-06',
    institutionId: 2,
    title: 'Off-Grid Solar Energy Storage & Battery Management (BMS)',
    badge: 'Storage & Batteries',
    desc: 'Lithium iron phosphate (LiFePO4) & tubular lead-acid batteries, hybrid inverters, DoD optimization, charge controllers (PWM/MPPT), and battery safety.',
    project: 'Hybrid 10 kVA Off-Grid Solar Energy Storage & Battery Management Facility',
    color: 'sky',
    defaultMentor: 'Mahesh Chand Saini'
  },
  {
    code: 'SOL-07',
    institutionId: 2,
    title: 'Solar PV System Design, Load Estimation & PVsyst Simulation',
    badge: 'PVsyst Design',
    desc: 'Solar irradiance modeling, PVsyst & HelioScope simulation, energy yield forecasting, loss diagram assessment, single-line diagram (SLD), and BOM estimation.',
    project: 'Comprehensive Techno-Economic PVsyst Simulation for 100 kWp Rooftop System',
    color: 'indigo',
    defaultMentor: 'Mahesh Chand Saini'
  },
  {
    code: 'SOL-08',
    institutionId: 2,
    title: 'Solar Safety Standards, Electrical Earthing & Net-Metering',
    badge: 'Safety & Metering',
    desc: 'Chemical earthing pits, copper strip bonded grounding, lightning arrestor (ESE) design, DISCOM net-metering protocols, and IEC/IS compliance documentation.',
    project: 'High-Integrity Earthing Grid & DISCOM Net-Metering Compliance Architecture',
    color: 'rose',
    defaultMentor: 'Mahesh Chand Saini'
  },

  // --- Poddar College & Technoglobe IT Tracks ---
  {
    code: 'DA',
    institutionId: 1,
    title: 'Data Analytics & Business Intelligence',
    badge: 'Python & Power BI',
    desc: 'Python, Pandas, NumPy, SQL, Power BI, Advanced Excel, Data Cleaning, and Executive Reporting.',
    project: 'Retail Sales & Customer Churn Predictive Dashboard',
    color: 'blue',
    defaultMentor: ''
  },
  {
    code: 'DM',
    institutionId: 1,
    title: 'Digital Marketing & Growth Strategy',
    badge: 'SEO, Ads & GA4',
    desc: 'SEO, Social Media, Google Ads, Meta Ads, GA4 Web Analytics, Copywriting & AI Content Workflows.',
    project: 'Omnichannel Healthcare Clinic Growth & Lead Generation Campaign',
    color: 'purple',
    defaultMentor: ''
  },
  {
    code: 'FS',
    institutionId: 1,
    title: 'Full Stack Web Development (MERN)',
    badge: 'React & Node.js',
    desc: 'React.js 18, Node.js, Express.js, MongoDB Atlas, TypeScript, Tailwind CSS, REST APIs & Cloud Deployment.',
    project: 'Cloud Patient Consultation & Health Records Management Portal',
    color: 'emerald',
    defaultMentor: ''
  },
  {
    code: 'AI',
    institutionId: 1,
    title: 'Python AI, ML & Data Science',
    badge: 'ML & Deep Learning',
    desc: 'Python 3.11, Scikit-Learn, TensorFlow, XGBoost, Predictive Modeling, EDA & FastAPI Deployment.',
    project: 'Clinical Disease Risk & Patient Prognosis Prediction System',
    color: 'indigo',
    defaultMentor: ''
  },
  {
    code: 'CS',
    institutionId: 1,
    title: 'Cyber Security & Defensive Ops',
    badge: 'Security & VAPT',
    desc: 'Kali Linux, Wireshark, Burp Suite, Network Sniffing, Vulnerability Assessment, Cryptography & Defensive Hardening.',
    project: 'Enterprise Vulnerability Assessment & Defensive Threat Mitigation',
    color: 'rose',
    defaultMentor: ''
  },
  {
    code: 'CC',
    institutionId: 1,
    title: 'Cloud Computing & DevOps Architecture',
    badge: 'AWS, Docker & K8s',
    desc: 'AWS EC2/VPC/S3, Docker Containerization, Kubernetes Orchestration, GitHub Actions CI/CD & Terraform IaC.',
    project: 'Multi-Tier Cloud Infrastructure Deployment with Docker & CI/CD',
    color: 'sky',
    defaultMentor: ''
  },
  {
    code: 'JV',
    institutionId: 1,
    title: 'Java Enterprise & Spring Boot Development',
    badge: 'Spring Boot & JPA',
    desc: 'Java 17/21 LTS, Spring Boot 3, Spring Data JPA, Hibernate, MySQL, Spring Security & Microservice APIs.',
    project: 'Enterprise Banking & Financial Transaction Microservices Platform',
    color: 'amber',
    defaultMentor: ''
  },
  {
    code: 'BI',
    institutionId: 1,
    title: 'Bioinformatics & Computational Biology',
    badge: 'Genomics & PyMOL',
    desc: 'BioPython, Pairwise/MSA Alignment, BLAST+, NCBI Entrez APIs, Protein Structure Visualization & Genomic Data.',
    project: 'Computational Genomic Mutation Profiling & Protein Homology Modeling',
    color: 'teal',
    defaultMentor: ''
  },
  {
    code: 'AD',
    institutionId: 1,
    title: 'Android Mobile App Development (Kotlin)',
    badge: 'Kotlin & Compose',
    desc: 'Kotlin 1.9, Jetpack Compose, Material 3, Room SQLite Database, Retrofit 2, Coroutines, Flow & MVVM Architecture.',
    project: 'Modern Telemedicine Consultation & Health Tracking Android App',
    color: 'violet',
    defaultMentor: ''
  }
];

const DOSSIER_FILES_15 = [
  { id: 'offer', name: '1. Offer Letter of Internship', code: 'OFF-01', desc: 'Formal corporate induction and terms of internship agreement.', icon: FileText, tag: 'Induction' },
  { id: 'joining', name: '2. Joining & Acceptance Letter', code: 'JON-02', desc: 'Candidate confirmation of joining and reporting protocols.', icon: UserCheck, tag: 'Reporting' },
  { id: 'schedule', name: '3. Technical Training Schedule', code: 'SCH-03', desc: 'Curriculum milestones, weekly lab schedule, and classroom roadmap.', icon: Calendar, tag: 'Roadmap' },
  { id: 'attendance_sheet', name: '4. Daily Attendance Register', code: 'ATT-04', desc: '36 working days roll-call register with punch-in/out timestamps.', icon: Calendar, tag: '36 Days' },
  { id: 'attendance_summary', name: '5. Attendance Summary Register', code: 'SUM-05', desc: 'Executive summary with percentage and authorized leaves analysis.', icon: CheckCircle2, tag: 'Summary' },
  { id: 'daily_log', name: '6. Student Daily Logbook', code: 'LOG-06', desc: 'Day-by-day practical task reflections, tools used, and topics covered.', icon: BookOpen, tag: 'Logbook' },
  { id: 'weekly_report', name: '7. Weekly Progress Appraisal', code: 'WKR-07', desc: '6 weekly supervisor assessments and milestone completions.', icon: FileText, tag: 'Weekly' },
  { id: 'project_assignment', name: '8. Project Assignment & Synopsis', code: 'PRJ-08', desc: 'Capstone problem statement, architectural requirements, and design scope.', icon: Sparkles, tag: 'Project' },
  { id: 'project_report', name: '9. Detailed Project Report', code: 'REP-09', desc: 'Technical documentation of system architecture, implementation, and deliverables.', icon: FileText, tag: 'Report' },
  { id: 'evaluation', name: '10. Mentor Rubrics Evaluation', code: 'EVL-10', desc: '100-point multi-criteria performance grading and supervisor feedback.', icon: Award, tag: 'Grading' },
  { id: 'performance', name: '11. Comprehensive Performance Report', code: 'PRF-11', desc: 'Standardized evaluation sheet detailing competencies and grade bands.', icon: CheckCircle2, tag: 'Appraisal' },
  { id: 'feedback', name: '12. Candidate Feedback Form', code: 'FDB-12', desc: 'Student reflection on facilities, mentorship, and practical training.', icon: UserCheck, tag: 'Feedback' },
  { id: 'certificate', name: '13. Internship Completion Certificate', code: 'CRT-13', desc: 'Official A4 landscape vector certificate with scannable QR and seals.', icon: Award, tag: 'Primary' },
  { id: 'experience', name: '14. Professional Experience Certificate', code: 'EXP-14', desc: 'Verification of professional tenure and core competencies letter.', icon: ShieldCheck, tag: 'Relieving' },
  { id: 'consolidated', name: '15. Consolidated 15-in-1 Dossier Report', code: 'ALL-15', desc: 'Unified single-file PDF binding all 15 documents into one complete book.', icon: FileText, tag: 'Complete' },
];

export const StepByStepWizardPage: React.FC = () => {
  const { institutionId: globalInstId, selectInstitution } = useInstitution();
  const navigate = useNavigate();

  const [currentStep, setCurrentStep] = useState<number>(1);
  const [generating, setGenerating] = useState<boolean>(false);
  const [error, setError] = useState<string>('');
  const [generationResult, setGenerationResult] = useState<any>(null);

  // Form State with high-clarity defaults
  const [formData, setFormData] = useState({
    institution_id: globalInstId || 1,

    // Step 1: Student Particulars
    full_name: '',
    father_mother_name: '',
    dob: '2004-05-15',
    gender: 'Male',
    mobile: '9829012345',
    email: '',
    address: 'Near SP Office, Bharatpur (Raj.)',
    city: 'Bharatpur',
    state: 'Rajasthan',
    college_name: 'Poddar College, Bharatpur',
    degree: 'BCA',
    branch: 'Computer Science',
    semester_year: '6th Semester',
    academic_session: '2025-2026',

    // Step 2: Course, Track & Faculty Selection
    course_track: 'DA',
    include_faculty: false,
    custom_faculty_name: '',
    custom_faculty_designation: 'Faculty Guide',
    start_date: '2026-06-01',
    end_date: '2026-07-12',
    custom_project_title: '',

    // Step 3: Attendance & Logbook Configuration
    attendance_preset: '100', // '100', '95', '90', '85'

    // Step 4: Mentor Evaluation & Compliance
    evaluation_score: 94,
    mentor_remarks: 'Demonstrated exemplary technical aptitude, consistency, and professional work ethic throughout the 6-week internship.'
  });

  // Preview Modal for individual files
  const [previewDocType, setPreviewDocType] = useState<string | null>(null);

  // Sync with global institution context changes
  useEffect(() => {
    if (globalInstId && globalInstId !== formData.institution_id) {
      handleInstitutionChange(globalInstId);
    }
  }, [globalInstId]);

  // Ensure course track matches active institution
  useEffect(() => {
    if (formData.institution_id === 2 && !formData.course_track.startsWith('SOL-')) {
      setFormData(prev => ({
        ...prev,
        course_track: 'SOL-01',
        college_name: 'Poswal Developers Training Division, Bharatpur',
        degree: 'Diploma / B.Tech (Solar & Electrical)',
        branch: 'Solar PV Systems & Grid-Tied Technology',
        address: '214, Bapu Nagar, Ghana Road, Bharatpur (Raj.) 321001',
        city: 'Bharatpur'
      }));
    } else if (formData.institution_id === 3 && formData.course_track.startsWith('SOL-')) {
      setFormData(prev => ({
        ...prev,
        course_track: 'DA',
        college_name: 'Technoglobe Center of Excellence, Jaipur',
        degree: 'BCA / B.Tech (IT)',
        branch: 'Computer Science & Engineering',
        address: 'Plot No. 4, Gopalpura Bypass Road, Jaipur (Raj.) 302018',
        city: 'Jaipur'
      }));
    } else if (formData.institution_id === 1 && formData.course_track.startsWith('SOL-')) {
      setFormData(prev => ({
        ...prev,
        course_track: 'DA',
        college_name: 'Poddar College, Bharatpur',
        degree: 'BCA',
        branch: 'Computer Science',
        address: 'Near SP Office, Bharatpur (Raj.)',
        city: 'Bharatpur'
      }));
    }
  }, [formData.institution_id]);

  const handleInstitutionChange = (instId: number) => {
    selectInstitution(instId);
    setFormData(prev => ({
      ...prev,
      institution_id: instId,
      college_name: instId === 2 ? 'Poswal Developers Training Division, Bharatpur' : (instId === 3 ? 'Technoglobe Center of Excellence, Jaipur' : 'Poddar College, Bharatpur'),
      degree: instId === 2 ? 'Diploma / B.Tech (Solar & Electrical)' : 'BCA',
      branch: instId === 2 ? 'Solar Energy Systems' : 'Computer Science',
      address: instId === 2 ? '214, Bapu Nagar, Ghana Road, Bharatpur (Raj.) 321001' : (instId === 3 ? 'Plot No. 4, Gopalpura Bypass Road, Jaipur (Raj.)' : 'Near SP Office, Bharatpur (Raj.)'),
      city: instId === 3 ? 'Jaipur' : 'Bharatpur',
      course_track: instId === 2 ? 'SOL-01' : 'DA',
      custom_faculty_name: instId === 2 ? 'Mahesh Chand Saini' : '',
      custom_faculty_designation: instId === 2 ? 'Trainer' : 'Faculty Guide',
      include_faculty: instId === 2
    }));
  };

  const handleFillPoddarSample = () => {
    handleInstitutionChange(1);
    setFormData(prev => ({
      ...prev,
      institution_id: 1,
      full_name: 'Sneha Agarwal',
      father_mother_name: 'Sh. Nitin Agarwal',
      dob: '2004-03-20',
      gender: 'Female',
      mobile: '9414293370',
      email: 'sneha.agarwal@example.com',
      address: 'Near SP Office, Bharatpur (Raj.)',
      city: 'Bharatpur',
      state: 'Rajasthan',
      college_name: 'Poddar College, Bharatpur',
      degree: 'BCA',
      branch: 'Computer Science',
      semester_year: '6th Semester',
      academic_session: '2025-2026',
      course_track: 'DA',
      include_faculty: false,
      custom_faculty_name: '',
      start_date: '2026-06-01',
      end_date: '2026-07-12',
      custom_project_title: 'Retail Sales Performance & Customer Churn Analytics Dashboard',
      attendance_preset: '100',
      evaluation_score: 96,
      mentor_remarks: 'Demonstrated exemplary technical diligence, advanced SQL & Power BI analytics modeling, and outstanding project delivery.'
    }));
  };

  const handleFillPoswalSample = () => {
    handleInstitutionChange(2);
    setFormData(prev => ({
      ...prev,
      institution_id: 2,
      full_name: 'Devendra Gurjar',
      father_mother_name: 'Sh. Madhuvan Singh Gurjar',
      dob: '2003-08-14',
      gender: 'Male',
      mobile: '9414694727',
      email: 'devendra.gurjar@example.com',
      address: '214, Bapu Nagar, Ghana Road, Bharatpur (Raj.) 321001',
      city: 'Bharatpur',
      state: 'Rajasthan',
      college_name: 'Poswal Developers Training Division, Bharatpur',
      degree: 'Diploma / B.Tech (Solar & Electrical)',
      branch: 'Solar PV Systems & Grid-Tied Technology',
      semester_year: '6th Semester',
      academic_session: '2025-2026',
      course_track: 'SOL-01',
      include_faculty: true,
      custom_faculty_name: 'Mahesh Chand Saini',
      custom_faculty_designation: 'Trainer',
      start_date: '2026-06-01',
      end_date: '2026-07-12',
      custom_project_title: '50 kWp Commercial Rooftop Solar PV & Building-Integrated (BIPV) System Installation',
      attendance_preset: '100',
      evaluation_score: 95,
      mentor_remarks: 'Exhibited superior understanding of rooftop civil structural layouts, string inverter synchronization, and DISCOM electrical safety standards.'
    }));
  };

  const handleFillTechnoglobeSample = () => {
    handleInstitutionChange(3);
    setFormData(prev => ({
      ...prev,
      institution_id: 3,
      full_name: 'Vikram Singh Rathore',
      father_mother_name: 'Sh. R.S. Rathore',
      dob: '2004-02-10',
      gender: 'Male',
      mobile: '9829012345',
      email: 'vikram.rathore@example.com',
      address: 'Plot No. 4, Gopalpura Bypass Road, Jaipur (Raj.) 302018',
      city: 'Jaipur',
      state: 'Rajasthan',
      college_name: 'Technoglobe Center of Excellence, Jaipur',
      degree: 'B.Tech (Computer Science)',
      branch: 'Full Stack Software Engineering',
      semester_year: '6th Semester',
      academic_session: '2025-2026',
      course_track: 'FS',
      include_faculty: false,
      custom_faculty_name: '',
      start_date: '2026-06-01',
      end_date: '2026-07-12',
      custom_project_title: 'Enterprise Scalable Microservices Architecture with React & Node.js',
      attendance_preset: '100',
      evaluation_score: 97,
      mentor_remarks: 'Outstanding full-stack engineering proficiency, clean RESTful design, and impressive deployment speed.'
    }));
  };

  const handleGenerate = async () => {
    if (!formData.full_name.trim()) {
      setError('Please enter the Student Full Name before proceeding.');
      setCurrentStep(1);
      return;
    }
    if (!formData.father_mother_name.trim()) {
      setError("Please enter Father's / Mother's Name.");
      setCurrentStep(1);
      return;
    }

    setGenerating(true);
    setError('');
    try {
      const payload = {
        institution_id: formData.institution_id,
        full_name: formData.full_name.trim(),
        father_mother_name: formData.father_mother_name.trim(),
        dob: formData.dob,
        gender: formData.gender,
        mobile: formData.mobile.trim(),
        email: formData.email.trim() || undefined,
        address: formData.address.trim(),
        city: formData.city.trim(),
        state: formData.state.trim(),
        college_name: formData.college_name.trim(),
        degree: formData.degree.trim(),
        branch: formData.branch.trim(),
        semester_year: formData.semester_year,
        academic_session: formData.academic_session,
        course_track: formData.course_track,
        mentor_id: null,
        custom_faculty_name: formData.include_faculty && formData.custom_faculty_name.trim() ? formData.custom_faculty_name.trim() : null,
        custom_faculty_designation: formData.include_faculty ? formData.custom_faculty_designation : null,
        start_date: formData.start_date,
        end_date: formData.end_date,
        custom_project_title: formData.custom_project_title.trim() || undefined,
        attendance_preset: formData.attendance_preset,
        evaluation_score: formData.evaluation_score,
        mentor_remarks: formData.mentor_remarks
      };

      const res = await api.quickGenerateInternship(payload);
      setGenerationResult(res);
      setCurrentStep(6); // Go to final download step
    } catch (err: any) {
      setError(err.message || 'Failed to generate internship documentation.');
    } finally {
      setGenerating(false);
    }
  };

  const isPoddar = formData.institution_id === 1;
  const isPoswal = formData.institution_id === 2;
  const isTechnoglobe = formData.institution_id === 3;

  const currentTrackObj = COURSE_TRACKS.find(t => t.code === formData.course_track) || COURSE_TRACKS[0];

  const steps = [
    { num: 1, label: '1. Organization & Student', desc: 'Institute & Candidate Info' },
    { num: 2, label: '2. Course Track & Faculty', desc: 'Syllabus & Authority Sign' },
    { num: 3, label: '3. Attendance Schedule', desc: '36 Working Days Logbook' },
    { num: 4, label: '4. Capstone & Rubrics', desc: 'Project & 100-Point Score' },
    { num: 5, label: '5. Pre-Generation Review', desc: 'Review All 15 Files' },
    { num: 6, label: '6. Download Package', desc: 'ZIP & Landscape Cert' },
  ];

  const inputStyle = "w-full px-4 py-3 text-sm font-bold text-slate-900 bg-white border-2 border-slate-300 rounded-xl shadow-xs focus:border-blue-600 focus:ring-4 focus:ring-blue-100 transition-all placeholder:text-slate-400";
  const labelStyle = "block text-xs font-bold uppercase tracking-wider text-slate-800 mb-1.5";

  return (
    <div className="max-w-5xl mx-auto space-y-6 pb-16">
      {/* Top Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-blue-950 to-indigo-950 text-white p-6 sm:p-8 rounded-3xl shadow-xl border border-slate-700 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-80 h-80 bg-amber-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="relative z-10 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div className="space-y-1.5">
            <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-amber-400/20 text-amber-300 border border-amber-400/30 text-xs font-bold uppercase tracking-wider">
              <Sparkles className="w-3.5 h-3.5 text-amber-400" />
              <span>Zero-Mistake Automated Dossier Wizard</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-serif font-black tracking-tight text-white">
              Step-by-Step Internship & Certificate Generator
            </h1>
            <p className="text-xs sm:text-sm text-slate-300 max-w-2xl leading-relaxed">
              Enter candidate details once. The engine will instantly assemble and format all <b>15 official dossier documents</b>, 36-day attendance logbook, project synopsis, rubrics evaluation, and scannable certificate with authentic signatures and seals.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <button
              onClick={handleFillPoddarSample}
              className="px-3 py-2 rounded-xl bg-blue-900/60 hover:bg-blue-800 text-blue-200 border border-blue-700 text-xs font-bold transition-all cursor-pointer"
            >
              🎓 Poddar Sample
            </button>
            <button
              onClick={handleFillPoswalSample}
              className="px-3 py-2 rounded-xl bg-amber-900/60 hover:bg-amber-800 text-amber-200 border border-amber-700 text-xs font-bold transition-all cursor-pointer"
            >
              ☀️ Poswal Sample
            </button>
            <button
              onClick={handleFillTechnoglobeSample}
              className="px-3 py-2 rounded-xl bg-indigo-900/60 hover:bg-indigo-800 text-indigo-200 border border-indigo-700 text-xs font-bold transition-all cursor-pointer"
            >
              🌐 Technoglobe Sample
            </button>
          </div>
        </div>
      </div>

      {/* Enlarged Step Indicator Tabs */}
      <div className="bg-white p-3 rounded-2xl border border-slate-200 shadow-sm">
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2">
          {steps.map((s) => {
            const isDone = currentStep > s.num || (s.num === 6 && generationResult);
            const isCurrent = currentStep === s.num;
            return (
              <button
                key={s.num}
                type="button"
                onClick={() => setCurrentStep(s.num)}
                className={`p-3 rounded-xl border text-left transition-all cursor-pointer ${
                  isCurrent
                    ? 'border-blue-600 bg-blue-50/90 shadow-sm ring-2 ring-blue-500/30'
                    : isDone
                    ? 'border-emerald-200 bg-emerald-50/50 hover:border-emerald-300'
                    : 'border-slate-200 bg-slate-50/40 hover:border-slate-300'
                }`}
              >
                <div className="flex items-center space-x-2">
                  <span className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-black shrink-0 ${
                    isCurrent
                      ? 'bg-blue-600 text-white'
                      : isDone
                      ? 'bg-emerald-600 text-white'
                      : 'bg-slate-200 text-slate-700'
                  }`}>
                    {isDone ? '✓' : s.num}
                  </span>
                  <div className="min-w-0">
                    <div className={`text-xs font-bold truncate ${isCurrent ? 'text-blue-950' : 'text-slate-800'}`}>
                      {s.label.split('.')[1]}
                    </div>
                    <div className="text-[10px] text-slate-500 truncate">{s.desc}</div>
                  </div>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="p-4 rounded-xl bg-red-50 border border-red-300 text-red-800 text-xs font-bold flex items-center justify-between shadow-xs">
          <div className="flex items-center space-x-2">
            <AlertCircle className="w-5 h-5 text-red-600 shrink-0" />
            <span>{error}</span>
          </div>
          <button onClick={() => setError('')} className="text-red-700 text-xs cursor-pointer">✕</button>
        </div>
      )}

      {/* STEP 1: ORGANIZATION & STUDENT PARTICULARS */}
      {currentStep === 1 && (
        <div className="bg-white rounded-3xl border border-slate-200 p-6 sm:p-8 shadow-sm space-y-6">
          <div className="pb-4 border-b border-slate-100 flex items-center justify-between">
            <div>
              <span className="text-xs font-black uppercase tracking-wider text-blue-600">Step 1 of 6</span>
              <h2 className="text-xl font-serif font-black text-slate-900">
                Issuing Organization & Student Particulars
              </h2>
            </div>
            <span className="text-xs font-semibold text-slate-500">All fields automatically formatted</span>
          </div>

          {/* 3 Institution Cards */}
          <div>
            <label className={labelStyle}>Select Issuing Institution</label>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              {/* Poddar College */}
              <div
                onClick={() => handleInstitutionChange(1)}
                className={`p-4 rounded-2xl border-2 cursor-pointer transition-all ${
                  isPoddar 
                    ? 'border-blue-600 bg-blue-50 shadow-md ring-2 ring-blue-500/20' 
                    : 'border-slate-200 bg-slate-50/50 hover:border-slate-300'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-11 h-11 rounded-xl bg-white p-1 flex items-center justify-center border border-slate-200 shadow-2xs">
                      <img src="/poddar_logo.png" alt="Poddar Logo" className="max-h-full max-w-full object-contain" />
                    </div>
                    <div>
                      <div className="text-xs font-bold text-blue-800 flex items-center space-x-1">
                        <GraduationCap className="w-3.5 h-3.5" />
                        <span>Poddar College</span>
                      </div>
                      <div className="text-sm font-black text-slate-900">PCTM Bharatpur</div>
                    </div>
                  </div>
                  {isPoddar && <Check className="w-5 h-5 text-blue-600 shrink-0" />}
                </div>
                <div className="text-[11px] text-slate-600 mt-2">
                  Near SP Office, Bharatpur • Authority: Nitin Agarwal
                </div>
              </div>

              {/* Poswal Developers */}
              <div
                onClick={() => handleInstitutionChange(2)}
                className={`p-4 rounded-2xl border-2 cursor-pointer transition-all ${
                  isPoswal 
                    ? 'border-amber-600 bg-amber-50 shadow-md ring-2 ring-amber-500/20' 
                    : 'border-slate-200 bg-slate-50/50 hover:border-slate-300'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-11 h-11 rounded-xl bg-white p-1 flex items-center justify-center border border-slate-200 shadow-2xs">
                      <img src="/poswal_logo.png" alt="Poswal Logo" className="max-h-full max-w-full object-contain" />
                    </div>
                    <div>
                      <div className="text-xs font-bold text-amber-800 flex items-center space-x-1">
                        <Sun className="w-3.5 h-3.5" />
                        <span>Poswal Developers</span>
                      </div>
                      <div className="text-sm font-black text-slate-900">Solar Division</div>
                    </div>
                  </div>
                  {isPoswal && <Check className="w-5 h-5 text-amber-600 shrink-0" />}
                </div>
                <div className="text-[11px] text-slate-600 mt-2">
                  Ghana Road, Bharatpur • MSME & Solar Certified
                </div>
              </div>

              {/* Technoglobe Jaipur */}
              <div
                onClick={() => handleInstitutionChange(3)}
                className={`p-4 rounded-2xl border-2 cursor-pointer transition-all ${
                  isTechnoglobe 
                    ? 'border-indigo-600 bg-indigo-50 shadow-md ring-2 ring-indigo-500/20' 
                    : 'border-slate-200 bg-slate-50/50 hover:border-slate-300'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-11 h-11 rounded-xl bg-white p-1 flex items-center justify-center border border-slate-200 shadow-2xs">
                      <img src="/technoglobe_logo.png" alt="Technoglobe Logo" className="max-h-full max-w-full object-contain" />
                    </div>
                    <div>
                      <div className="text-xs font-bold text-indigo-800 flex items-center space-x-1">
                        <Globe className="w-3.5 h-3.5" />
                        <span>Technoglobe</span>
                      </div>
                      <div className="text-sm font-black text-slate-900">Jaipur Head Office</div>
                    </div>
                  </div>
                  {isTechnoglobe && <Check className="w-5 h-5 text-indigo-600 shrink-0" />}
                </div>
                <div className="text-[11px] text-slate-600 mt-2">
                  Gopalpura Bypass, Jaipur • Authority: Nitin Agarwal
                </div>
              </div>
            </div>
          </div>

          {/* Student Fields */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className={labelStyle}>Student Full Name <span className="text-red-500">*</span></label>
              <input
                type="text"
                value={formData.full_name}
                onChange={e => setFormData({ ...formData, full_name: e.target.value })}
                placeholder="e.g. Sneha Agarwal / Rohan Sharma"
                className={inputStyle}
              />
            </div>

            <div>
              <label className={labelStyle}>Father's / Mother's Name <span className="text-red-500">*</span></label>
              <input
                type="text"
                value={formData.father_mother_name}
                onChange={e => setFormData({ ...formData, father_mother_name: e.target.value })}
                placeholder="e.g. Sh. Nitin Agarwal"
                className={inputStyle}
              />
            </div>

            <div>
              <label className={labelStyle}>Date of Birth</label>
              <input
                type="date"
                value={formData.dob}
                onChange={e => setFormData({ ...formData, dob: e.target.value })}
                className={inputStyle}
              />
            </div>

            <div>
              <label className={labelStyle}>Gender</label>
              <select
                value={formData.gender}
                onChange={e => setFormData({ ...formData, gender: e.target.value })}
                className={inputStyle}
              >
                <option value="Male">Male</option>
                <option value="Female">Female</option>
                <option value="Other">Other</option>
              </select>
            </div>

            <div>
              <label className={labelStyle}>Mobile Number</label>
              <input
                type="text"
                value={formData.mobile}
                onChange={e => setFormData({ ...formData, mobile: e.target.value })}
                placeholder="e.g. 9829012345"
                className={inputStyle}
              />
            </div>

            <div>
              <label className={labelStyle}>Email Address (Optional)</label>
              <input
                type="email"
                value={formData.email}
                onChange={e => setFormData({ ...formData, email: e.target.value })}
                placeholder="e.g. student@example.com"
                className={inputStyle}
              />
            </div>

            <div>
              <label className={labelStyle}>Degree / Qualification</label>
              <input
                type="text"
                value={formData.degree}
                onChange={e => setFormData({ ...formData, degree: e.target.value })}
                placeholder="e.g. BCA / B.Tech / Diploma"
                className={inputStyle}
              />
            </div>

            <div>
              <label className={labelStyle}>Branch / Specialization</label>
              <input
                type="text"
                value={formData.branch}
                onChange={e => setFormData({ ...formData, branch: e.target.value })}
                placeholder="e.g. Computer Science / Solar PV Systems"
                className={inputStyle}
              />
            </div>
          </div>

          <div className="pt-4 border-t border-slate-100 flex justify-end">
            <button
              type="button"
              onClick={() => setCurrentStep(2)}
              className="px-6 py-3 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-sm shadow-md flex items-center space-x-2 transition-all cursor-pointer"
            >
              <span>Next: Course Track & Faculty</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* STEP 2: COURSE TRACK & OPTIONAL FACULTY */}
      {currentStep === 2 && (
        <div className="bg-white rounded-3xl border border-slate-200 p-6 sm:p-8 shadow-sm space-y-6">
          <div className="pb-4 border-b border-slate-100 flex items-center justify-between">
            <div>
              <span className="text-xs font-black uppercase tracking-wider text-blue-600">Step 2 of 6</span>
              <h2 className="text-xl font-serif font-black text-slate-900">
                Course Track & Authority Signatures
              </h2>
            </div>
            <span className="text-xs font-semibold text-slate-500">
              {isPoswal ? 'Solar & Industrial Curriculums' : 'Advanced IT Curriculums'}
            </span>
          </div>

          {/* Course Track Grid */}
          <div>
            <label className={labelStyle}>Select Specialization Track</label>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
              {COURSE_TRACKS.filter(t => isPoswal ? t.code.startsWith('SOL-') : !t.code.startsWith('SOL-')).map(t => (
                <div
                  key={t.code}
                  onClick={() => setFormData({ ...formData, course_track: t.code })}
                  className={`p-3.5 rounded-2xl border-2 cursor-pointer transition-all flex flex-col justify-between ${
                    formData.course_track === t.code
                      ? 'border-blue-600 bg-blue-50/90 shadow-md ring-2 ring-blue-500/20'
                      : 'border-slate-200 bg-slate-50/50 hover:border-slate-300'
                  }`}
                >
                  <div>
                    <div className="flex items-center justify-between mb-1.5">
                      <span className="px-2 py-0.5 rounded text-[10px] font-black bg-blue-200 text-blue-900 font-mono">
                        {t.code}
                      </span>
                      {formData.course_track === t.code && <Check className="w-4 h-4 text-blue-600" />}
                    </div>
                    <div className="text-xs font-bold text-slate-900 leading-snug">{t.title}</div>
                    <div className="text-[11px] text-slate-500 mt-1 line-clamp-2">{t.desc}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Optional Faculty Toggle / Name Input */}
          <div className="p-5 rounded-2xl bg-amber-50/70 border-2 border-amber-200 space-y-3">
            <div className="flex items-center justify-between">
              <label className="flex items-center space-x-2.5 cursor-pointer">
                <input
                  type="checkbox"
                  checked={formData.include_faculty}
                  onChange={e => setFormData({ ...formData, include_faculty: e.target.checked })}
                  className="w-5 h-5 rounded text-amber-600 focus:ring-amber-500"
                />
                <span className="text-sm font-black text-slate-900">
                  Include Faculty / Guide Signature (Optional)
                </span>
              </label>
              <span className="text-xs font-bold px-2.5 py-1 rounded-full bg-amber-200 text-amber-900">
                {formData.include_faculty ? 'Dual Signatures' : 'Single Authority: Nitin Agarwal'}
              </span>
            </div>

            {formData.include_faculty ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
                <div>
                  <label className="block text-[11px] font-bold text-slate-800 mb-1">Faculty / Guide Name</label>
                  <input
                    type="text"
                    value={formData.custom_faculty_name}
                    onChange={e => setFormData({ ...formData, custom_faculty_name: e.target.value })}
                    placeholder="e.g. Prof. Krishlay / Mahesh Chand Saini"
                    className="w-full px-3 py-2 text-xs font-bold text-slate-900 bg-white border border-amber-300 rounded-lg"
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-bold text-slate-800 mb-1">Faculty Designation</label>
                  <input
                    type="text"
                    value={formData.custom_faculty_designation}
                    onChange={e => setFormData({ ...formData, custom_faculty_designation: e.target.value })}
                    placeholder="e.g. Faculty Guide / Trainer"
                    className="w-full px-3 py-2 text-xs text-slate-900 bg-white border border-amber-300 rounded-lg"
                  />
                </div>
              </div>
            ) : (
              <p className="text-xs text-slate-700 leading-relaxed">
                ✓ <b>Faculty is optional.</b> Leaving unchecked automatically formats all certificates and 15 documents with a prominent single authority signature for <b>{isPoswal ? 'Madhuvan Singh Gurjar (Authority)' : 'Nitin Agarwal (Director / Authority)'}</b> with zero blank lines.
              </p>
            )}
          </div>

          <div className="pt-4 border-t border-slate-100 flex justify-between">
            <button
              type="button"
              onClick={() => setCurrentStep(1)}
              className="px-5 py-2.5 rounded-xl border border-slate-300 text-slate-700 font-bold text-xs hover:bg-slate-50 cursor-pointer"
            >
              Back: Student Info
            </button>
            <button
              type="button"
              onClick={() => setCurrentStep(3)}
              className="px-6 py-3 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-sm shadow-md flex items-center space-x-2 transition-all cursor-pointer"
            >
              <span>Next: Attendance & Schedule</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* STEP 3: ATTENDANCE & SCHEDULE */}
      {currentStep === 3 && (
        <div className="bg-white rounded-3xl border border-slate-200 p-6 sm:p-8 shadow-sm space-y-6">
          <div className="pb-4 border-b border-slate-100 flex items-center justify-between">
            <div>
              <span className="text-xs font-black uppercase tracking-wider text-blue-600">Step 3 of 6</span>
              <h2 className="text-xl font-serif font-black text-slate-900">
                Training Dates & 36-Day Attendance Preset
              </h2>
            </div>
            <span className="text-xs font-semibold text-slate-500">Auto-calculated 36 Working Days</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className={labelStyle}>Internship Start Date</label>
              <input
                type="date"
                value={formData.start_date}
                onChange={e => setFormData({ ...formData, start_date: e.target.value })}
                className={inputStyle}
              />
            </div>

            <div>
              <label className={labelStyle}>Internship End Date</label>
              <input
                type="date"
                value={formData.end_date}
                onChange={e => setFormData({ ...formData, end_date: e.target.value })}
                className={inputStyle}
              />
            </div>
          </div>

          <div>
            <label className={labelStyle}>Attendance Percentage Preset</label>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              {[
                { val: '100', label: '100% Exemplary', desc: '36/36 Days Present' },
                { val: '95', label: '95% Outstanding', desc: '34 Present, 2 Leaves' },
                { val: '90', label: '90% Very Good', desc: '32 Present, 4 Leaves' },
                { val: '85', label: '85% Good', desc: '30 Present, 6 Leaves' },
              ].map(p => (
                <div
                  key={p.val}
                  onClick={() => setFormData({ ...formData, attendance_preset: p.val })}
                  className={`p-3.5 rounded-2xl border-2 cursor-pointer transition-all text-center ${
                    formData.attendance_preset === p.val
                      ? 'border-emerald-600 bg-emerald-50 shadow-md ring-2 ring-emerald-500/20'
                      : 'border-slate-200 bg-slate-50/50 hover:border-slate-300'
                  }`}
                >
                  <div className="text-base font-black text-slate-900">{p.label}</div>
                  <div className="text-xs text-slate-500 mt-0.5">{p.desc}</div>
                </div>
              ))}
            </div>
          </div>

          <div className="p-4 rounded-2xl bg-blue-50 border border-blue-200 text-xs text-blue-900 space-y-1">
            <div className="font-bold flex items-center space-x-1.5">
              <CheckCircle2 className="w-4 h-4 text-blue-600" />
              <span>Automatic 36 Working Days Logbook Generation</span>
            </div>
            <p className="text-blue-800">
              Sundays are omitted automatically. Daily logbook entries, weekly summaries, and topic coverage for <b>{currentTrackObj.title}</b> will be filled seamlessly.
            </p>
          </div>

          <div className="pt-4 border-t border-slate-100 flex justify-between">
            <button
              type="button"
              onClick={() => setCurrentStep(2)}
              className="px-5 py-2.5 rounded-xl border border-slate-300 text-slate-700 font-bold text-xs hover:bg-slate-50 cursor-pointer"
            >
              Back: Course Track
            </button>
            <button
              type="button"
              onClick={() => setCurrentStep(4)}
              className="px-6 py-3 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-sm shadow-md flex items-center space-x-2 transition-all cursor-pointer"
            >
              <span>Next: Capstone & Rubrics</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* STEP 4: CAPSTONE PROJECT & MENTOR RUBRICS */}
      {currentStep === 4 && (
        <div className="bg-white rounded-3xl border border-slate-200 p-6 sm:p-8 shadow-sm space-y-6">
          <div className="pb-4 border-b border-slate-100 flex items-center justify-between">
            <div>
              <span className="text-xs font-black uppercase tracking-wider text-blue-600">Step 4 of 6</span>
              <h2 className="text-xl font-serif font-black text-slate-900">
                Capstone Project & Mentor Appraisal
              </h2>
            </div>
            <span className="text-xs font-semibold text-slate-500">100-Point Grading Rubrics</span>
          </div>

          <div className="space-y-4">
            <div>
              <label className={labelStyle}>Capstone Project Title</label>
              <input
                type="text"
                value={formData.custom_project_title || currentTrackObj.project}
                onChange={e => setFormData({ ...formData, custom_project_title: e.target.value })}
                placeholder="e.g. Retail Sales Analytics & Predictive Dashboard"
                className={inputStyle}
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className={labelStyle}>Overall Evaluation Score (0 - 100)</label>
                <input
                  type="number"
                  min="50"
                  max="100"
                  value={formData.evaluation_score}
                  onChange={e => setFormData({ ...formData, evaluation_score: Number(e.target.value) })}
                  className={inputStyle}
                />
              </div>

              <div>
                <label className={labelStyle}>Grade Band</label>
                <div className="px-4 py-3 bg-slate-50 rounded-xl border border-slate-300 font-bold text-sm text-slate-800 flex items-center justify-between">
                  <span>
                    {formData.evaluation_score >= 90 ? 'Grade A+ (Outstanding)' : formData.evaluation_score >= 80 ? 'Grade A (Excellent)' : 'Grade B+ (Good)'}
                  </span>
                  <span className="text-xs text-emerald-700 bg-emerald-100 px-2 py-0.5 rounded-md">Verified</span>
                </div>
              </div>
            </div>

            <div>
              <label className={labelStyle}>Mentor Remarks / Recommendation</label>
              <textarea
                rows={3}
                value={formData.mentor_remarks}
                onChange={e => setFormData({ ...formData, mentor_remarks: e.target.value })}
                className="w-full px-4 py-3 text-xs font-medium text-slate-900 bg-white border-2 border-slate-300 rounded-xl focus:border-blue-600 resize-none leading-relaxed"
              />
            </div>
          </div>

          <div className="pt-4 border-t border-slate-100 flex justify-between">
            <button
              type="button"
              onClick={() => setCurrentStep(3)}
              className="px-5 py-2.5 rounded-xl border border-slate-300 text-slate-700 font-bold text-xs hover:bg-slate-50 cursor-pointer"
            >
              Back: Attendance
            </button>
            <button
              type="button"
              onClick={() => setCurrentStep(5)}
              className="px-6 py-3 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-sm shadow-md flex items-center space-x-2 transition-all cursor-pointer"
            >
              <span>Next: Review All 15 Files</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* STEP 5: PRE-GENERATION 15-DOCUMENT REVIEW SCREEN */}
      {currentStep === 5 && (
        <div className="bg-white rounded-3xl border border-slate-200 p-6 sm:p-8 shadow-sm space-y-6">
          <div className="pb-4 border-b border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-blue-100 text-blue-800 text-xs font-bold uppercase tracking-wider mb-1">
                <Eye className="w-3.5 h-3.5 text-blue-600" />
                <span>Pre-Generation Audit & Review</span>
              </div>
              <h2 className="text-xl font-serif font-black text-slate-900">
                Review All 15 Official Files Before Issuance
              </h2>
              <p className="text-xs text-slate-500 mt-0.5">
                Inspect every document in the dossier. Click any card to preview its layout or jump back to edit details.
              </p>
            </div>

            <button
              type="button"
              onClick={handleGenerate}
              disabled={generating || !formData.full_name.trim()}
              className="px-6 py-3.5 rounded-2xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-black text-sm shadow-lg shadow-emerald-600/20 flex items-center space-x-2 cursor-pointer transition-all disabled:opacity-50"
            >
              {generating ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Processing Dossier...</span>
                </>
              ) : (
                <>
                  <Wand2 className="w-4 h-4 text-amber-300" />
                  <span>Generate All 15 Files & Certificate</span>
                </>
              )}
            </button>
          </div>

          {/* Candidate Dossier Summary Card */}
          <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200 grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
            <div>
              <span className="text-slate-400 block uppercase font-bold text-[10px]">Candidate</span>
              <span className="font-bold text-slate-900 text-sm">{formData.full_name || 'Sneha Agarwal'}</span>
            </div>
            <div>
              <span className="text-slate-400 block uppercase font-bold text-[10px]">Institution</span>
              <span className="font-bold text-slate-900">{isPoswal ? 'Poswal Developers' : (isTechnoglobe ? 'Technoglobe Jaipur' : 'Poddar College')}</span>
            </div>
            <div>
              <span className="text-slate-400 block uppercase font-bold text-[10px]">Track</span>
              <span className="font-bold text-slate-900">{currentTrackObj.badge}</span>
            </div>
            <div>
              <span className="text-slate-400 block uppercase font-bold text-[10px]">Signatory</span>
              <span className="font-bold text-slate-900">
                {formData.include_faculty ? `${formData.custom_faculty_name} + Authority` : 'Authority Only (Nitin Agarwal)'}
              </span>
            </div>
          </div>

          {/* 15 Files Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3.5">
            {DOSSIER_FILES_15.map((file) => {
              const Icon = file.icon;
              return (
                <div
                  key={file.id}
                  className="p-4 rounded-2xl border-2 border-slate-200 hover:border-blue-400 bg-white hover:bg-blue-50/30 transition-all flex flex-col justify-between group shadow-xs"
                >
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="px-2 py-0.5 rounded text-[10px] font-black bg-slate-100 group-hover:bg-blue-100 text-slate-800 group-hover:text-blue-900 font-mono">
                        {file.code}
                      </span>
                      <span className="text-[10px] font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full">
                        {file.tag}
                      </span>
                    </div>
                    <div className="text-xs font-bold text-slate-900 group-hover:text-blue-900">
                      {file.name}
                    </div>
                    <p className="text-[11px] text-slate-500 mt-1 leading-relaxed line-clamp-2">
                      {file.desc}
                    </p>
                  </div>

                  <div className="mt-3 pt-2.5 border-t border-slate-100 flex items-center justify-between text-[11px]">
                    <span className="text-slate-400 font-mono">Ready to emit</span>
                    <button
                      type="button"
                      onClick={() => setPreviewDocType(file.id)}
                      className="inline-flex items-center space-x-1 text-blue-600 hover:text-blue-800 font-bold cursor-pointer"
                    >
                      <Eye className="w-3.5 h-3.5" />
                      <span>Preview</span>
                    </button>
                  </div>
                </div>
              );
            })}
          </div>

          <div className="pt-4 border-t border-slate-100 flex justify-between">
            <button
              type="button"
              onClick={() => setCurrentStep(4)}
              className="px-5 py-2.5 rounded-xl border border-slate-300 text-slate-700 font-bold text-xs hover:bg-slate-50 cursor-pointer"
            >
              Back: Capstone & Rubrics
            </button>
            <button
              type="button"
              onClick={handleGenerate}
              disabled={generating || !formData.full_name.trim()}
              className="px-8 py-3.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-sm shadow-md flex items-center space-x-2 transition-all cursor-pointer disabled:opacity-50"
            >
              <span>{generating ? 'Emitting Package...' : 'Final Step: Generate & Download'}</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* STEP 6: FINAL GENERATION & INSTANT DOWNLOADS */}
      {currentStep === 6 && (
        <div className="bg-white rounded-3xl border border-slate-200 p-6 sm:p-8 shadow-sm space-y-6">
          <div className="text-center space-y-2 py-2">
            <div className="w-16 h-16 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center mx-auto shadow-sm">
              <CheckCircle2 className="w-10 h-10" />
            </div>
            <h2 className="text-2xl font-serif font-black text-slate-900">
              15-Document Internship Dossier Generated Successfully!
            </h2>
            <p className="text-xs sm:text-sm text-slate-600 max-w-xl mx-auto">
              Candidate record for <b>{formData.full_name}</b> has been compiled and saved with official certificate number and cryptographic QR code.
            </p>
          </div>

          {/* Primary Action Buttons */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {/* 1. Complete Package ZIP */}
            <a
              href={generationResult ? generationResult.zip_url : '#'}
              target="_blank"
              rel="noreferrer"
              className="p-5 rounded-2xl bg-gradient-to-br from-blue-700 to-indigo-800 text-white shadow-lg hover:shadow-xl hover:from-blue-600 hover:to-indigo-700 transition-all flex flex-col justify-between cursor-pointer group"
            >
              <div>
                <div className="w-10 h-10 rounded-xl bg-white/20 flex items-center justify-center mb-3">
                  <Download className="w-5 h-5 text-white" />
                </div>
                <div className="text-base font-black">Download Complete ZIP Package</div>
                <div className="text-xs text-blue-100 mt-1">All 15 individual PDF documents bundled in 1 ZIP.</div>
              </div>
              <div className="mt-4 pt-3 border-t border-white/20 flex items-center justify-between text-xs font-bold text-amber-300">
                <span>1-Click ZIP Download</span>
                <span>→</span>
              </div>
            </a>

            {/* 2. Landscape Certificate PDF */}
            <a
              href={generationResult ? generationResult.cert_pdf_url : '#'}
              target="_blank"
              rel="noreferrer"
              className="p-5 rounded-2xl bg-gradient-to-br from-amber-500 to-amber-600 text-slate-950 shadow-lg hover:shadow-xl hover:from-amber-400 hover:to-amber-500 transition-all flex flex-col justify-between cursor-pointer group"
            >
              <div>
                <div className="w-10 h-10 rounded-xl bg-black/10 flex items-center justify-center mb-3">
                  <Award className="w-5 h-5 text-slate-950" />
                </div>
                <div className="text-base font-black">Print Completion Certificate</div>
                <div className="text-xs text-slate-900 mt-1">A4 landscape vector PDF with scannable QR and stamp.</div>
              </div>
              <div className="mt-4 pt-3 border-t border-black/10 flex items-center justify-between text-xs font-black">
                <span>Vector Certificate PDF</span>
                <span>→</span>
              </div>
            </a>

            {/* 3. Consolidated 15-in-1 Report */}
            <a
              href={generationResult ? generationResult.report_pdf_url : '#'}
              target="_blank"
              rel="noreferrer"
              className="p-5 rounded-2xl bg-gradient-to-br from-slate-900 to-slate-800 text-white shadow-lg hover:shadow-xl hover:from-slate-800 hover:to-slate-700 transition-all flex flex-col justify-between cursor-pointer group"
            >
              <div>
                <div className="w-10 h-10 rounded-xl bg-white/10 flex items-center justify-center mb-3">
                  <FileText className="w-5 h-5 text-white" />
                </div>
                <div className="text-base font-black">Unified 15-in-1 Dossier</div>
                <div className="text-xs text-slate-300 mt-1">Consolidated single PDF file binding all 15 reports.</div>
              </div>
              <div className="mt-4 pt-3 border-t border-white/20 flex items-center justify-between text-xs font-bold text-amber-400">
                <span>Unified Dossier PDF</span>
                <span>→</span>
              </div>
            </a>
          </div>

          {/* Individual Document Quick Downloads Table */}
          <div className="pt-4 border-t border-slate-100">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-3">
              Individual Document PDF Downloads
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
              {DOSSIER_FILES_15.map((file) => {
                const intId = generationResult?.internship_id;
                const pdfUrl = intId ? api.getDocumentPdfUrl(intId, file.id) : '#';
                return (
                  <div key={file.id} className="p-2.5 rounded-xl border border-slate-200 bg-slate-50/50 flex items-center justify-between text-xs">
                    <span className="font-semibold text-slate-800 truncate mr-2">{file.name}</span>
                    <a
                      href={pdfUrl}
                      target="_blank"
                      rel="noreferrer"
                      className="px-2.5 py-1 rounded bg-blue-600 hover:bg-blue-500 text-white font-bold text-[11px] shrink-0"
                    >
                      PDF
                    </a>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="pt-4 border-t border-slate-100 flex justify-between">
            <button
              type="button"
              onClick={() => {
                setGenerationResult(null);
                setCurrentStep(1);
              }}
              className="px-5 py-2.5 rounded-xl border border-slate-300 text-slate-700 font-bold text-xs hover:bg-slate-50 cursor-pointer"
            >
              Generate Another Student
            </button>
            <Link
              to="/students"
              className="px-6 py-2.5 rounded-xl bg-slate-900 text-white font-bold text-xs hover:bg-slate-800"
            >
              View in Student Directory →
            </Link>
          </div>
        </div>
      )}

      {/* Live Preview Modal */}
      {previewDocType && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-xs p-4">
          <div className="bg-white rounded-3xl max-w-2xl w-full p-6 shadow-2xl space-y-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <h3 className="text-base font-bold text-slate-900">
                Document Preview: {DOSSIER_FILES_15.find(f => f.id === previewDocType)?.name}
              </h3>
              <button onClick={() => setPreviewDocType(null)} className="p-1.5 rounded-lg hover:bg-slate-100 text-slate-500 cursor-pointer">
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="p-6 bg-slate-50 rounded-2xl border border-slate-200 text-center space-y-3">
              <FileText className="w-12 h-12 text-blue-600 mx-auto" />
              <div className="text-sm font-bold text-slate-900">
                {DOSSIER_FILES_15.find(f => f.id === previewDocType)?.name}
              </div>
              <p className="text-xs text-slate-600 max-w-md mx-auto">
                {DOSSIER_FILES_15.find(f => f.id === previewDocType)?.desc}
              </p>
              <div className="p-3 bg-white rounded-xl border border-slate-200 text-xs text-slate-700 text-left space-y-1">
                <div><b>Candidate:</b> {formData.full_name || 'Sneha Agarwal'}</div>
                <div><b>Institution:</b> {isPoswal ? 'Poswal Developers' : (isTechnoglobe ? 'Technoglobe Jaipur' : 'Poddar College')}</div>
                <div><b>Track:</b> {currentTrackObj.title}</div>
                <div><b>Dates:</b> {formData.start_date} to {formData.end_date} (36 Working Days)</div>
              </div>
            </div>
            <div className="flex justify-end space-x-2">
              <button
                onClick={() => setPreviewDocType(null)}
                className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold rounded-xl cursor-pointer"
              >
                Close Preview
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default StepByStepWizardPage;
