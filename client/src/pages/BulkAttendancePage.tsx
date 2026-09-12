import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  Users, Calendar, Clock, Download, FileText, CheckCircle2, 
  Sparkles, Sliders, Plus, Trash2, ArrowRight, Building2, 
  RefreshCw, CheckSquare, Layers, FileSpreadsheet, Archive,
  ShieldCheck, AlertCircle, Award, UserCheck, X
} from 'lucide-react';
import { api } from '../services/api';

interface BatchStudent {
  id: string;
  full_name: string;
  father_mother_name: string;
  roll_no: string;
  college_name: string;
  degree: string;
  branch: string;
  attendance_pct: number;
}

const SAMPLE_NAMES = [
  "Aarav Sharma", "Aditi Verma", "Akash Gupta", "Ananya Singh", "Aniket Mishra",
  "Anjali Choudhary", "Arjun Patel", "Ayush Meena", "Bhavya Joshi", "Chetan Saini",
  "Deepak Kumar", "Divya Rathore", "Gaurav Agarwal", "Harsh Vardhan", "Ishita Jain",
  "Jatin Goyal", "Karan Mathur", "Khushi Sharma", "Kritika Soni", "Kuldeep Yadav",
  "Manish Jangid", "Mayank Bhardwaj", "Megha Khandelwal", "Mohit Bansal", "Muskan Pareek",
  "Naman Tiwari", "Neha Shringi", "Nikhil Singhal", "Nisha Gurjar", "Nitin Sharma",
  "Pankaj Prajapat", "Pooja Kumawat", "Pradeep Rawat", "Prakash Choudhary", "Prateek Saxena",
  "Priya Mahawar", "Rahul Gautam", "Rajesh Meena", "Rakesh Tanwar", "Riya Agrawal",
  "Rohit Nagar", "Roshni Sen", "Sachin Soni", "Sakshi Koli", "Sameer Khan",
  "Sanjay Meena", "Shreya Sharma", "Siddharth Jain", "Sneha Bairwa", "Vikas Jat"
];

const COURSE_TRACKS = [
  { code: 'DA', title: 'Data Analytics & Business Intelligence', badge: 'Python & Power BI', mentorId: 1 },
  { code: 'FS', title: 'Full Stack Web Development (MERN)', badge: 'React & Node.js', mentorId: 1 },
  { code: 'AI', title: 'Python AI, ML & Data Science', badge: 'ML & TensorFlow', mentorId: 2 },
  { code: 'CS', title: 'Cyber Security & Defensive Ops', badge: 'Security & VAPT', mentorId: 1 },
  { code: 'CC', title: 'Cloud Computing & DevOps Architecture', badge: 'AWS, Docker & K8s', mentorId: 2 },
  { code: 'JV', title: 'Java Enterprise & Spring Boot', badge: 'Spring Boot & JPA', mentorId: 1 },
  { code: 'BI', title: 'Bioinformatics & Computational Biology', badge: 'Genomics & BioPython', mentorId: 1 },
  { code: 'AD', title: 'Android Mobile App Development', badge: 'Kotlin & Compose', mentorId: 2 },
  { code: 'DM', title: 'Digital Marketing & Growth Strategy', badge: 'SEO, Ads & GA4', mentorId: 2 },
  { code: 'CUSTOM', title: 'Custom Track / Program Name', badge: 'Flexible Curricula', mentorId: 1 },
];

export const BulkAttendancePage: React.FC = () => {
  // 1. Institution selection (1 = TechnoGlobe, 2 = Poddar College)
  const [institutionId, setInstitutionId] = useState<number>(2);

  // 2. Batch configuration
  const [courseTrack, setCourseTrack] = useState<string>('DA');
  const [customTrackName, setCustomTrackName] = useState<string>('');
  const [totalDays, setTotalDays] = useState<number>(50);
  const [startDate, setStartDate] = useState<string>('2026-06-01');
  const [startTime, setStartTime] = useState<string>('10:00 AM');
  const [endTime, setEndTime] = useState<string>('01:30 PM');
  const [dailyHours, setDailyHours] = useState<number>(3.5);
  const [mentorId, setMentorId] = useState<number>(1);

  // 3. Students list
  const [students, setStudents] = useState<BatchStudent[]>([]);

  // 4. View Mode: 'roster' | 'preview'
  const [activeTab, setActiveTab] = useState<'roster' | 'preview'>('roster');

  // 5. Preview response state
  const [previewData, setPreviewData] = useState<any>(null);
  const [loadingPreview, setLoadingPreview] = useState<boolean>(false);
  const [isGeneratingPdf, setIsGeneratingPdf] = useState<boolean>(false);
  const [isGeneratingZip, setIsGeneratingZip] = useState<boolean>(false);
  const [isEnrolling, setIsEnrolling] = useState<boolean>(false);
  const [statusMessage, setStatusMessage] = useState<{ type: 'success' | 'error' | 'info'; text: string } | null>(null);

  // 6. Bulk Quick Paste Modal State
  const [showPasteModal, setShowPasteModal] = useState<boolean>(false);
  const [pasteText, setPasteText] = useState<string>('');

  // Initialize with 50 sample students on first render
  useEffect(() => {
    loadSampleStudents(50, 100);
  }, []);

  const loadSampleStudents = (count = 50, defaultPct = 100) => {
    const list: BatchStudent[] = [];
    const prefix = institutionId === 2 ? 'PCTM-2026' : 'TG-BPT-2026';
    const college = institutionId === 2 ? 'Poddar College, Bharatpur' : 'TechnoGlobe Centre, Bharatpur';

    for (let i = 0; i < count; i++) {
      const name = SAMPLE_NAMES[i % SAMPLE_NAMES.length];
      list.push({
        id: `stu_${Date.now()}_${i}`,
        full_name: count > SAMPLE_NAMES.length ? `${name} (${i + 1})` : name,
        father_mother_name: `Mr. ${name.split(' ')[1] || 'Kumar'} Sharma`,
        roll_no: `${prefix}-${String(i + 1).padStart(3, '0')}`,
        college_name: college,
        degree: 'BCA',
        branch: 'Computer Science',
        attendance_pct: defaultPct
      });
    }
    setStudents(list);
    setStatusMessage({ type: 'info', text: `Loaded ${count} sample students with ${defaultPct}% attendance.` });
  };

  const setAllAttendance = (pct: number) => {
    setStudents(prev => prev.map(s => ({ ...s, attendance_pct: pct })));
    setStatusMessage({ type: 'info', text: `All ${students.length} students set to ${pct}% attendance.` });
  };

  const randomizeAttendance = () => {
    setStudents(prev => prev.map(s => {
      const pcts = [100, 100, 95, 95, 92, 90, 88, 100, 96, 94];
      const randomPct = pcts[Math.floor(Math.random() * pcts.length)];
      return { ...s, attendance_pct: randomPct };
    }));
    setStatusMessage({ type: 'info', text: `Randomized attendance realistically (88% - 100%) across ${students.length} students.` });
  };

  const handleAddStudent = () => {
    const prefix = institutionId === 2 ? 'PCTM-2026' : 'TG-BPT-2026';
    const college = institutionId === 2 ? 'Poddar College, Bharatpur' : 'TechnoGlobe Centre, Bharatpur';
    const newIdx = students.length + 1;
    const newStudent: BatchStudent = {
      id: `stu_${Date.now()}_${newIdx}`,
      full_name: `New Student ${newIdx}`,
      father_mother_name: 'Father Name',
      roll_no: `${prefix}-${String(newIdx).padStart(3, '0')}`,
      college_name: college,
      degree: 'BCA',
      branch: 'Computer Science',
      attendance_pct: 100
    };
    setStudents([...students, newStudent]);
  };

  const handleRemoveStudent = (id: string) => {
    setStudents(students.filter(s => s.id !== id));
  };

  const handleUpdateStudent = (id: string, field: keyof BatchStudent, value: any) => {
    setStudents(students.map(s => s.id === id ? { ...s, [field]: value } : s));
  };

  const handleProcessPaste = () => {
    if (!pasteText.trim()) return;
    const lines = pasteText.split('\n').map(l => l.trim()).filter(l => l.length > 0);
    const prefix = institutionId === 2 ? 'PCTM-2026' : 'TG-BPT-2026';
    const college = institutionId === 2 ? 'Poddar College, Bharatpur' : 'TechnoGlobe Centre, Bharatpur';

    const parsedList: BatchStudent[] = lines.map((line, idx) => {
      const parts = line.split(/[,\t]+/).map(p => p.trim());
      let name = parts[0] || `Student ${idx + 1}`;
      let father = 'Father Name';
      let roll = `${prefix}-${String(idx + 1).padStart(3, '0')}`;
      let att = 100;

      if (parts.length === 2) {
        if (!isNaN(Number(parts[1]))) {
          att = Math.min(100, Math.max(0, Number(parts[1])));
        } else {
          father = parts[1];
        }
      } else if (parts.length >= 3) {
        father = parts[1] || father;
        roll = parts[2] || roll;
        if (parts[3] && !isNaN(Number(parts[3]))) {
          att = Math.min(100, Math.max(0, Number(parts[3])));
        }
      }

      return {
        id: `stu_${Date.now()}_${idx}`,
        full_name: name,
        father_mother_name: father,
        roll_no: roll,
        college_name: college,
        degree: 'BCA',
        branch: 'Computer Science',
        attendance_pct: att
      };
    });

    setStudents(parsedList);
    setShowPasteModal(false);
    setPasteText('');
    setStatusMessage({ type: 'success', text: `Successfully imported ${parsedList.length} students from pasted text!` });
  };

  const fetchLivePreview = async () => {
    if (students.length === 0) {
      setStatusMessage({ type: 'error', text: 'Please add at least one student to generate attendance.' });
      return;
    }
    setLoadingPreview(true);
    setStatusMessage(null);
    try {
      const payload = {
        institution_id: institutionId,
        course_track: courseTrack,
        custom_track_name: courseTrack === 'CUSTOM' ? customTrackName : undefined,
        total_days: Number(totalDays),
        start_date: startDate,
        start_time: startTime,
        end_time: endTime,
        daily_hours: Number(dailyHours),
        mentor_id: mentorId,
        students: students.map(s => ({
          full_name: s.full_name,
          father_mother_name: s.father_mother_name,
          roll_no: s.roll_no,
          college_name: s.college_name,
          degree: s.degree,
          branch: s.branch,
          attendance_pct: Number(s.attendance_pct)
        }))
      };
      const data = await api.bulkAttendancePreview(payload);
      setPreviewData(data);
      setActiveTab('preview');
      setStatusMessage({ type: 'success', text: `Generated day-wise schedule for ${data.students.length} students across ${data.working_days.length} working days!` });
    } catch (e: any) {
      setStatusMessage({ type: 'error', text: e.message || 'Failed to generate preview' });
    } finally {
      setLoadingPreview(false);
    }
  };

  const handleDownloadMasterPdf = async () => {
    if (students.length === 0) return;
    setIsGeneratingPdf(true);
    try {
      const payload = {
        institution_id: institutionId,
        course_track: courseTrack,
        custom_track_name: courseTrack === 'CUSTOM' ? customTrackName : undefined,
        total_days: Number(totalDays),
        start_date: startDate,
        start_time: startTime,
        end_time: endTime,
        daily_hours: Number(dailyHours),
        mentor_id: mentorId,
        students: students.map(s => ({
          full_name: s.full_name,
          father_mother_name: s.father_mother_name,
          roll_no: s.roll_no,
          college_name: s.college_name,
          degree: s.degree,
          branch: s.branch,
          attendance_pct: Number(s.attendance_pct)
        }))
      };
      await api.downloadMasterAttendancePdf(payload);
      setStatusMessage({ type: 'success', text: 'Master Batch Attendance Register PDF downloaded successfully!' });
    } catch (e: any) {
      setStatusMessage({ type: 'error', text: e.message || 'Failed to download PDF' });
    } finally {
      setIsGeneratingPdf(false);
    }
  };

  const handleDownloadZip = async () => {
    if (students.length === 0) return;
    setIsGeneratingZip(true);
    try {
      const payload = {
        institution_id: institutionId,
        course_track: courseTrack,
        custom_track_name: courseTrack === 'CUSTOM' ? customTrackName : undefined,
        total_days: Number(totalDays),
        start_date: startDate,
        start_time: startTime,
        end_time: endTime,
        daily_hours: Number(dailyHours),
        mentor_id: mentorId,
        students: students.map(s => ({
          full_name: s.full_name,
          father_mother_name: s.father_mother_name,
          roll_no: s.roll_no,
          college_name: s.college_name,
          degree: s.degree,
          branch: s.branch,
          attendance_pct: Number(s.attendance_pct)
        }))
      };
      await api.downloadBatchAttendanceZip(payload);
      setStatusMessage({ type: 'success', text: `Complete Batch ZIP Package (${students.length} individual PDFs + Master PDF + CSV) downloaded!` });
    } catch (e: any) {
      setStatusMessage({ type: 'error', text: e.message || 'Failed to download ZIP bundle' });
    } finally {
      setIsGeneratingZip(false);
    }
  };

  const handleBulkEnroll = async () => {
    if (students.length === 0) return;
    if (!window.confirm(`Are you sure you want to enroll all ${students.length} students into the system database? This will create complete student profiles and day-wise attendance records.`)) {
      return;
    }
    setIsEnrolling(true);
    try {
      const payload = {
        institution_id: institutionId,
        course_track: courseTrack,
        custom_track_name: courseTrack === 'CUSTOM' ? customTrackName : undefined,
        total_days: Number(totalDays),
        start_date: startDate,
        start_time: startTime,
        end_time: endTime,
        daily_hours: Number(dailyHours),
        mentor_id: mentorId,
        students: students.map(s => ({
          full_name: s.full_name,
          father_mother_name: s.father_mother_name,
          roll_no: s.roll_no,
          college_name: s.college_name,
          degree: s.degree,
          branch: s.branch,
          attendance_pct: Number(s.attendance_pct)
        }))
      };
      const res = await api.bulkEnrollStudents(payload);
      setStatusMessage({ type: 'success', text: res.message || `Enrolled ${res.enrolled_count} students successfully!` });
    } catch (e: any) {
      setStatusMessage({ type: 'error', text: e.message || 'Failed to enroll students' });
    } finally {
      setIsEnrolling(false);
    }
  };

  const avgAttendance = students.length > 0 
    ? (students.reduce((sum, s) => sum + Number(s.attendance_pct || 0), 0) / students.length).toFixed(1)
    : '0';

  const count100 = students.filter(s => Number(s.attendance_pct) === 100).length;

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Top Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 text-white p-6 rounded-2xl shadow-xl border border-indigo-500/20 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center space-x-2 text-indigo-400 text-xs font-bold uppercase tracking-wider mb-1">
              <Layers className="w-4 h-4" />
              <span>Multi-Student Batch Generator</span>
              <span className="bg-amber-400 text-slate-950 text-[10px] px-2 py-0.5 rounded-full font-extrabold">NEW</span>
            </div>
            <h1 className="text-2xl md:text-3xl font-black tracking-tight text-white">
              Bulk Batch Attendance Generator (50+ Students)
            </h1>
            <p className="text-sm text-slate-300 mt-1 max-w-3xl">
              Configure day-wise attendance for 50 or more students across any customizable timeline (50 days, 36 days, 60 days). Configure individual attendance percentages (100% = 0 absences) with dual institutional branding for TechnoGlobe and Poddar College, Bharatpur.
            </p>
          </div>

          <div className="flex items-center space-x-3 shrink-0">
            <Link
              to="/attendance"
              className="px-4 py-2 text-xs font-semibold text-slate-300 hover:text-white bg-slate-800/80 hover:bg-slate-800 rounded-lg border border-slate-700 transition"
            >
              Single Student Planner
            </Link>
          </div>
        </div>
      </div>

      {/* Status Alert */}
      {statusMessage && (
        <div className={`p-4 rounded-xl flex items-center justify-between shadow-sm border ${
          statusMessage.type === 'success' 
            ? 'bg-emerald-50 text-emerald-900 border-emerald-200' 
            : statusMessage.type === 'error'
            ? 'bg-rose-50 text-rose-900 border-rose-200'
            : 'bg-blue-50 text-blue-900 border-blue-200'
        }`}>
          <div className="flex items-center space-x-2.5 text-sm font-medium">
            {statusMessage.type === 'success' ? <CheckCircle2 className="w-5 h-5 text-emerald-600" /> : <AlertCircle className="w-5 h-5 text-blue-600" />}
            <span>{statusMessage.text}</span>
          </div>
          <button onClick={() => setStatusMessage(null)} className="text-slate-400 hover:text-slate-600">
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* 1. Dual Institution Selection */}
      <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-sm font-bold uppercase tracking-wider text-slate-500 flex items-center space-x-2">
              <Building2 className="w-4 h-4 text-indigo-600" />
              <span>Step 1: Choose Issuing Institution</span>
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Select which institutional branding, crest watermark, header, and official stamp box will be applied.
            </p>
          </div>
          <span className="text-xs font-bold px-2.5 py-1 rounded-full bg-indigo-50 text-indigo-700 border border-indigo-200">
            Active: {institutionId === 2 ? 'Poddar College' : 'TechnoGlobe'}
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Card 1: TechnoGlobe */}
          <div
            onClick={() => setInstitutionId(1)}
            className={`p-4 rounded-xl border-2 cursor-pointer transition-all ${
              institutionId === 1
                ? 'border-blue-600 bg-blue-50/50 shadow-md ring-2 ring-blue-500/20'
                : 'border-slate-200 bg-white hover:border-slate-300'
            }`}
          >
            <div className="flex items-start justify-between">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 rounded-lg bg-blue-900 text-amber-400 flex items-center justify-center font-black text-xs shadow-sm">
                  TG
                </div>
                <div>
                  <h3 className="font-bold text-slate-900 text-sm">TechnoGlobe – Bharatpur Centre</h3>
                  <p className="text-xs text-slate-500">ISO 9001:2015 Certified IT Solutions</p>
                </div>
              </div>
              {institutionId === 1 && (
                <CheckCircle2 className="w-5 h-5 text-blue-600" />
              )}
            </div>
            <div className="mt-3 grid grid-cols-2 gap-2 text-[11px] text-slate-600 bg-white/80 p-2.5 rounded-lg border border-slate-100">
              <div><span className="font-semibold text-slate-700">Seal:</span> Digital Gold Seal</div>
              <div><span className="font-semibold text-slate-700">Ref Code:</span> TG/BPT/BATCH</div>
              <div><span className="font-semibold text-slate-700">Theme:</span> Deep Navy & Gold</div>
              <div><span className="font-semibold text-slate-700">Signatory:</span> Nitin Sir</div>
            </div>
          </div>

          {/* Card 2: Poddar College */}
          <div
            onClick={() => setInstitutionId(2)}
            className={`p-4 rounded-xl border-2 cursor-pointer transition-all ${
              institutionId === 2
                ? 'border-amber-600 bg-amber-50/50 shadow-md ring-2 ring-amber-500/20'
                : 'border-slate-200 bg-white hover:border-slate-300'
            }`}
          >
            <div className="flex items-start justify-between">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 rounded-lg bg-slate-900 text-amber-400 flex items-center justify-center font-black text-xs shadow-sm">
                  PCTM
                </div>
                <div>
                  <h3 className="font-bold text-slate-900 text-sm">Poddar College of Technology & Management</h3>
                  <p className="text-xs text-slate-500">Bharatpur, Rajasthan (No Affiliation Line)</p>
                </div>
              </div>
              {institutionId === 2 && (
                <CheckCircle2 className="w-5 h-5 text-amber-600" />
              )}
            </div>
            <div className="mt-3 grid grid-cols-2 gap-2 text-[11px] text-slate-600 bg-white/80 p-2.5 rounded-lg border border-slate-100">
              <div><span className="font-semibold text-slate-700">Seal:</span> Physical Ink Stamp Box</div>
              <div><span className="font-semibold text-slate-700">Watermark:</span> Poddar Crest</div>
              <div><span className="font-semibold text-slate-700">Ref Code:</span> PCTM/BPT/BATCH</div>
              <div><span className="font-semibold text-slate-700">Signatory:</span> Nitin Sir</div>
            </div>
          </div>
        </div>
      </div>

      {/* 2. Batch Timeline & Schedule Configuration */}
      <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-4">
        <h2 className="text-sm font-bold uppercase tracking-wider text-slate-500 flex items-center space-x-2">
          <Calendar className="w-4 h-4 text-indigo-600" />
          <span>Step 2: Batch Track & Working Days Configuration</span>
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Course Track */}
          <div className="md:col-span-2 space-y-1.5">
            <label className="text-xs font-bold text-slate-700">Course Track / Program</label>
            <select
              value={courseTrack}
              onChange={(e) => setCourseTrack(e.target.value)}
              className="w-full text-xs font-medium px-3 py-2.5 bg-slate-50 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
            >
              {COURSE_TRACKS.map(t => (
                <option key={t.code} value={t.code}>
                  {t.title} ({t.badge})
                </option>
              ))}
            </select>
            {courseTrack === 'CUSTOM' && (
              <input
                type="text"
                placeholder="Enter custom program name (e.g. Advanced Diploma in AI)"
                value={customTrackName}
                onChange={(e) => setCustomTrackName(e.target.value)}
                className="w-full text-xs px-3 py-2 mt-2 bg-white border border-indigo-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              />
            )}
          </div>

          {/* Number of Working Days */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between">
              <label className="text-xs font-bold text-slate-700">Working Days</label>
              <span className="text-xs font-extrabold text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded">
                {totalDays} Days
              </span>
            </div>
            <input
              type="number"
              min={1}
              max={120}
              value={totalDays}
              onChange={(e) => setTotalDays(Math.max(1, Number(e.target.value)))}
              className="w-full text-xs font-bold px-3 py-2 bg-slate-50 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
            />
            <div className="flex items-center space-x-1 mt-1">
              {[36, 45, 50, 60].map(d => (
                <button
                  key={d}
                  type="button"
                  onClick={() => setTotalDays(d)}
                  className={`text-[10px] px-2 py-0.5 rounded font-semibold border transition ${
                    totalDays === d ? 'bg-indigo-600 text-white border-indigo-600' : 'bg-slate-100 text-slate-600 hover:bg-slate-200 border-slate-200'
                  }`}
                >
                  {d}d
                </button>
              ))}
            </div>
          </div>

          {/* Start Date */}
          <div className="space-y-1.5">
            <label className="text-xs font-bold text-slate-700">Start Date</label>
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="w-full text-xs font-medium px-3 py-2 bg-slate-50 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
            />
            <p className="text-[10px] text-slate-500">Skips Sundays automatically</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 pt-2 border-t border-slate-100">
          {/* Timings */}
          <div className="space-y-1.5">
            <label className="text-xs font-bold text-slate-700">Daily Session Timings</label>
            <div className="flex items-center space-x-2">
              <input
                type="text"
                value={startTime}
                onChange={(e) => setStartTime(e.target.value)}
                placeholder="10:00 AM"
                className="w-1/2 text-xs px-2 py-1.5 bg-slate-50 border border-slate-300 rounded-md"
              />
              <span className="text-xs text-slate-400">to</span>
              <input
                type="text"
                value={endTime}
                onChange={(e) => setEndTime(e.target.value)}
                placeholder="01:30 PM"
                className="w-1/2 text-xs px-2 py-1.5 bg-slate-50 border border-slate-300 rounded-md"
              />
            </div>
          </div>

          {/* Daily Hours */}
          <div className="space-y-1.5">
            <label className="text-xs font-bold text-slate-700">Daily Hours Logged</label>
            <input
              type="number"
              step="0.5"
              min="1"
              max="8"
              value={dailyHours}
              onChange={(e) => setDailyHours(Number(e.target.value))}
              className="w-full text-xs px-3 py-1.5 bg-slate-50 border border-slate-300 rounded-md"
            />
            <p className="text-[10px] text-slate-500">Total: {totalDays * dailyHours} structured training hrs</p>
          </div>

          {/* Supervising Mentor */}
          <div className="space-y-1.5">
            <label className="text-xs font-bold text-slate-700">Supervising Faculty</label>
            <select
              value={mentorId}
              onChange={(e) => setMentorId(Number(e.target.value))}
              className="w-full text-xs font-medium px-3 py-1.5 bg-slate-50 border border-slate-300 rounded-md"
            >
              <option value={1}>Prof. Krishlay Sharma (Computer Science)</option>
              <option value={2}>Prof. Rahul Bhatnagar (Data Science & AI)</option>
            </select>
          </div>

          {/* Center Head */}
          <div className="space-y-1.5">
            <label className="text-xs font-bold text-slate-700">Centre Head & Signatory</label>
            <div className="px-3 py-1.5 bg-slate-100 border border-slate-200 rounded-md text-xs font-bold text-slate-800 flex items-center justify-between">
              <span>Nitin Sir</span>
              <span className="text-[10px] text-indigo-700 font-medium">Centre Head</span>
            </div>
          </div>
        </div>
      </div>

      {/* 3. Main Roster & Preview Tabs */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        {/* Navigation Tabs & Bulk Actions */}
        <div className="bg-slate-50 p-4 border-b border-slate-200 flex flex-col md:flex-row md:items-center justify-between gap-3">
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setActiveTab('roster')}
              className={`px-4 py-2 rounded-lg text-xs font-bold transition flex items-center space-x-2 ${
                activeTab === 'roster'
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'bg-white text-slate-700 hover:bg-slate-100 border border-slate-200'
              }`}
            >
              <Users className="w-3.5 h-3.5" />
              <span>Student Roster Editor ({students.length})</span>
            </button>

            <button
              onClick={fetchLivePreview}
              disabled={loadingPreview}
              className={`px-4 py-2 rounded-lg text-xs font-bold transition flex items-center space-x-2 ${
                activeTab === 'preview'
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'bg-white text-slate-700 hover:bg-slate-100 border border-slate-200'
              }`}
            >
              {loadingPreview ? <RefreshCw className="w-3.5 h-3.5 animate-spin text-indigo-600" /> : <Calendar className="w-3.5 h-3.5 text-indigo-600" />}
              <span>Live Day-Wise Matrix Preview</span>
            </button>
          </div>

          {/* Quick Presets */}
          <div className="flex flex-wrap items-center gap-2">
            <button
              onClick={() => loadSampleStudents(50, 100)}
              className="px-2.5 py-1.5 rounded-lg text-[11px] font-semibold bg-white hover:bg-slate-100 text-slate-700 border border-slate-200 transition flex items-center space-x-1"
            >
              <Sparkles className="w-3 h-3 text-amber-500" />
              <span>Fill 50 Students</span>
            </button>

            <button
              onClick={() => setAllAttendance(100)}
              className="px-2.5 py-1.5 rounded-lg text-[11px] font-bold bg-emerald-50 hover:bg-emerald-100 text-emerald-800 border border-emerald-200 transition flex items-center space-x-1"
            >
              <span>💯 Set All 100%</span>
            </button>

            <button
              onClick={() => setAllAttendance(95)}
              className="px-2.5 py-1.5 rounded-lg text-[11px] font-semibold bg-white hover:bg-slate-100 text-slate-700 border border-slate-200 transition"
            >
              Set 95%
            </button>

            <button
              onClick={randomizeAttendance}
              className="px-2.5 py-1.5 rounded-lg text-[11px] font-semibold bg-white hover:bg-slate-100 text-slate-700 border border-slate-200 transition"
            >
              🎲 Randomize (90-100%)
            </button>

            <button
              onClick={() => setShowPasteModal(true)}
              className="px-3 py-1.5 rounded-lg text-[11px] font-bold bg-indigo-50 hover:bg-indigo-100 text-indigo-800 border border-indigo-200 transition flex items-center space-x-1"
            >
              <FileSpreadsheet className="w-3.5 h-3.5 text-indigo-600" />
              <span>Paste 50 Names</span>
            </button>

            <button
              onClick={handleAddStudent}
              className="px-2.5 py-1.5 rounded-lg text-[11px] font-bold bg-slate-900 hover:bg-slate-800 text-white transition flex items-center space-x-1"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Add</span>
            </button>
          </div>
        </div>

        {/* Tab 1: Student Roster Grid */}
        {activeTab === 'roster' && (
          <div className="p-4 space-y-4">
            {/* Summary Strip */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
                <span className="text-[10px] font-bold uppercase text-slate-400">Total Students</span>
                <p className="text-xl font-black text-slate-800">{students.length}</p>
              </div>
              <div className="p-3 bg-emerald-50 rounded-xl border border-emerald-200">
                <span className="text-[10px] font-bold uppercase text-emerald-600">100% Attendance (0 Absences)</span>
                <p className="text-xl font-black text-emerald-800">{count100} Students</p>
              </div>
              <div className="p-3 bg-blue-50 rounded-xl border border-blue-200">
                <span className="text-[10px] font-bold uppercase text-blue-600">Batch Avg Attendance</span>
                <p className="text-xl font-black text-blue-800">{avgAttendance}%</p>
              </div>
              <div className="p-3 bg-indigo-50 rounded-xl border border-indigo-200">
                <span className="text-[10px] font-bold uppercase text-indigo-600">Total Working Days</span>
                <p className="text-xl font-black text-indigo-800">{totalDays} Days</p>
              </div>
            </div>

            {/* Students Table */}
            <div className="overflow-x-auto rounded-xl border border-slate-200">
              <table className="w-full text-left border-collapse text-xs">
                <thead>
                  <tr className="bg-slate-900 text-white font-bold">
                    <th className="py-2.5 px-3 w-10 text-center">#</th>
                    <th className="py-2.5 px-3 w-32">Roll / ID</th>
                    <th className="py-2.5 px-3 min-w-[180px]">Student Full Name</th>
                    <th className="py-2.5 px-3 min-w-[150px]">Father's Name</th>
                    <th className="py-2.5 px-3 w-28">Degree / Branch</th>
                    <th className="py-2.5 px-3 min-w-[180px]">Attendance % (Configurable)</th>
                    <th className="py-2.5 px-3 w-24 text-center">Days Present</th>
                    <th className="py-2.5 px-3 w-12 text-center">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-200 font-medium">
                  {students.map((stu, index) => {
                    const presentCount = Math.max(1, Math.round(totalDays * (stu.attendance_pct / 100)));
                    const is100 = stu.attendance_pct === 100;

                    return (
                      <tr key={stu.id} className="hover:bg-slate-50/80 transition">
                        <td className="py-2 px-3 text-center text-slate-400 font-mono text-[11px]">{index + 1}</td>
                        <td className="py-2 px-3">
                          <input
                            type="text"
                            value={stu.roll_no}
                            onChange={(e) => handleUpdateStudent(stu.id, 'roll_no', e.target.value)}
                            className="w-full px-2 py-1 bg-transparent border border-transparent hover:border-slate-300 focus:border-indigo-500 rounded font-mono text-[11px]"
                          />
                        </td>
                        <td className="py-2 px-3">
                          <input
                            type="text"
                            value={stu.full_name}
                            onChange={(e) => handleUpdateStudent(stu.id, 'full_name', e.target.value)}
                            className="w-full px-2 py-1 bg-transparent border border-transparent hover:border-slate-300 focus:border-indigo-500 rounded font-bold text-slate-800"
                          />
                        </td>
                        <td className="py-2 px-3">
                          <input
                            type="text"
                            value={stu.father_mother_name}
                            onChange={(e) => handleUpdateStudent(stu.id, 'father_mother_name', e.target.value)}
                            className="w-full px-2 py-1 bg-transparent border border-transparent hover:border-slate-300 focus:border-indigo-500 rounded text-slate-600"
                          />
                        </td>
                        <td className="py-2 px-3">
                          <span className="text-[11px] text-slate-600 font-semibold">{stu.degree} - {stu.branch}</span>
                        </td>
                        <td className="py-2 px-3">
                          <div className="flex items-center space-x-2">
                            <input
                              type="range"
                              min={50}
                              max={100}
                              step={1}
                              value={stu.attendance_pct}
                              onChange={(e) => handleUpdateStudent(stu.id, 'attendance_pct', Number(e.target.value))}
                              className="w-24 h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-indigo-600"
                            />
                            <input
                              type="number"
                              min={50}
                              max={100}
                              value={stu.attendance_pct}
                              onChange={(e) => handleUpdateStudent(stu.id, 'attendance_pct', Math.min(100, Math.max(0, Number(e.target.value))))}
                              className={`w-14 px-1.5 py-0.5 text-center font-bold rounded border ${
                                is100
                                  ? 'bg-emerald-50 text-emerald-800 border-emerald-300'
                                  : stu.attendance_pct >= 90
                                  ? 'bg-blue-50 text-blue-800 border-blue-300'
                                  : 'bg-amber-50 text-amber-800 border-amber-300'
                              }`}
                            />
                            <span className="text-[11px] font-bold text-slate-500">%</span>
                            {is100 && (
                              <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-100 text-emerald-800 font-extrabold uppercase">
                                Full
                              </span>
                            )}
                          </div>
                        </td>
                        <td className="py-2 px-3 text-center">
                          <span className={`font-bold ${is100 ? 'text-emerald-700' : 'text-slate-700'}`}>
                            {presentCount} / {totalDays}d
                          </span>
                        </td>
                        <td className="py-2 px-3 text-center">
                          <button
                            onClick={() => handleRemoveStudent(stu.id)}
                            className="p-1 text-slate-400 hover:text-rose-600 rounded transition"
                            title="Remove Student"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Tab 2: Live Day-Wise Matrix Preview */}
        {activeTab === 'preview' && (
          <div className="p-4 space-y-4">
            {previewData ? (
              <>
                <div className="p-4 bg-slate-900 text-white rounded-xl flex flex-wrap items-center justify-between gap-4">
                  <div>
                    <h3 className="text-sm font-bold">
                      {previewData.institution.full_name} — Master Attendance Register Preview
                    </h3>
                    <p className="text-xs text-slate-400 mt-0.5">
                      Batch: {previewData.batch_meta.custom_track_name} | {previewData.working_days.length} Working Days ({previewData.batch_meta.start_date} to {previewData.batch_meta.end_date})
                    </p>
                  </div>
                  <div className="flex items-center space-x-3 text-xs">
                    <span className="flex items-center space-x-1.5"><span className="w-2.5 h-2.5 rounded-full bg-emerald-400"></span><span>P = Present</span></span>
                    <span className="flex items-center space-x-1.5"><span className="w-2.5 h-2.5 rounded-full bg-amber-400"></span><span>L = Leave</span></span>
                  </div>
                </div>

                <div className="overflow-x-auto rounded-xl border border-slate-200 max-h-[500px]">
                  <table className="w-full text-left border-collapse text-[11px]">
                    <thead className="sticky top-0 z-10">
                      <tr className="bg-slate-900 text-white font-bold">
                        <th className="py-2 px-2.5 w-8 text-center border-r border-slate-700">#</th>
                        <th className="py-2 px-2.5 w-24 border-r border-slate-700">Roll No</th>
                        <th className="py-2 px-2.5 min-w-[140px] border-r border-slate-700">Student Name</th>
                        {previewData.working_days.map((d: any) => (
                          <th key={d.day_number} className="py-1 px-1.5 text-center min-w-[28px] border-r border-slate-700 text-[10px]">
                            D{d.day_number}
                            <div className="text-[8px] font-normal text-slate-400">{d.short_date}</div>
                          </th>
                        ))}
                        <th className="py-2 px-2 text-center w-12 border-r border-slate-700">Pres</th>
                        <th className="py-2 px-2 text-center w-12 border-r border-slate-700">Leave</th>
                        <th className="py-2 px-2 text-center w-12 border-r border-slate-700">Hours</th>
                        <th className="py-2 px-2 text-center w-14">Att %</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-200">
                      {previewData.students.map((stu: any, sIdx: number) => (
                        <tr key={sIdx} className="hover:bg-slate-50 transition">
                          <td className="py-1.5 px-2 text-center text-slate-400 font-mono text-[10px] border-r border-slate-200">{sIdx + 1}</td>
                          <td className="py-1.5 px-2 font-mono text-[10px] text-slate-600 border-r border-slate-200">{stu.roll_no}</td>
                          <td className="py-1.5 px-2 font-bold text-slate-800 border-r border-slate-200">{stu.full_name}</td>
                          {stu.records.map((r: any, rIdx: number) => (
                            <td key={rIdx} className="py-1 px-1 text-center border-r border-slate-200">
                              {r.short_status === 'P' ? (
                                <span className="font-extrabold text-emerald-600">P</span>
                              ) : (
                                <span className="font-extrabold text-amber-600">L</span>
                              )}
                            </td>
                          ))}
                          <td className="py-1.5 px-2 text-center font-bold text-slate-800 border-r border-slate-200">{stu.present_days}</td>
                          <td className="py-1.5 px-2 text-center text-slate-600 border-r border-slate-200">{stu.leave_days}</td>
                          <td className="py-1.5 px-2 text-center text-slate-600 border-r border-slate-200">{stu.total_hours_logged}h</td>
                          <td className="py-1.5 px-2 text-center font-bold">
                            <span className={stu.attendance_pct_actual >= 90 ? 'text-emerald-700' : 'text-amber-700'}>
                              {stu.attendance_pct_actual}%
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </>
            ) : (
              <div className="p-12 text-center space-y-3">
                <Calendar className="w-10 h-10 text-slate-300 mx-auto" />
                <h3 className="font-bold text-slate-700 text-sm">No Preview Generated Yet</h3>
                <p className="text-xs text-slate-500 max-w-sm mx-auto">
                  Click the button below to compute day-by-day attendance schedules for all {students.length} students.
                </p>
                <button
                  onClick={fetchLivePreview}
                  disabled={loadingPreview}
                  className="px-4 py-2 bg-indigo-600 text-white text-xs font-bold rounded-lg hover:bg-indigo-700 shadow-sm"
                >
                  Generate Live Day-Wise Matrix
                </button>
              </div>
            )}
          </div>
        )}

        {/* 4. Action Bar (Download Master PDF / Complete ZIP / Enroll to Database) */}
        <div className="bg-slate-900 p-5 text-white flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <span className="text-xs text-slate-400">Ready to download & issue batch documentation:</span>
            <div className="text-sm font-bold text-white flex items-center space-x-2 mt-0.5">
              <span>{students.length} Students</span>
              <span>•</span>
              <span>{totalDays} Working Days</span>
              <span>•</span>
              <span>{institutionId === 2 ? 'Poddar College' : 'TechnoGlobe'}</span>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            {/* Download Master PDF */}
            <button
              onClick={handleDownloadMasterPdf}
              disabled={isGeneratingPdf || students.length === 0}
              className="px-4 py-2.5 rounded-xl text-xs font-bold bg-white hover:bg-slate-100 text-slate-900 transition flex items-center space-x-2 shadow-sm disabled:opacity-50"
            >
              {isGeneratingPdf ? <RefreshCw className="w-4 h-4 animate-spin text-slate-900" /> : <FileText className="w-4 h-4 text-indigo-600" />}
              <span>Download Master Register (Landscape PDF)</span>
            </button>

            {/* Download Complete ZIP */}
            <button
              onClick={handleDownloadZip}
              disabled={isGeneratingZip || students.length === 0}
              className="px-4 py-2.5 rounded-xl text-xs font-bold bg-gradient-to-r from-amber-500 to-amber-400 hover:from-amber-400 hover:to-amber-300 text-slate-950 transition flex items-center space-x-2 shadow-md disabled:opacity-50"
            >
              {isGeneratingZip ? <RefreshCw className="w-4 h-4 animate-spin text-slate-950" /> : <Archive className="w-4 h-4 text-slate-950" />}
              <span>Download Complete Batch ZIP (All PDFs + CSV)</span>
            </button>

            {/* Enroll to DB */}
            <button
              onClick={handleBulkEnroll}
              disabled={isEnrolling || students.length === 0}
              className="px-4 py-2.5 rounded-xl text-xs font-bold bg-indigo-600 hover:bg-indigo-500 text-white transition flex items-center space-x-2 shadow-md disabled:opacity-50"
            >
              {isEnrolling ? <RefreshCw className="w-4 h-4 animate-spin text-white" /> : <UserCheck className="w-4 h-4 text-white" />}
              <span>Save & Enroll to Database</span>
            </button>
          </div>
        </div>
      </div>

      {/* Bulk Quick Paste Modal */}
      {showPasteModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-2xl w-full p-6 shadow-2xl border border-slate-200 space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <FileSpreadsheet className="w-5 h-5 text-indigo-600" />
                <h3 className="font-bold text-slate-900 text-base">Quick Bulk Paste (50+ Student Names)</h3>
              </div>
              <button onClick={() => setShowPasteModal(false)} className="text-slate-400 hover:text-slate-600">
                <X className="w-5 h-5" />
              </button>
            </div>

            <p className="text-xs text-slate-600 leading-relaxed">
              Paste student names directly from Excel, Word, or plain text (one student per line). You can also include attendance percentage separated by comma (e.g. <code>Aarav Sharma, 100</code>).
            </p>

            <textarea
              rows={10}
              value={pasteText}
              onChange={(e) => setPasteText(e.target.value)}
              placeholder="Aarav Sharma&#10;Aditi Verma, 100&#10;Akash Gupta, 95&#10;Ananya Singh, Mr. R.K. Singh, PCTM-004, 100&#10;..."
              className="w-full text-xs font-mono p-3 bg-slate-50 border border-slate-300 rounded-xl focus:ring-2 focus:ring-indigo-500"
            />

            <div className="flex items-center justify-between pt-2">
              <span className="text-xs text-slate-400">
                Lines detected: {pasteText.split('\n').filter(l => l.trim().length > 0).length}
              </span>
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => setShowPasteModal(false)}
                  className="px-4 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-100 rounded-lg"
                >
                  Cancel
                </button>
                <button
                  onClick={handleProcessPaste}
                  className="px-5 py-2 text-xs font-bold bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg shadow-sm"
                >
                  Import Roster Now
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
