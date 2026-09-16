import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { 
  Wand2, CheckCircle2, ArrowRight, ArrowLeft, Download, 
  FileText, Award, Calendar, BookOpen, ShieldCheck, UserCheck, 
  GraduationCap, AlertCircle, RefreshCw, Printer, Sparkles, Building2
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
    defaultMentor: 1
  },
  {
    code: 'SOL-02',
    institutionId: 2,
    title: 'Solar Structure Fitting, Panel Mounting & Civil Layout',
    badge: 'Structure Fitting',
    desc: 'Hot-dip galvanized (HDG) mounting structure assembly, tilt angle optimization, torque specifications, foundation civil work, wind-load anchoring, and module stringing.',
    project: '100 kWp Ground-Mounted Fixed-Tilt Solar Array Structural Layout & Alignment',
    color: 'orange',
    defaultMentor: 1
  },
  {
    code: 'SOL-03',
    institutionId: 2,
    title: 'Solar Electrical Systems, Inverters & Grid-Tied Technology',
    badge: 'Electrical & Inverter',
    desc: 'String & central inverters, MPPT tracking, DC/AC distribution boxes, SPD surge protection, AC combiner boxes, LT panel integration, and grid synchronization.',
    project: 'Grid-Connected 25 kW Solar Inverter & Net-Metering Synchronization Facility',
    color: 'yellow',
    defaultMentor: 1
  },
  {
    code: 'SOL-04',
    institutionId: 2,
    title: 'Industrial Solar Power Plant Operations & Maintenance (O&M)',
    badge: 'Industrial Solar O&M',
    desc: 'Thermal imaging inspections, IV-curve tracing, degradation analysis, soiling loss mitigation, SCADA telemetry monitoring, and preventive maintenance protocols.',
    project: 'Preventive O&M Audit & SCADA Telemetry Protocol for 500 kWp Industrial Plant',
    color: 'emerald',
    defaultMentor: 1
  },
  {
    code: 'SOL-05',
    institutionId: 2,
    title: 'Solar Water Heating & Agricultural Pumping Systems',
    badge: 'Pumps & Thermal',
    desc: 'Evacuated tube collectors (ETC), flat plate collectors (FPC), solar VFD pump controllers, brushless DC surface/submersible pumps, and piping layout.',
    project: '7.5 HP Solar Agricultural Irrigation Pumping & Micro-Grid Distribution',
    color: 'teal',
    defaultMentor: 1
  },
  {
    code: 'SOL-06',
    institutionId: 2,
    title: 'Off-Grid Solar Energy Storage & Battery Management (BMS)',
    badge: 'Storage & Batteries',
    desc: 'Lithium iron phosphate (LiFePO4) & tubular lead-acid batteries, hybrid inverters, DoD optimization, charge controllers (PWM/MPPT), and battery safety.',
    project: 'Hybrid 10 kVA Off-Grid Solar Energy Storage & Battery Management Facility',
    color: 'sky',
    defaultMentor: 1
  },
  {
    code: 'SOL-07',
    institutionId: 2,
    title: 'Solar PV System Design, Load Estimation & PVsyst Simulation',
    badge: 'PVsyst Design',
    desc: 'Solar irradiance modeling, PVsyst & HelioScope simulation, energy yield forecasting, loss diagram assessment, single-line diagram (SLD), and BOM estimation.',
    project: 'Comprehensive Techno-Economic PVsyst Simulation for 100 kWp Rooftop System',
    color: 'indigo',
    defaultMentor: 1
  },
  {
    code: 'SOL-08',
    institutionId: 2,
    title: 'Solar Safety Standards, Electrical Earthing & Net-Metering',
    badge: 'Safety & Metering',
    desc: 'Chemical earthing pits, copper strip bonded grounding, lightning arrestor (ESE) design, DISCOM net-metering protocols, and IEC/IS compliance documentation.',
    project: 'High-Integrity Earthing Grid & DISCOM Net-Metering Compliance Architecture',
    color: 'rose',
    defaultMentor: 1
  },

  // --- Poddar College Tracks (Academic & Professional IT) ---
  {
    code: 'DA',
    institutionId: 1,
    title: 'Data Analytics & Business Intelligence',
    badge: 'Python & Power BI',
    desc: 'Python, Pandas, NumPy, SQL, Power BI, Advanced Excel, Data Cleaning, and Executive Reporting.',
    project: 'Retail Sales & Customer Churn Predictive Dashboard',
    color: 'blue',
    defaultMentor: 2
  },
  {
    code: 'DM',
    institutionId: 1,
    title: 'Digital Marketing & Growth Strategy',
    badge: 'SEO, Ads & GA4',
    desc: 'SEO, Social Media, Google Ads, Meta Ads, GA4 Web Analytics, Copywriting & AI Content Workflows.',
    project: 'Omnichannel Healthcare Clinic Growth & Lead Generation Campaign',
    color: 'purple',
    defaultMentor: 3
  },
  {
    code: 'FS',
    institutionId: 1,
    title: 'Full Stack Web Development (MERN)',
    badge: 'React & Node.js',
    desc: 'React.js 18, Node.js, Express.js, MongoDB Atlas, TypeScript, Tailwind CSS, REST APIs & Cloud Deployment.',
    project: 'Cloud Patient Consultation & Health Records Management Portal',
    color: 'emerald',
    defaultMentor: 2
  },
  {
    code: 'AI',
    institutionId: 1,
    title: 'Python AI, ML & Data Science',
    badge: 'ML & Deep Learning',
    desc: 'Python 3.11, Scikit-Learn, TensorFlow, XGBoost, Predictive Modeling, EDA & FastAPI Deployment.',
    project: 'Clinical Disease Risk & Patient Prognosis Prediction System',
    color: 'indigo',
    defaultMentor: 2
  },
  {
    code: 'CS',
    institutionId: 1,
    title: 'Cyber Security & Defensive Ops',
    badge: 'Security & VAPT',
    desc: 'Kali Linux, Wireshark, Burp Suite, Network Sniffing, Vulnerability Assessment, Cryptography & Defensive Hardening.',
    project: 'Enterprise Vulnerability Assessment & Defensive Threat Mitigation',
    color: 'rose',
    defaultMentor: 3
  },
  {
    code: 'CC',
    institutionId: 1,
    title: 'Cloud Computing & DevOps Architecture',
    badge: 'AWS, Docker & K8s',
    desc: 'AWS EC2/VPC/S3, Docker Containerization, Kubernetes Orchestration, GitHub Actions CI/CD & Terraform IaC.',
    project: 'Multi-Tier Cloud Infrastructure Deployment with Docker & CI/CD',
    color: 'sky',
    defaultMentor: 2
  },
  {
    code: 'JV',
    institutionId: 1,
    title: 'Java Enterprise & Spring Boot Development',
    badge: 'Spring Boot & JPA',
    desc: 'Java 17/21 LTS, Spring Boot 3, Spring Data JPA, Hibernate, MySQL, Spring Security & Microservice APIs.',
    project: 'Enterprise Banking & Financial Transaction Microservices Platform',
    color: 'amber',
    defaultMentor: 2
  },
  {
    code: 'BI',
    institutionId: 1,
    title: 'Bioinformatics & Computational Biology',
    badge: 'Genomics & PyMOL',
    desc: 'BioPython, Pairwise/MSA Alignment, BLAST+, NCBI Entrez APIs, Protein Structure Visualization & Genomic Data.',
    project: 'Computational Genomic Mutation Profiling & Protein Homology Modeling',
    color: 'teal',
    defaultMentor: 2
  },
  {
    code: 'AD',
    institutionId: 1,
    title: 'Android Mobile App Development (Kotlin)',
    badge: 'Kotlin & Compose',
    desc: 'Kotlin 1.9, Jetpack Compose, Material 3, Room SQLite Database, Retrofit 2, Coroutines, Flow & MVVM Architecture.',
    project: 'Modern Telemedicine Consultation & Health Tracking Android App',
    color: 'violet',
    defaultMentor: 3
  }
];

const FACULTY_MEMBERS = [
  {
    id: 1,
    institutionId: 2,
    name: 'Mahesh Chand Saini',
    designation: 'Trainer',
    department: 'Solar Power & Industrial Engineering Division (Poswal Developers)',
    avatar: 'MS',
    color: 'amber'
  },
  {
    id: 2,
    institutionId: 1,
    name: 'Krishlay',
    designation: 'Faculty',
    department: 'Department of Computing, Data Science & AI (Poddar College)',
    avatar: 'KS',
    color: 'blue'
  },
  {
    id: 3,
    institutionId: 1,
    name: 'Rahul',
    designation: 'Faculty',
    department: 'Department of Digital Technologies & Web Engineering (Poddar College)',
    avatar: 'RB',
    color: 'purple'
  }
];

const INSTITUTIONS = [
  {
    id: 1,
    code: 'PODDAR',
    name: 'Poddar College',
    fullName: 'Poddar College of Technology & Management',
    subTitle: 'Department of Technical & Higher Education (Academic & Professional Credential)',
    location: 'Bharatpur, Rajasthan | Phone: 9414293370 | Email: nitin@pctm',
    badge: 'Poddar College Bharatpur',
    stampType: 'Empty Box for Physical Ink Stamping',
    watermarkType: 'Poddar College Logo Watermark',
    authority: 'Nitin Agarwal (Authority)',
    prefix: 'PCTM',
    logo: '/poddar_logo.png',
    borderSelected: 'border-indigo-600 ring-2 ring-indigo-500/20 bg-indigo-50/70',
    badgeClass: 'bg-indigo-100 text-indigo-900 border-indigo-200'
  },
  {
    id: 2,
    code: 'POSWAL',
    name: 'Poswal Developers',
    fullName: 'Poswal Developers',
    subTitle: 'Solar Power Generation & Industrial Infrastructure Training',
    location: '214, Bapu Nagar, Ghana Road, Bharatpur (Raj.) | Mob: 9414694727',
    badge: 'GST: 08ABIFP2454N1ZQ | MSME: UDYAM-RJ-06-0052498',
    stampType: 'Empty Box for Physical Ink Stamping',
    watermarkType: 'Poswal Developers Logo Watermark',
    authority: 'Madhuvan Singh Gurjar (Authority)',
    prefix: 'POSWAL',
    logo: '/poswal_logo.png',
    borderSelected: 'border-amber-600 ring-2 ring-amber-500/20 bg-amber-50/70',
    badgeClass: 'bg-amber-100 text-amber-900 border-amber-200'
  }
];

export const StepByStepWizardPage: React.FC = () => {
  const { institutionId: globalInstId, selectInstitution } = useInstitution();
  const [currentStep, setCurrentStep] = useState<number>(1);
  const [generating, setGenerating] = useState<boolean>(false);
  const [error, setError] = useState<string>('');
  const [generationResult, setGenerationResult] = useState<any>(null);

  // Form State with Sensible Autofill Defaults
  const [formData, setFormData] = useState({
    // Organization Selection: 1 = Poddar College, 2 = Poswal Developers
    institution_id: globalInstId || 1,

    // Step 1: Student Information
    full_name: '',
    father_mother_name: '',
    dob: '2004-05-15',
    gender: 'Male',
    mobile: '9829012345',
    email: '',
    address: 'Poddar College Campus, Bharatpur',
    city: 'Bharatpur',
    state: 'Rajasthan',
    college_name: 'Poddar College, Bharatpur',
    degree: 'BCA',
    branch: 'Computer Science',
    semester_year: '6th Semester',
    academic_session: '2025-2026',

    // Step 2: Course & Track Selection & Faculty
    course_track: 'DA',
    mentor_id: 2,
    start_date: '2026-06-01',
    end_date: '2026-07-12',
    custom_project_title: '',

    // Step 3: Attendance & Logbook Configuration
    attendance_preset: '100', // '100', '95', '90', '85'

    // Step 4: Mentor Evaluation & Compliance
    evaluation_score: 94,
    mentor_remarks: 'Demonstrated exemplary technical aptitude, consistency, and professional work ethic throughout the 6-week internship.'
  });

  // Auto-Save and Restore Draft from localStorage
  React.useEffect(() => {
    const saved = localStorage.getItem('wizard_form_draft');
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        if (parsed && parsed.full_name) {
          setFormData((prev) => ({ ...prev, ...parsed }));
        }
      } catch {}
    }
  }, []);

  React.useEffect(() => {
    if (formData.full_name) {
      localStorage.setItem('wizard_form_draft', JSON.stringify(formData));
    }
  }, [formData]);

  // Sync with global institution context changes
  React.useEffect(() => {
    if (globalInstId && globalInstId !== formData.institution_id) {
      handleInstitutionChange(globalInstId);
    }
  }, [globalInstId]);

  // Ensure course_track strictly matches active institution
  React.useEffect(() => {
    if (formData.institution_id === 2 && !formData.course_track.startsWith('SOL-')) {
      setFormData(prev => ({
        ...prev,
        course_track: 'SOL-01',
        mentor_id: 1,
        college_name: 'Poswal Developers Training Division, Bharatpur',
        degree: 'Diploma / B.Tech (Solar & Electrical)',
        branch: 'Solar PV Systems & Grid-Tied Technology'
      }));
    } else if (formData.institution_id === 1 && formData.course_track.startsWith('SOL-')) {
      setFormData(prev => ({
        ...prev,
        course_track: 'DA',
        mentor_id: 2,
        college_name: 'Poddar College, Bharatpur',
        degree: 'BCA',
        branch: 'Computer Science'
      }));
    }
  }, [formData.institution_id, formData.course_track]);

  const toTitleCase = (str: string) => {
    return str.replace(/\w\S*/g, (txt) => txt.charAt(0).toUpperCase() + txt.substring(1).toLowerCase());
  };

  const handleFillPoddarSample = () => {
    handleInstitutionChange(1);
    setFormData((prev) => ({
      ...prev,
      institution_id: 1,
      full_name: 'Sneha Agarwal',
      father_mother_name: 'Sh. Nitin Agarwal',
      dob: '2004-03-20',
      gender: 'Female',
      mobile: '9414293370',
      email: 'sneha.agarwal@example.com',
      address: 'Poddar College Campus, Bharatpur',
      city: 'Bharatpur',
      state: 'Rajasthan',
      college_name: 'Poddar College, Bharatpur',
      degree: 'BCA',
      branch: 'Computer Science',
      semester_year: '6th Semester',
      academic_session: '2025-2026',
      course_track: 'DA',
      mentor_id: 2,
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
    setFormData((prev) => ({
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
      mentor_id: 1,
      start_date: '2026-06-01',
      end_date: '2026-07-12',
      custom_project_title: '50 kWp Commercial Rooftop Solar PV & Building-Integrated (BIPV) System Installation',
      attendance_preset: '100',
      evaluation_score: 95,
      mentor_remarks: 'Exhibited superior understanding of rooftop civil structural layouts, string inverter synchronization, and DISCOM electrical safety standards.'
    }));
  };

  const handleResetForm = () => {
    localStorage.removeItem('wizard_form_draft');
    setFormData({
      institution_id: globalInstId || 1,
      full_name: '',
      father_mother_name: '',
      dob: '2004-05-15',
      gender: 'Male',
      mobile: '9829012345',
      email: '',
      address: 'Poddar College Campus, Bharatpur',
      city: 'Bharatpur',
      state: 'Rajasthan',
      college_name: 'Poddar College, Bharatpur',
      degree: 'BCA',
      branch: 'Computer Science',
      semester_year: '6th Semester',
      academic_session: '2025-2026',
      course_track: 'DA',
      mentor_id: 2,
      start_date: '2026-06-01',
      end_date: '2026-07-12',
      custom_project_title: '',
      attendance_preset: '100',
      evaluation_score: 94,
      mentor_remarks: 'Demonstrated exemplary technical aptitude, consistency, and professional work ethic throughout the 6-week internship.'
    });
  };

    const handleInstitutionChange = (instId: number) => {
    selectInstitution(instId);
    setFormData((prev) => ({
      ...prev,
      institution_id: instId,
      college_name: instId === 2 ? 'Poswal Developers Training Division' : 'Poddar College, Bharatpur',
      degree: instId === 2 ? 'Diploma / B.Tech (Solar & Electrical)' : 'BCA',
      branch: instId === 2 ? 'Solar Energy Systems' : 'Computer Science',
      address: instId === 2 ? '214, Bapu Nagar, Ghana Road, Bharatpur (Raj.)' : 'Poddar College Campus, Bharatpur',
      course_track: instId === 2 ? 'SOL-01' : 'DA',
      mentor_id: instId === 2 ? 1 : 2
    }));
  };

  const handleTrackChange = (trackCode: string) => {
    const trackObj = COURSE_TRACKS.find(t => t.code === trackCode);
    setFormData((prev) => ({
      ...prev,
      course_track: trackCode,
      mentor_id: trackObj ? trackObj.defaultMentor : prev.mentor_id,
      custom_project_title: ''
    }));
  };

  const handleMentorChange = (mentorId: number) => {
    setFormData((prev) => ({
      ...prev,
      mentor_id: mentorId
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

    const mobileDigits = formData.mobile.replace(/\D/g, '');
    if (mobileDigits.length < 10) {
      setError('Mobile number must be at least 10 digits.');
      setCurrentStep(1);
      return;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (formData.email && !emailRegex.test(formData.email)) {
      setError('Please enter a valid email address.');
      setCurrentStep(1);
      return;
    }

    if (new Date(formData.start_date) >= new Date(formData.end_date)) {
      setError('Start date must be before end date.');
      setCurrentStep(2);
      return;
    }

    if (formData.evaluation_score < 0 || formData.evaluation_score > 100) {
      setError('Evaluation score must be between 0 and 100.');
      setCurrentStep(4);
      return;
    }

    setGenerating(true);
    setError('');
    try {
      const res = await api.quickGenerateInternship({
        ...formData,
        mentor_id: formData.mentor_id,
        full_name: formData.full_name.trim(),
        father_mother_name: formData.father_mother_name.trim()
      });
      setGenerationResult(res);
      setCurrentStep(5); // Jump to download step
    } catch (err: any) {
      setError(err.message || 'Failed to generate internship documentation.');
    } finally {
      setGenerating(false);
    }
  };

  // High-Contrast, Large, Highly Legible Input Style
  const inputStyle = "w-full px-4 py-3 text-base font-semibold text-slate-950 bg-white border-2 border-slate-300 rounded-lg shadow-xs focus:border-blue-600 focus:ring-3 focus:ring-blue-100 transition-all placeholder:text-slate-400";
  const labelStyle = "block text-sm font-bold text-slate-900 mb-1.5";

  const steps = [
    { num: 1, label: 'Student Info', desc: 'Name & Academics' },
    { num: 2, label: 'Course Track', desc: '9 Tracks & Faculty' },
    { num: 3, label: 'Attendance', desc: '36-Day Logbook' },
    { num: 4, label: 'Evaluation', desc: 'Rubric & Compliance' },
    { num: 5, label: 'Download', desc: 'ZIP & All 15 PDFs' },
  ];

  return (
    <div className="max-w-5xl mx-auto space-y-6 pb-12">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-blue-900 via-brand-900 to-indigo-900 text-white p-6 rounded-2xl shadow-md border border-blue-800">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-blue-500/20 text-blue-200 border border-blue-400/30 text-xs font-bold uppercase tracking-wider">
              <Sparkles className="w-3.5 h-3.5 text-amber-300" />
              <span>Zero-Mistake Automated Documentation</span>
            </div>
            <h1 className="text-2xl font-bold tracking-tight text-white flex items-center space-x-3">
              <span>Step-by-Step Internship Generator</span>
            </h1>
            <p className="text-sm text-blue-100/90 max-w-2xl leading-relaxed">
              Enter student particulars once. Everything else (attendance, 36 daily logs, 6 weekly reviews, capstone project, mentor rubric, and offline JSON certificate) is <b>100% automatically generated</b> with official franchise standards.
            </p>
          </div>

          <div className="flex items-center space-x-3 shrink-0">
            {currentStep < 5 && (
              <button
                type="button"
                onClick={handleGenerate}
                disabled={generating || !formData.full_name.trim()}
                className="px-5 py-3 rounded-xl bg-amber-400 hover:bg-amber-300 text-slate-950 font-bold text-sm shadow-md transition-all flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
              >
                {generating ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    <span>Generating Documentation...</span>
                  </>
                ) : (
                  <>
                    <Wand2 className="w-4 h-4 text-slate-950" />
                    <span>Quick Generate Now</span>
                  </>
                )}
              </button>
            )}
          </div>
        </div>

        {/* Live Typing Confirmation Badge */}
        {formData.full_name && (
          <div className="mt-4 pt-4 border-t border-blue-800/80 flex items-center space-x-2 text-xs text-blue-100">
            <span className="font-semibold text-amber-300 uppercase tracking-wide">Candidate being prepared:</span>
            <span className="bg-white text-slate-900 px-3 py-1 rounded-md font-bold text-sm shadow-xs">
              {formData.full_name.toUpperCase()}
            </span>
            <span className="text-blue-200">
              ({formData.degree} in {formData.branch} • {formData.course_track === 'DA' ? 'Data Analytics' : 'Digital Marketing'})
            </span>
          </div>
        )}
      </div>

      {/* Stepper Navigation */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-2xs">
        <div className="grid grid-cols-5 gap-2">
          {steps.map((s) => {
            const isDone = currentStep > s.num || (s.num === 5 && generationResult);
            const isCurrent = currentStep === s.num;
            return (
              <button
                key={s.num}
                type="button"
                onClick={() => {
                  if (s.num < currentStep || generationResult) {
                    setCurrentStep(s.num);
                  }
                }}
                className={`flex flex-col items-center p-2 rounded-lg text-center transition-all ${
                  isCurrent
                    ? 'bg-blue-50 border-2 border-blue-600 text-blue-900 shadow-xs'
                    : isDone
                    ? 'bg-emerald-50 text-emerald-800 hover:bg-emerald-100/70 border border-emerald-200'
                    : 'bg-slate-50 text-slate-400 border border-slate-200 cursor-not-allowed'
                }`}
              >
                <div className="flex items-center space-x-1.5 mb-1">
                  <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${
                    isCurrent ? 'bg-blue-600 text-white' : isDone ? 'bg-emerald-600 text-white' : 'bg-slate-300 text-slate-600'
                  }`}>
                    {isDone ? <CheckCircle2 className="w-4 h-4" /> : s.num}
                  </div>
                  <span className="text-xs font-bold">{s.label}</span>
                </div>
                <span className="text-[10px] hidden md:block text-slate-500 font-medium">
                  {s.desc}
                </span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="p-4 rounded-xl bg-red-50 border-2 border-red-300 text-red-900 text-sm flex items-center space-x-3 shadow-xs">
          <AlertCircle className="w-5 h-5 text-red-600 shrink-0" />
          <div className="font-semibold">{error}</div>
        </div>
      )}

      {/* STEP 1: Student Information */}
      {currentStep === 1 && (
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-6 animate-in fade-in">
          <div className="border-b border-slate-200 pb-3 flex items-center justify-between">
            <div>
              <h2 className="text-lg font-bold text-slate-900 flex items-center space-x-2">
                <span className="w-7 h-7 rounded-full bg-blue-600 text-white flex items-center justify-center text-xs font-bold">1</span>
                <span>Select Organization & Enter Student Information</span>
              </h2>
              <p className="text-xs text-slate-500 mt-0.5">
                Choose between Poddar College or Poswal Developers (Direct Credential), then enter student particulars.
              </p>
            </div>
            <span className="text-xs font-bold px-3 py-1 rounded-full bg-blue-100 text-blue-800">
              Autofill Active
            </span>
          </div>

          {/* Quick 1-Click Preset Bar for Zero-Effort Generation */}
          <div className="bg-linear-to-r from-amber-500/15 via-blue-500/10 to-indigo-500/15 border border-amber-300/80 rounded-2xl p-4 flex flex-col sm:flex-row items-center justify-between gap-3 shadow-xs">
            <div className="flex items-center space-x-2.5">
              <div className="w-8 h-8 rounded-lg bg-amber-400 text-slate-950 flex items-center justify-center shrink-0 font-bold">
                ⚡
              </div>
              <div className="text-left">
                <span className="text-xs font-bold text-slate-900 block">Quick 1-Click Autofill Presets</span>
                <span className="text-[11px] text-slate-600">Populate realistic test candidate particulars instantly</span>
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-2">
              <button
                type="button"
                onClick={handleFillPoddarSample}
                className="px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold shadow-xs transition-transform active:scale-95 cursor-pointer flex items-center space-x-1"
              >
                <span>🎓 Fill Poddar BCA</span>
              </button>
              <button
                type="button"
                onClick={handleFillPoswalSample}
                className="px-3 py-1.5 rounded-lg bg-amber-500 hover:bg-amber-400 text-slate-950 text-xs font-bold shadow-xs transition-transform active:scale-95 cursor-pointer flex items-center space-x-1"
              >
                <span>☀️ Fill Poswal Solar</span>
              </button>
              <button
                type="button"
                onClick={handleResetForm}
                className="px-2.5 py-1.5 rounded-lg bg-slate-200 hover:bg-slate-300 text-slate-700 text-xs font-semibold transition-colors cursor-pointer"
                title="Reset Form to Defaults"
              >
                Reset
              </button>
            </div>
          </div>

          {/* Organization / Institution Selector Cards */}
          <div className="space-y-2">
            <label className="block text-xs font-extrabold uppercase tracking-wider text-slate-700">
              Issuing Organization / Institution Profile *
            </label>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {INSTITUTIONS.map((inst) => {
                const isSelected = formData.institution_id === inst.id;
                return (
                  <div
                    key={inst.id}
                    onClick={() => handleInstitutionChange(inst.id)}
                    className={`p-4 rounded-xl border-2 transition-all cursor-pointer flex flex-col justify-between space-y-3 ${
                      isSelected
                        ? inst.borderSelected + ' shadow-xs'
                        : 'border-slate-200 bg-white hover:border-slate-300 hover:bg-slate-50/50'
                    }`}
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex items-center space-x-3">
                        <div className="w-12 h-12 rounded-lg bg-white border border-slate-200 p-1.5 flex items-center justify-center shrink-0 shadow-2xs">
                          <img
                            src={inst.logo}
                            alt={inst.name}
                            className="max-h-full max-w-full object-contain"
                          />
                        </div>
                        <div>
                          <div className="flex items-center space-x-2">
                            <h3 className="font-bold text-slate-950 text-base">{inst.name}</h3>
                            <span className={`text-[10px] font-extrabold px-2 py-0.5 rounded-full border ${inst.badgeClass}`}>
                              {inst.code}
                            </span>
                          </div>
                          <p className="text-xs text-slate-600 font-medium leading-snug">{inst.subTitle}</p>
                        </div>
                      </div>
                      <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center shrink-0 mt-1 ${
                        isSelected ? 'border-blue-600 bg-blue-600 text-white' : 'border-slate-300'
                      }`}>
                        {isSelected && <div className="w-2 h-2 rounded-full bg-white" />}
                      </div>
                    </div>

                    <div className="pt-2 border-t border-slate-200/80 grid grid-cols-2 gap-2 text-[11px] text-slate-600">
                      <div>
                        <span className="text-slate-400 block text-[9px] uppercase font-bold">Stamp Style</span>
                        <span className="font-semibold text-slate-800">{inst.stampType}</span>
                      </div>
                      <div>
                        <span className="text-slate-400 block text-[9px] uppercase font-bold">Watermark</span>
                        <span className="font-semibold text-slate-800">{inst.watermarkType}</span>
                      </div>
                      <div>
                        <span className="text-slate-400 block text-[9px] uppercase font-bold">Authority</span>
                        <span className="font-semibold text-slate-800">{inst.authority}</span>
                      </div>
                      <div>
                        <span className="text-slate-400 block text-[9px] uppercase font-bold">Cert Prefix</span>
                        <span className="font-mono font-bold text-brand-700">{inst.prefix}</span>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-5 pt-2">
            {/* Full Name */}
            <div>
              <label className={labelStyle}>
                Student Full Name (as per matriculation) *
              </label>
              <input
                type="text"
                required
                value={formData.full_name}
                onChange={(e) => {
                  setError('');
                  setFormData({ ...formData, full_name: e.target.value });
                }}
                onBlur={(e) => {
                  if (e.target.value) {
                    setFormData({ ...formData, full_name: toTitleCase(e.target.value) });
                  }
                }}
                placeholder="Type full name, e.g. Rohan Sharma"
                className={`${inputStyle} ring-2 ring-blue-500/20`}
                autoFocus
              />
              {formData.full_name && (
                <p className="text-xs font-bold text-emerald-700 mt-1 flex items-center space-x-1">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>Typed: {formData.full_name}</span>
                </p>
              )}
            </div>

            {/* Father's / Mother's Name */}
            <div>
              <label className={labelStyle}>
                Father's / Mother's Name *
              </label>
              <input
                type="text"
                required
                value={formData.father_mother_name}
                onChange={(e) => setFormData({ ...formData, father_mother_name: e.target.value })}
                placeholder="e.g. Sh. Rakesh Sharma"
                className={inputStyle}
              />
            </div>

            {/* Mobile */}
            <div>
              <label className={labelStyle}>Mobile Number</label>
              <input
                type="tel"
                value={formData.mobile}
                onChange={(e) => setFormData({ ...formData, mobile: e.target.value })}
                placeholder="e.g. 9829012345"
                className={inputStyle}
              />
            </div>

            {/* Email */}
            <div>
              <label className={labelStyle}>Email ID (Optional - auto-generated if empty)</label>
              <input
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                placeholder={formData.full_name ? `${formData.full_name.toLowerCase().replace(/\s+/g, '.')}@example.com` : 'student@example.com'}
                className={inputStyle}
              />
            </div>


          </div>

          <div className="pt-4 border-t border-slate-200 flex items-center justify-between">
            <div className="text-xs text-slate-500 font-medium">
              Step 1 of 4: All fields above are pre-configured with sensible defaults.
            </div>
            <button
              type="button"
              onClick={() => {
                if (!formData.full_name.trim()) {
                  setError('Please enter Candidate Name.');
                  return;
                }
                setError('');
                setCurrentStep(2);
              }}
              className="px-6 py-3 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-sm shadow-md transition-all flex items-center space-x-2 cursor-pointer"
            >
              <span>Next: Choose Course Track</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* STEP 2: Course & Track Selection */}
      {currentStep === 2 && (
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-6 animate-in fade-in">
          <div className="border-b border-slate-200 pb-3 flex items-center justify-between">
            <div>
              <h2 className="text-lg font-bold text-slate-900 flex items-center space-x-2">
                <span className="w-7 h-7 rounded-full bg-blue-600 text-white flex items-center justify-center text-xs font-bold">2</span>
                <span>Select Course Track & Supervising Faculty</span>
              </h2>
              <p className="text-xs text-slate-500 mt-0.5">
                Select from 9 industry tracks. The approved curriculum, duration (6 weeks / 126 hours), daily syllabus, and 28-page capstone dissertation will be dynamically generated.
              </p>
            </div>
          </div>

          {/* 9 Visual Cards for Track Selection */}
          <div>
            <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
              Choose Internship Specialization Track (9 Tracks Available):
            </label>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3.5">
              {COURSE_TRACKS.filter(t => t.institutionId === formData.institution_id).map((track) => {
                const isSelected = formData.course_track === track.code;
                return (
                  <div
                    key={track.code}
                    onClick={() => handleTrackChange(track.code)}
                    className={`p-4 rounded-xl border-2 cursor-pointer transition-all flex flex-col justify-between ${
                      isSelected
                        ? 'border-blue-600 bg-blue-50/70 shadow-md ring-2 ring-blue-600/30'
                        : 'border-slate-200 bg-white hover:border-slate-300 hover:bg-slate-50/50'
                    }`}
                  >
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <span className={`px-2 py-0.5 rounded-md text-xs font-extrabold uppercase ${
                          isSelected ? 'bg-blue-600 text-white' : 'bg-slate-200 text-slate-800'
                        }`}>
                          {track.code}
                        </span>
                        <span className="text-[10px] font-bold text-blue-700 bg-blue-100/70 px-2 py-0.5 rounded-full">
                          {track.badge}
                        </span>
                      </div>
                      <h3 className="text-sm font-bold text-slate-950 mb-1 leading-snug">
                        {track.title}
                      </h3>
                      <p className="text-[11px] text-slate-600 mb-2 leading-relaxed line-clamp-2">
                        {track.desc}
                      </p>
                    </div>

                    <div className="text-[10px] text-slate-700 bg-white/90 p-2 rounded-lg border border-slate-200/80 space-y-0.5 mt-1">
                      <div className="truncate"><b>Project:</b> {track.project}</div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Supervising Faculty Mentor Selection */}
          <div className="pt-2 border-t border-slate-200">
            <div className="flex items-center justify-between mb-2">
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider">
                Supervising Faculty Mentor (Will Sign All 15 Documents & 28-Page Report):
              </label>
              <span className="text-[11px] text-slate-500 font-medium">
                {formData.institution_id === 2 ? 'Authority: Madhuvan Singh Gurjar (Authority & Authorized Signatory)' : 'Authority: Nitin Agarwal (Authority & Authorized Signatory)'}
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {FACULTY_MEMBERS.filter(f => f.institutionId === formData.institution_id).map((faculty) => {
                const isSelected = formData.mentor_id === faculty.id;
                return (
                  <div
                    key={faculty.id}
                    onClick={() => handleMentorChange(faculty.id)}
                    className={`p-4 rounded-xl border-2 cursor-pointer transition-all flex items-start space-x-3 ${
                      isSelected
                        ? 'border-blue-600 bg-blue-50/70 shadow-md ring-2 ring-blue-600/30'
                        : 'border-slate-200 bg-white hover:border-slate-300'
                    }`}
                  >
                    <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold text-sm text-white shrink-0 ${
                      faculty.id === 1 ? 'bg-blue-600' : 'bg-purple-600'
                    }`}>
                      {faculty.avatar}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <h4 className="text-sm font-bold text-slate-950 truncate">
                          {faculty.name}
                        </h4>
                        {isSelected && (
                          <span className="px-2 py-0.5 rounded-full bg-blue-600 text-white text-[10px] font-bold flex items-center space-x-1 shrink-0">
                            <CheckCircle2 className="w-3 h-3" />
                            <span>Assigned</span>
                          </span>
                        )}
                      </div>
                      <p className="text-xs font-semibold text-slate-700">{faculty.designation}</p>
                      <p className="text-[11px] text-slate-500 truncate">{faculty.department}</p>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Dates & Optional Project Title */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-5 pt-2 border-t border-slate-200">
            <div>
              <label className={labelStyle}>Start Date</label>
              <input
                type="date"
                value={formData.start_date}
                onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
                className={inputStyle}
              />
            </div>
            <div>
              <label className={labelStyle}>End Date</label>
              <input
                type="date"
                value={formData.end_date}
                onChange={(e) => setFormData({ ...formData, end_date: e.target.value })}
                className={inputStyle}
              />
            </div>
            <div>
              <label className={labelStyle}>Custom Project Title (Optional)</label>
              <input
                type="text"
                value={formData.custom_project_title}
                onChange={(e) => setFormData({ ...formData, custom_project_title: e.target.value })}
                placeholder="Leave blank for standard approved project"
                className={inputStyle}
              />
            </div>
          </div>

          <div className="pt-4 border-t border-slate-200 flex items-center justify-between">
            <button
              type="button"
              onClick={() => setCurrentStep(1)}
              className="px-5 py-2.5 rounded-xl border border-slate-300 text-slate-700 font-bold text-sm hover:bg-slate-100 transition-all flex items-center space-x-2"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>Back</span>
            </button>
            <button
              type="button"
              onClick={() => setCurrentStep(3)}
              className="px-6 py-3 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-sm shadow-md transition-all flex items-center space-x-2 cursor-pointer"
            >
              <span>Next: Attendance & Logbook</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* STEP 3: Attendance & Logbook */}
      {currentStep === 3 && (
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-6 animate-in fade-in">
          <div className="border-b border-slate-200 pb-3 flex items-center justify-between">
            <div>
              <h2 className="text-lg font-bold text-slate-900 flex items-center space-x-2">
                <span className="w-7 h-7 rounded-full bg-blue-600 text-white flex items-center justify-center text-xs font-bold">3</span>
                <span>Attendance & Daily Logbook Preset</span>
              </h2>
              <p className="text-xs text-slate-500 mt-0.5">
                Configure attendance rate. All 36 daily sessions and 6 weekly reviews will be generated automatically based on curriculum modules.
              </p>
            </div>
          </div>

          {/* Preset Buttons */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { val: '100', label: '100% Present', days: '36/36 Days', hrs: '126 Hours', tag: 'Perfect Attendance (Recommended)' },
              { val: '95', label: '95% Present', days: '34/36 Days', hrs: '119 Hours', tag: '2 Approved Leaves' },
              { val: '90', label: '90% Present', days: '32/36 Days', hrs: '112 Hours', tag: '4 Approved Leaves' },
              { val: '85', label: '85% Present', days: '31/36 Days', hrs: '108.5 Hours', tag: '5 Approved Leaves' },
            ].map((p) => (
              <div
                key={p.val}
                onClick={() => setFormData({ ...formData, attendance_preset: p.val })}
                className={`p-4 rounded-xl border-2 cursor-pointer text-center transition-all ${
                  formData.attendance_preset === p.val
                    ? 'border-blue-600 bg-blue-50/70 shadow-sm ring-2 ring-blue-600/30 font-bold'
                    : 'border-slate-200 bg-white hover:border-slate-300'
                }`}
              >
                <div className="text-base font-bold text-slate-900">{p.label}</div>
                <div className="text-xs text-blue-700 font-semibold mt-0.5">{p.days} • {p.hrs}</div>
                <div className="text-[10px] text-slate-500 mt-1">{p.tag}</div>
              </div>
            ))}
          </div>

          {/* Summary Box */}
          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-2 text-xs text-slate-700">
            <div className="font-bold text-slate-900 text-sm flex items-center space-x-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              <span>Attendance & Logbook Automation Details:</span>
            </div>
            <ul className="list-disc list-inside space-y-1 text-slate-600">
              <li>36 working days generated (Mon–Sat, skipping Sundays) between {formData.start_date} and {formData.end_date}.</li>
              <li>Daily session timings: 10:00 AM to 01:30 PM (3.5 hours per day).</li>
              <li>Every day has its corresponding curriculum module topic, practical activity, tools used, and mentor sign-off.</li>
              <li>6 Weekly Progress Reports (Weeks 1 to 6) automatically formulated with syllabus review milestones.</li>
              <li>Physical stamp and signature areas remain blank for genuine ink signing.</li>
            </ul>
          </div>

          <div className="pt-4 border-t border-slate-200 flex items-center justify-between">
            <button
              type="button"
              onClick={() => setCurrentStep(2)}
              className="px-5 py-2.5 rounded-xl border border-slate-300 text-slate-700 font-bold text-sm hover:bg-slate-100 transition-all flex items-center space-x-2"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>Back</span>
            </button>
            <button
              type="button"
              onClick={() => setCurrentStep(4)}
              className="px-6 py-3 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-sm shadow-md transition-all flex items-center space-x-2 cursor-pointer"
            >
              <span>Next: Mentor Evaluation & Compliance</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* STEP 4: Mentor Evaluation & Compliance */}
      {currentStep === 4 && (
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-6 animate-in fade-in">
          <div className="border-b border-slate-200 pb-3 flex items-center justify-between">
            <div>
              <h2 className="text-lg font-bold text-slate-900 flex items-center space-x-2">
                <span className="w-7 h-7 rounded-full bg-blue-600 text-white flex items-center justify-center text-xs font-bold">4</span>
                <span>Mentor Evaluation & Institutional Compliance</span>
              </h2>
              <p className="text-xs text-slate-500 mt-0.5">
                Rubric assessment and college compliance approval are pre-configured for immediate certificate issuance.
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            <div>
              <label className={labelStyle}>Mentor Evaluation Score (out of 100)</label>
              <div className="flex items-center space-x-3">
                <input
                  type="number"
                  min="60"
                  max="100"
                  value={formData.evaluation_score}
                  onChange={(e) => setFormData({ ...formData, evaluation_score: Number(e.target.value) })}
                  className={inputStyle}
                />
                <span className="text-sm font-bold text-emerald-700 bg-emerald-50 px-3 py-3 rounded-lg border border-emerald-200 whitespace-nowrap">
                  {formData.evaluation_score >= 90 ? 'Grade A+ (Exemplary)' :
                   formData.evaluation_score >= 80 ? 'Grade A (Excellent)' :
                   formData.evaluation_score >= 70 ? 'Grade B+ (Very Good)' :
                   formData.evaluation_score >= 60 ? 'Grade B (Good)' :
                   formData.evaluation_score >= 50 ? 'Grade C (Satisfactory)' :
                   'Grade D (Needs Improvement)'}
                </span>
              </div>
              <p className="text-xs text-slate-500 mt-1">
                9 criteria (Technical Knowledge, Application, Problem Solving, Work Quality, etc.) scored automatically.
              </p>
            </div>

            <div>
              <label className={labelStyle}>Institutional Compliance Status</label>
              <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-lg text-emerald-900 text-sm font-semibold flex items-center space-x-2">
                <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" />
                <span>
                  APPROVED by {formData.institution_id === 2 ? 'Poswal Developers (Ref: POSWAL/BPT/2026/088)' : 'Poddar College, Bharatpur (Ref: PC/INT/2026/042)'}
                </span>
              </div>
              <p className="text-xs text-slate-500 mt-1">
                {formData.institution_id === 2
                  ? 'Authority: Madhuvan Singh Gurjar. Trainer: Mahesh Chand Saini. Designated ink-stamp box provided for physical stamping.'
                  : 'Authority: Nitin Agarwal. Designated ink-stamp box provided for physical college stamping.'}
              </p>
            </div>

            <div className="md:col-span-2">
              <label className={labelStyle}>Mentor Assessment Remarks</label>
              <textarea
                rows={2}
                value={formData.mentor_remarks}
                onChange={(e) => setFormData({ ...formData, mentor_remarks: e.target.value })}
                className={inputStyle}
              />
            </div>
          </div>

          <div className="pt-4 border-t border-slate-200 flex items-center justify-between">
            <button
              type="button"
              onClick={() => setCurrentStep(3)}
              className="px-5 py-2.5 rounded-xl border border-slate-300 text-slate-700 font-bold text-sm hover:bg-slate-100 transition-all flex items-center space-x-2"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>Back</span>
            </button>
            <button
              type="button"
              onClick={handleGenerate}
              disabled={generating}
              className="px-8 py-3.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-base shadow-lg transition-all flex items-center space-x-2 cursor-pointer"
            >
              {generating ? (
                <>
                  <RefreshCw className="w-5 h-5 animate-spin" />
                  <span>Generating All 15 Documents...</span>
                </>
              ) : (
                <>
                  <Wand2 className="w-5 h-5" />
                  <span>Generate All 15 Documents & Certificate Now</span>
                </>
              )}
            </button>
          </div>
        </div>
      )}

      {/* STEP 5: Review & Download Everything */}
      {currentStep === 5 && generationResult && (
        <div className="bg-white p-6 rounded-2xl border-2 border-emerald-300 shadow-lg space-y-6 animate-in zoom-in-95 duration-200">
          {/* Success Banner */}
          <div className="p-6 rounded-2xl bg-gradient-to-r from-emerald-600 to-teal-700 text-white flex flex-col md:flex-row items-start md:items-center justify-between gap-4 shadow-md">
            <div className="space-y-1">
              <div className="inline-flex items-center space-x-1.5 px-3 py-0.5 rounded-full bg-emerald-800/60 text-emerald-100 text-xs font-bold uppercase tracking-wider">
                <CheckCircle2 className="w-4 h-4 text-emerald-300" />
                <span>
                  {generationResult.institution_name || (formData.institution_id === 2 ? 'Poswal Developers' : 'Poddar College')} — Package Complete & Verified
                </span>
              </div>
              <h2 className="text-2xl font-bold">
                Internship Package Ready for {generationResult.student_name}
              </h2>
              <p className="text-xs text-emerald-100">
                Certificate Number: <b>{generationResult.certificate_number}</b> • Verification Code: <b>{generationResult.verification_code}</b>
              </p>
            </div>

            <a
              href={generationResult.zip_url}
              download
              className="px-6 py-3.5 rounded-xl bg-white text-emerald-900 font-extrabold text-sm shadow-md hover:bg-emerald-50 transition-all flex items-center space-x-2 shrink-0 cursor-pointer"
            >
              <Download className="w-5 h-5 text-emerald-700" />
              <span>DOWNLOAD COMPLETE PACKAGE (.ZIP)</span>
            </a>
          </div>

          {/* Quick Metrics */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 text-center">
              <div className="text-xs text-slate-500 font-semibold">Course Track</div>
              <div className="text-sm font-bold text-slate-900 mt-1">{generationResult.course_name}</div>
            </div>
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 text-center">
              <div className="text-xs text-slate-500 font-semibold">Attendance Achieved</div>
              <div className="text-sm font-bold text-emerald-700 mt-1">{generationResult.attendance_pct}% (36 Days)</div>
            </div>
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 text-center">
              <div className="text-xs text-slate-500 font-semibold">Total Hours</div>
              <div className="text-sm font-bold text-blue-700 mt-1">{generationResult.total_hours} Hours</div>
            </div>
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 text-center">
              <div className="text-xs text-slate-500 font-semibold">Offline QR Code</div>
              <div className="text-sm font-bold text-purple-700 mt-1">100% Self-Contained</div>
            </div>
          </div>

          {/* Key Documents Grid */}
          <div className="space-y-3">
            <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider">
              Download Key Documents Individually:
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* Certificate */}
              <div className="p-4 rounded-xl border border-blue-200 bg-blue-50/50 flex flex-col justify-between space-y-3">
                <div className="flex items-start space-x-3">
                  <Award className="w-6 h-6 text-blue-700 shrink-0 mt-0.5" />
                  <div>
                    <h4 className="text-sm font-bold text-slate-950">Completion Certificate</h4>
                    <p className="text-[11px] text-slate-600">A4 Landscape with Guilloche border and self-contained JSON QR code.</p>
                  </div>
                </div>
                <a
                  href={generationResult.cert_pdf_url}
                  download
                  className="w-full py-2 px-3 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs flex items-center justify-center space-x-2"
                >
                  <Download className="w-3.5 h-3.5" />
                  <span>Download Certificate (PDF)</span>
                </a>
              </div>

              {/* Consolidated Report */}
              <div className="p-4 rounded-xl border border-purple-200 bg-purple-50/50 flex flex-col justify-between space-y-3">
                <div className="flex items-start space-x-3">
                  <BookOpen className="w-6 h-6 text-purple-700 shrink-0 mt-0.5" />
                  <div>
                    <h4 className="text-sm font-bold text-slate-950">Complete Academic Report</h4>
                    <p className="text-[11px] text-slate-600">25+ page bound university report with all chapters and declarations.</p>
                  </div>
                </div>
                <a
                  href={generationResult.report_pdf_url}
                  download
                  className="w-full py-2 px-3 rounded-lg bg-purple-600 hover:bg-purple-700 text-white font-bold text-xs flex items-center justify-center space-x-2"
                >
                  <Download className="w-3.5 h-3.5" />
                  <span>Download Academic Report (PDF)</span>
                </a>
              </div>

              {/* 50/50 Live Editor */}
              <div className="p-4 rounded-xl border border-slate-200 bg-slate-50 flex flex-col justify-between space-y-3">
                <div className="flex items-start space-x-3">
                  <FileText className="w-6 h-6 text-slate-700 shrink-0 mt-0.5" />
                  <div>
                    <h4 className="text-sm font-bold text-slate-950">Live Document Preview</h4>
                    <p className="text-[11px] text-slate-600">Open in the 50/50 live editor to preview paper styling and print.</p>
                  </div>
                </div>
                <Link
                  to={`/document-editor?student_id=${generationResult.student_id}&doc=certificate`}
                  className="w-full py-2 px-3 rounded-lg bg-slate-800 hover:bg-slate-900 text-white font-bold text-xs flex items-center justify-center space-x-2"
                >
                  <span>Open 50/50 Live Editor</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            </div>
          </div>

          {/* All 15 Documents Download List */}
          <div className="space-y-2 pt-2">
            <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider">
              All 15 Official Generated Documents (Contained in ZIP):
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-2 text-xs">
              {[
                { name: '01_Offer_Letter.pdf', key: 'offer' },
                { name: '02_Joining_Letter.pdf', key: 'joining' },
                { name: '03_Course_Syllabus.pdf', key: 'syllabus' },
                { name: '04_Training_Schedule.pdf', key: 'schedule' },
                { name: '05_Attendance_Sheet.pdf', key: 'attendance_sheet' },
                { name: '06_Attendance_Summary.pdf', key: 'attendance_summary' },
                { name: '07_Daily_Logbook.pdf', key: 'daily_log' },
                { name: '08_Weekly_Progress_Report.pdf', key: 'weekly_report' },
                { name: '09_Project_Assignment.pdf', key: 'project_assignment' },
                { name: '10_Project_Report.pdf', key: 'project_report' },
                { name: '11_Mentor_Evaluation.pdf', key: 'evaluation' },
                { name: '12_Performance_Report.pdf', key: 'performance' },
                { name: '13_Student_Feedback.pdf', key: 'feedback' },
                { name: '14_Internship_Completion_Certificate.pdf', key: 'certificate' },
                { name: '15_Experience_Training_Certificate.pdf', key: 'experience' },
              ].map((doc) => (
                <a
                  key={doc.key}
                  href={`/api/documents/${generationResult.internship_id}/${doc.key}/pdf`}
                  download
                  className="p-2 rounded-lg bg-white border border-slate-200 hover:border-blue-400 text-slate-800 flex items-center justify-between hover:bg-blue-50/50 transition-all font-medium"
                >
                  <span className="truncate">{doc.name}</span>
                  <Download className="w-3.5 h-3.5 text-slate-400 shrink-0 ml-1" />
                </a>
              ))}
            </div>
          </div>

          {/* Action Buttons */}
          <div className="pt-4 border-t border-slate-200 flex flex-wrap items-center justify-between gap-3">
            <button
              type="button"
              onClick={() => {
                setGenerationResult(null);
                setFormData({
                  ...formData,
                  full_name: '',
                  father_mother_name: '',
                  mobile: '9829012345',
                  email: '',
                  custom_project_title: ''
                });
                setCurrentStep(1);
              }}
              className="px-5 py-2.5 rounded-xl border-2 border-slate-300 text-slate-700 font-bold text-xs hover:bg-slate-100 transition-all flex items-center space-x-2"
            >
              <RefreshCw className="w-4 h-4" />
              <span>Generate for Another Student</span>
            </button>

            <Link
              to={`/students/${generationResult.student_id}`}
              className="px-5 py-2.5 rounded-xl bg-blue-50 text-blue-700 border border-blue-200 font-bold text-xs hover:bg-blue-100 transition-all flex items-center space-x-2"
            >
              <span>View Full Student Dossier</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      )}
    </div>
  );
};
