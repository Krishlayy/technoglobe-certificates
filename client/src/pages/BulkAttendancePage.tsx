import React, { useState, useEffect } from 'react';
import {
  Users,
  Building2,
  Calendar,
  Clock,
  Award,
  FileSpreadsheet,
  FileText,
  Download,
  CheckCircle2,
  RefreshCw,
  Plus,
  Trash2,
  Sliders,
  Sparkles,
  ClipboardPaste,
  Eye,
  BookOpen,
  ArrowRight,
  ShieldCheck,
  Percent,
  Check,
  X,
  RotateCcw,
  Sun
} from 'lucide-react';
import { api } from '../services/api';

interface BatchStudent {
  id: string;
  full_name: string;
  father_mother_name?: string;
  roll_no?: string;
  college_name?: string;
  degree?: string;
  branch?: string;
  attendance_pct: number;
  day_overrides?: { [dayNumber: number]: 'PRESENT' | 'LEAVE' };
}

const SAMPLE_NAMES = [
  'Aarav Sharma', 'Bhavya Gupta', 'Chirag Meena', 'Divya Patel', 'Eshan Verma',
  'Gaurav Singhal', 'Harshita Saini', 'Ishaan Agarwal', 'Jatin Choudhary', 'Kavita Mishra',
  'Lakshya Khandelwal', 'Manish Bansal', 'Neha Gurjar', 'Om Prakash Rawat', 'Pooja Jangid',
  'Rahul Prajapat', 'Ritu Mathur', 'Sachin Goyal', 'Tanvi Soni', 'Utkarsh Bhardwaj',
  'Vikas Kumawat', 'Yash Sharma', 'Aakash Nagar', 'Ananya Dixit', 'Ankit Faujdar',
  'Deepak Sain', 'Garima Mittal', 'Himanshu Sharma', 'Jyoti Meena', 'Kunal Verma',
  'Mayank Agrawal', 'Naveen Kumar', 'Prachi Jain', 'Priya Gurjar', 'Rohit Saini',
  'Sakshi Sharma', 'Sandeep Singh', 'Shubham Jindal', 'Tarun Lodha', 'Varun Goyal'
];

const COURSE_TRACKS = [
  { code: 'SOL-01', title: 'Rooftop Solar PV Installation & Building Integration (BIPV)', badge: 'Solar & BIPV', mentorId: 1 },
  { code: 'SOL-02', title: 'Solar Structure Fitting, Panel Mounting & Civil Layout', badge: 'Structure Fitting', mentorId: 1 },
  { code: 'SOL-03', title: 'Solar Electrical Systems, Inverters & Grid-Tied Technology', badge: 'Electrical & Inverter', mentorId: 1 },
  { code: 'SOL-04', title: 'Industrial Solar Power Plant Operations & Maintenance (O&M)', badge: 'Industrial Solar O&M', mentorId: 1 },
  { code: 'SOL-05', title: 'Solar Water Heating & Agricultural Pumping Systems', badge: 'Pumps & Thermal', mentorId: 1 },
  { code: 'SOL-06', title: 'Off-Grid Solar Energy Storage & Battery Management (BMS)', badge: 'Storage & Batteries', mentorId: 1 },
  { code: 'SOL-07', title: 'Solar PV System Design, Load Estimation & PVsyst Simulation', badge: 'PVsyst Design', mentorId: 1 },
  { code: 'SOL-08', title: 'Solar Safety Standards, Electrical Earthing & Net-Metering', badge: 'Safety & Metering', mentorId: 1 },
  { code: 'DA', title: 'Data Analytics & Business Intelligence', badge: 'Excel, SQL & Power BI', mentorId: 2 },
  { code: 'FS', title: 'Full Stack Web Development (MERN)', badge: 'React, Node & MongoDB', mentorId: 2 },
  { code: 'AI', title: 'Python AI, ML & Data Science', badge: 'ML & TensorFlow', mentorId: 2 },
  { code: 'CS', title: 'Cyber Security & Ethical Hacking', badge: 'Security & VAPT', mentorId: 2 },
  { code: 'CC', title: 'Cloud Computing & DevOps Architecture', badge: 'AWS, Docker & K8s', mentorId: 3 },
  { code: 'JV', title: 'Java Full Stack Development', badge: 'Spring Boot & JPA', mentorId: 2 },
  { code: 'AD', title: 'Android Mobile App Development', badge: 'Kotlin & Compose', mentorId: 3 },
  { code: 'DM', title: 'Digital Marketing & Growth Strategy', badge: 'SEO, Ads & GA4', mentorId: 3 },
  { code: 'CUSTOM', title: 'Custom Track / Program Name', badge: 'Flexible Curricula', mentorId: 1 },
];

export const BulkAttendancePage: React.FC = () => {
  // 1. Institution selection (1 = Poddar College, 2 = Poswal Developers)
  const [institutionId, setInstitutionId] = useState<number>(1);

  // 2. Batch configuration
  const [courseTrack, setCourseTrack] = useState<string>('DA');
  const [customTrackName, setCustomTrackName] = useState<string>('');
  const [totalDays, setTotalDays] = useState<number>(50);
  const [startDate, setStartDate] = useState<string>('2026-06-01');
  const [startTime, setStartTime] = useState<string>('10:00 AM');
  const [endTime, setEndTime] = useState<string>('01:30 PM');
  const [dailyHours, setDailyHours] = useState<number>(3.5);
  const [mentorId, setMentorId] = useState<number>(2);

  // 3. Daily Day-Wise Sheet Configuration (1 or 2 pages per day)
  const [selectedDay, setSelectedDay] = useState<number>(1);
  const [layoutMode, setLayoutMode] = useState<'1_page_per_day' | '2_pages_per_day'>('1_page_per_day');

  // 4. Students list (defaults to 5 clean students)
  const [students, setStudents] = useState<BatchStudent[]>([]);

  // 5. View Mode: 'roster' | 'daily_sheet' | 'matrix_preview'
  const [activeTab, setActiveTab] = useState<'daily_sheet' | 'roster' | 'matrix_preview'>('daily_sheet');

  // 6. Preview response state
  const [previewData, setPreviewData] = useState<any>(null);
  const [loadingPreview, setLoadingPreview] = useState<boolean>(false);
  const [isGeneratingDailyBook, setIsGeneratingDailyBook] = useState<boolean>(false);
  const [isGeneratingDayPdf, setIsGeneratingDayPdf] = useState<boolean>(false);
  const [isGeneratingMatrixPdf, setIsGeneratingMatrixPdf] = useState<boolean>(false);
  const [isGeneratingZip, setIsGeneratingZip] = useState<boolean>(false);
  const [isEnrolling, setIsEnrolling] = useState<boolean>(false);
  const [statusMessage, setStatusMessage] = useState<{ type: 'success' | 'error' | 'info'; text: string } | null>(null);

  // 7. Bulk Quick Paste Modal State
  const [showPasteModal, setShowPasteModal] = useState<boolean>(false);
  const [pasteText, setPasteText] = useState<string>('');

  // 8. Reset Database Confirmation Modal State
  const [showResetDbModal, setShowResetDbModal] = useState<boolean>(false);
  const [isResettingDb, setIsResettingDb] = useState<boolean>(false);

  // Initialize with 5 students on first render
  useEffect(() => {
    loadSampleStudents(5, 100);
  }, []);

  // When switching institution, adjust default mentor and course track
  const handleInstitutionChange = (id: number) => {
    setInstitutionId(id);
    if (id === 2) {
      // Poswal Developers -> Solar track & Mahesh Chand Saini
      setCourseTrack('SOL-01');
      setMentorId(1);
    } else {
      // Poddar College -> Data Analytics & Krishlay
      setCourseTrack('DA');
      setMentorId(2);
    }
  };

  const loadSampleStudents = (count = 5, defaultPct = 100) => {
    const list: BatchStudent[] = [];
    const prefix = institutionId === 2 ? 'POSWAL-2026' : 'PCTM-2026';
    const college = institutionId === 2 ? 'Poswal Developers Training Division' : 'Poddar College, Bharatpur';

    for (let i = 0; i < count; i++) {
      const name = SAMPLE_NAMES[i % SAMPLE_NAMES.length];
      list.push({
        id: `stu_${Date.now()}_${i}`,
        full_name: count > SAMPLE_NAMES.length ? `${name} (${i + 1})` : name,
        father_mother_name: `Mr. ${name.split(' ')[1] || 'Kumar'} Sharma`,
        roll_no: `${prefix}-${String(i + 1).padStart(3, '0')}`,
        college_name: college,
        degree: institutionId === 2 ? 'Diploma / B.Tech' : 'BCA',
        branch: institutionId === 2 ? 'Electrical & Solar' : 'Computer Science',
        attendance_pct: defaultPct
      });
    }
    setStudents(list);
    setStatusMessage({ type: 'info', text: `Loaded ${count} students with ${defaultPct}% attendance.` });
  };

  const handleClearAllStudents = () => {
    setStudents([]);
    setPreviewData(null);
    setStatusMessage({ type: 'info', text: 'Cleared student roster.' });
  };

  const setAllAttendance = (pct: number) => {
    setStudents(prev => prev.map(s => ({ ...s, attendance_pct: pct, day_overrides: undefined })));
    setStatusMessage({ type: 'info', text: `All ${students.length} students set to ${pct}% attendance.` });
    if (previewData) {
      setTimeout(() => fetchLivePreview(), 50);
    }
  };

  const randomizeAttendance = () => {
    setStudents(prev => prev.map(s => {
      const pcts = [100, 100, 96, 94, 92, 90, 88, 100, 98, 95];
      const randomPct = pcts[Math.floor(Math.random() * pcts.length)];
      return { ...s, attendance_pct: randomPct, day_overrides: undefined };
    }));
    setStatusMessage({ type: 'info', text: `Randomized attendance realistically (88% - 100%) across ${students.length} students.` });
    if (previewData) {
      setTimeout(() => fetchLivePreview(), 50);
    }
  };

  const handleAddStudent = () => {
    const prefix = institutionId === 2 ? 'POSWAL-2026' : 'PCTM-2026';
    const college = institutionId === 2 ? 'Poswal Developers Training Division' : 'Poddar College, Bharatpur';
    const newIdx = students.length + 1;
    const newStudent: BatchStudent = {
      id: `stu_${Date.now()}_${newIdx}`,
      full_name: `Student Name ${newIdx}`,
      father_mother_name: 'Father Name',
      roll_no: `${prefix}-${String(newIdx).padStart(3, '0')}`,
      college_name: college,
      degree: institutionId === 2 ? 'Diploma / B.Tech' : 'BCA',
      branch: institutionId === 2 ? 'Electrical & Solar' : 'Computer Science',
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

  const toggleStudentDay = (studentIdx: number, dayNumber: number) => {
    const updatedStudents = [...students];
    const stu = { ...updatedStudents[studentIdx] };
    const overrides = { ...(stu.day_overrides || {}) };

    let currentStatus = 'PRESENT';
    if (overrides[dayNumber]) {
      currentStatus = overrides[dayNumber];
    } else if (previewData?.students?.[studentIdx]?.records?.[dayNumber - 1]) {
      currentStatus = previewData.students[studentIdx].records[dayNumber - 1].status;
    } else if (stu.attendance_pct < 100) {
      currentStatus = 'PRESENT';
    }

    const nextStatus: 'PRESENT' | 'LEAVE' = currentStatus === 'PRESENT' ? 'LEAVE' : 'PRESENT';
    overrides[dayNumber] = nextStatus;
    stu.day_overrides = overrides;
    updatedStudents[studentIdx] = stu;
    setStudents(updatedStudents);

    if (previewData && previewData.students && previewData.students[studentIdx]) {
      const updatedPreview = { ...previewData };
      const studentPreview = { ...updatedPreview.students[studentIdx] };
      const records = [...studentPreview.records];
      if (records[dayNumber - 1]) {
        records[dayNumber - 1] = {
          ...records[dayNumber - 1],
          status: nextStatus === 'PRESENT' ? 'PRESENT' : 'AUTHORIZED LEAVE',
          short_status: nextStatus === 'PRESENT' ? 'P' : 'L'
        };
        studentPreview.records = records;
        const presentCount = records.filter(r => r.status === 'PRESENT').length;
        const leaveCount = records.length - presentCount;
        studentPreview.present_days = presentCount;
        studentPreview.leave_days = leaveCount;
        studentPreview.attendance_pct_actual = Math.round((presentCount / records.length) * 1000) / 10;
        updatedPreview.students[studentIdx] = studentPreview;
        setPreviewData(updatedPreview);
      }
    }
  };

  const setAllStudentsOnDay = (dayNumber: number, status: 'PRESENT' | 'LEAVE') => {
    const updatedStudents = students.map(stu => {
      const overrides = { ...(stu.day_overrides || {}) };
      overrides[dayNumber] = status;
      return { ...stu, day_overrides: overrides };
    });
    setStudents(updatedStudents);
    setStatusMessage({
      type: 'info',
      text: `Marked all ${students.length} students as ${status} on Day ${dayNumber}.`
    });
    setTimeout(() => fetchLivePreview(), 50);
  };

  const resetStudentOverrides = (studentIdx: number) => {
    const updatedStudents = [...students];
    updatedStudents[studentIdx] = {
      ...updatedStudents[studentIdx],
      day_overrides: undefined
    };
    setStudents(updatedStudents);
    setStatusMessage({
      type: 'info',
      text: `Reset custom day overrides for ${updatedStudents[studentIdx].full_name}.`
    });
    setTimeout(() => fetchLivePreview(), 50);
  };

  const handleBulkPaste = () => {
    if (!pasteText.trim()) return;
    const lines = pasteText.split(/\r?\n/).map(l => l.trim()).filter(Boolean);
    const prefix = institutionId === 2 ? 'POSWAL-2026' : 'PCTM-2026';
    const college = institutionId === 2 ? 'Poswal Developers Training Division' : 'Poddar College, Bharatpur';

    const newStudents: BatchStudent[] = lines.map((line, idx) => {
      const parts = line.split(/[\t,|]+/).map(p => p.trim());
      const fullName = parts[0] || `Student ${idx + 1}`;
      const fatherName = parts[1] || 'Father Name';
      const roll = parts[2] || `${prefix}-${String(idx + 1).padStart(3, '0')}`;
      const pct = parseFloat(parts[3]) || 100;

      return {
        id: `stu_${Date.now()}_${idx}`,
        full_name: fullName,
        father_mother_name: fatherName,
        roll_no: roll,
        college_name: college,
        degree: institutionId === 2 ? 'Diploma / B.Tech' : 'BCA',
        branch: institutionId === 2 ? 'Electrical & Solar' : 'Computer Science',
        attendance_pct: pct
      };
    });

    setStudents(newStudents);
    setShowPasteModal(false);
    setPasteText('');
    setStatusMessage({ type: 'success', text: `Successfully imported ${newStudents.length} students!` });
  };

  const getCommonPayload = () => ({
    institution_id: institutionId,
    course_track: courseTrack,
    custom_track_name: customTrackName || undefined,
    total_days: totalDays,
    start_date: startDate,
    start_time: startTime,
    end_time: endTime,
    daily_hours: dailyHours,
    mentor_id: mentorId,
    selected_day: selectedDay,
    layout_mode: layoutMode,
    students: students.map(s => ({
      full_name: s.full_name,
      father_mother_name: s.father_mother_name || 'Father Name',
      roll_no: s.roll_no || '',
      college_name: s.college_name || (institutionId === 2 ? 'Poswal Developers Training Division' : 'Poddar College, Bharatpur'),
      degree: s.degree || (institutionId === 2 ? 'Diploma / B.Tech' : 'BCA'),
      branch: s.branch || (institutionId === 2 ? 'Electrical & Solar' : 'Computer Science'),
      attendance_pct: s.attendance_pct,
      day_overrides: s.day_overrides || undefined
    }))
  });

  const fetchLivePreview = async () => {
    if (students.length === 0) {
      setStatusMessage({ type: 'error', text: 'Please add at least 1 student to generate preview.' });
      return;
    }
    try {
      setLoadingPreview(true);
      const res = await api.bulkAttendancePreview(getCommonPayload());
      setPreviewData(res);
      setStatusMessage({ type: 'success', text: `Live matrix synchronized (${res.students.length} students x ${res.total_days} days).` });
    } catch (err: any) {
      setStatusMessage({ type: 'error', text: err.message || 'Failed to generate preview' });
    } finally {
      setLoadingPreview(false);
    }
  };

  const handleDownloadSingleDayPdf = async () => {
    try {
      setIsGeneratingDayPdf(true);
      setStatusMessage({ type: 'info', text: `Rendering Day ${selectedDay} (${layoutMode === '1_page_per_day' ? '1-Page' : '2-Pages'}) PDF...` });
      await api.downloadDailyDayPdf(getCommonPayload());
      setStatusMessage({ type: 'success', text: `Day ${selectedDay} Attendance Sheet downloaded successfully!` });
    } catch (err: any) {
      setStatusMessage({ type: 'error', text: err.message || 'Failed to generate Day Sheet PDF' });
    } finally {
      setIsGeneratingDayPdf(false);
    }
  };

  const handleDownloadAllDailyBookPdf = async () => {
    try {
      setIsGeneratingDailyBook(true);
      setStatusMessage({ type: 'info', text: `Compiling Complete ${totalDays}-Days Daily Register Book...` });
      await api.downloadDailyBookPdf(getCommonPayload());
      setStatusMessage({ type: 'success', text: `Complete ${totalDays}-Days Daily Register Book downloaded successfully!` });
    } catch (err: any) {
      setStatusMessage({ type: 'error', text: err.message || 'Failed to generate Daily Register Book' });
    } finally {
      setIsGeneratingDailyBook(false);
    }
  };

  const handleDownloadMasterMatrixPdf = async () => {
    try {
      setIsGeneratingMatrixPdf(true);
      setStatusMessage({ type: 'info', text: 'Generating Landscape Master Attendance Register PDF...' });
      await api.downloadMasterAttendancePdf(getCommonPayload());
      setStatusMessage({ type: 'success', text: 'Master Matrix PDF downloaded successfully!' });
    } catch (err: any) {
      setStatusMessage({ type: 'error', text: err.message || 'Failed to generate Master PDF' });
    } finally {
      setIsGeneratingMatrixPdf(false);
    }
  };

  const handleDownloadZipBundle = async () => {
    try {
      setIsGeneratingZip(true);
      setStatusMessage({ type: 'info', text: `Compiling Complete ZIP Archive (${students.length} Student Reports + Day Sheets + Register Book + Master PDF + CSV Matrix)...` });
      await api.downloadBatchAttendanceZip(getCommonPayload());
      setStatusMessage({ type: 'success', text: 'Complete ZIP Archive downloaded successfully!' });
    } catch (err: any) {
      setStatusMessage({ type: 'error', text: err.message || 'Failed to generate ZIP bundle' });
    } finally {
      setIsGeneratingZip(false);
    }
  };

  const handleEnrollAndSave = async () => {
    try {
      setIsEnrolling(true);
      setStatusMessage({ type: 'info', text: 'Enrolling all batch candidates into database...' });
      const res = await api.bulkEnrollStudents(getCommonPayload());
      setStatusMessage({
        type: 'success',
        text: `Enrolled ${res.enrolled_count} students with full 50-day attendance in database!`
      });
    } catch (err: any) {
      setStatusMessage({ type: 'error', text: err.message || 'Failed to enroll batch students' });
    } finally {
      setIsEnrolling(false);
    }
  };

  const handleResetDatabase = async () => {
    try {
      setIsResettingDb(true);
      setStatusMessage({ type: 'info', text: 'Resetting database to pristine clean state...' });
      const res = await api.resetDatabase();
      setShowResetDbModal(false);
      setStatusMessage({
        type: 'success',
        text: `Database wiped clean! (Preserved: Poddar College & Poswal Developers, all courses, faculty & authorities).`
      });
      loadSampleStudents(5, 100);
      setPreviewData(null);
    } catch (err: any) {
      setStatusMessage({ type: 'error', text: err.response?.data?.detail || 'Failed to reset database' });
    } finally {
      setIsResettingDb(false);
    }
  };

  const triggerBlobDownload = (blob: Blob, filename: string) => {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6 pb-24">
      {/* Top Banner & Header */}
      <div className="bg-linear-to-r from-slate-900 via-indigo-950 to-blue-950 p-6 rounded-3xl text-white shadow-xl relative overflow-hidden">
        <div className="absolute -right-10 -bottom-10 opacity-10 pointer-events-none">
          <FileSpreadsheet className="w-80 h-80 text-white" />
        </div>
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-amber-500/20 text-amber-300 text-xs font-semibold mb-2 border border-amber-500/30">
              <Sun className="w-3.5 h-3.5 text-amber-400" />
              <span>Poddar College & Poswal Developers Training Portal</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-serif font-black tracking-tight text-white">
              Bulk Attendance & Day-Wise Register Generator
            </h1>
            <p className="text-xs sm:text-sm text-slate-300 mt-1 max-w-2xl">
              Generate official A4 day-wise attendance sheets (1 or 2 sheets per day) for students across all days with customizable attendance per student, instant click-to-toggle attendance marks, and official authority seal/stamp.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2.5">
            <button
              onClick={() => setShowResetDbModal(true)}
              className="inline-flex items-center space-x-2 px-3.5 py-2 rounded-xl bg-red-900/60 hover:bg-red-800 text-red-200 text-xs font-bold border border-red-700/50 shadow-sm transition-all"
              title="Wipe test data and reset database cleanly"
            >
              <Trash2 className="w-4 h-4 text-red-400" />
              <span>Reset DB</span>
            </button>

            <button
              onClick={fetchLivePreview}
              disabled={loadingPreview}
              className="inline-flex items-center space-x-2 px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs sm:text-sm font-bold shadow-lg shadow-indigo-600/30 transition-all hover:scale-105 active:scale-95 disabled:opacity-50"
            >
              <RefreshCw className={`w-4 h-4 ${loadingPreview ? 'animate-spin' : ''}`} />
              <span>{loadingPreview ? 'Computing...' : 'Generate Matrix Preview'}</span>
            </button>
          </div>
        </div>
      </div>

      {/* Status Feedback Notification */}
      {statusMessage && (
        <div
          className={`p-4 rounded-2xl text-xs sm:text-sm font-medium flex items-center justify-between shadow-sm transition-all ${
            statusMessage.type === 'success'
              ? 'bg-emerald-50 text-emerald-900 border border-emerald-200'
              : statusMessage.type === 'error'
              ? 'bg-red-50 text-red-900 border border-red-200'
              : 'bg-blue-50 text-blue-900 border border-blue-200'
          }`}
        >
          <div className="flex items-center space-x-2">
            {statusMessage.type === 'success' && <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />}
            {statusMessage.type === 'error' && <Trash2 className="w-4 h-4 text-red-600 shrink-0" />}
            {statusMessage.type === 'info' && <RefreshCw className="w-4 h-4 text-blue-600 shrink-0 animate-spin" />}
            <span>{statusMessage.text}</span>
          </div>
          <button
            onClick={() => setStatusMessage(null)}
            className="text-slate-400 hover:text-slate-600 text-xs font-bold ml-4"
          >
            ✕
          </button>
        </div>
      )}

      {/* 1. Institution Selector (Poddar College vs Poswal Developers) */}
      <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-sm font-bold uppercase tracking-wider text-slate-700 flex items-center space-x-2">
              <Building2 className="w-4 h-4 text-indigo-600" />
              <span>Step 1: Choose Organization / Certification Body</span>
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Select which institutional branding, header, GST/MSME credentials, and official authority will be applied.
            </p>
          </div>
          <span className="text-xs font-bold px-2.5 py-1 rounded-full bg-indigo-50 text-indigo-700 border border-indigo-200">
            Active: {institutionId === 2 ? 'Poswal Developers' : 'Poddar College'}
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Card 1: Poddar College */}
          <div
            onClick={() => handleInstitutionChange(1)}
            className={`p-4 rounded-xl border-2 cursor-pointer transition-all ${
              institutionId === 1
                ? 'border-indigo-600 bg-indigo-50/50 shadow-md ring-2 ring-indigo-500/20'
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
                  <p className="text-xs text-slate-500">Bharatpur, Rajasthan | Phone: 9414293370</p>
                </div>
              </div>
              {institutionId === 1 && (
                <CheckCircle2 className="w-5 h-5 text-indigo-600" />
              )}
            </div>
            <div className="mt-3 grid grid-cols-2 gap-2 text-[11px] text-slate-600 bg-white/80 p-2.5 rounded-lg border border-slate-100">
              <div><span className="font-semibold text-slate-700">Authority:</span> Nitin Agarwal (Authority)</div>
              <div><span className="font-semibold text-slate-700">Faculty:</span> Krishlay / Rahul</div>
              <div><span className="font-semibold text-slate-700">Ref Code:</span> PCTM/BPT/DAILY-ATT</div>
              <div><span className="font-semibold text-slate-700">Email:</span> nitin@pctm</div>
            </div>
          </div>

          {/* Card 2: Poswal Developers */}
          <div
            onClick={() => handleInstitutionChange(2)}
            className={`p-4 rounded-xl border-2 cursor-pointer transition-all ${
              institutionId === 2
                ? 'border-amber-600 bg-amber-50/50 shadow-md ring-2 ring-amber-500/20'
                : 'border-slate-200 bg-white hover:border-slate-300'
            }`}
          >
            <div className="flex items-start justify-between">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 rounded-lg bg-amber-800 text-white flex items-center justify-center font-black text-xs shadow-sm">
                  PD
                </div>
                <div>
                  <h3 className="font-bold text-slate-900 text-sm">Poswal Developers</h3>
                  <p className="text-xs text-slate-500">Solar Power & Industrial Development (Mob: 9414694727)</p>
                </div>
              </div>
              {institutionId === 2 && (
                <CheckCircle2 className="w-5 h-5 text-amber-600" />
              )}
            </div>
            <div className="mt-3 grid grid-cols-2 gap-2 text-[11px] text-slate-600 bg-white/80 p-2.5 rounded-lg border border-slate-100">
              <div><span className="font-semibold text-slate-700">Authority:</span> Madhuvan Singh Gurjar</div>
              <div><span className="font-semibold text-slate-700">Trainer:</span> Mahesh Chand Saini</div>
              <div><span className="font-semibold text-slate-700">GST No:</span> 08ABIFP2454N1ZQ</div>
              <div><span className="font-semibold text-slate-700">MSME Udyam:</span> UDYAM-RJ-06-0052498</div>
            </div>
          </div>
        </div>
      </div>

      {/* 2. Batch Track & Schedule Configuration */}
      <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-4">
        <h2 className="text-sm font-bold uppercase tracking-wider text-slate-700 flex items-center space-x-2">
          <Calendar className="w-4 h-4 text-indigo-600" />
          <span>Step 2: Training Track & Schedule Parameters</span>
        </h2>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Track Selection */}
          <div className="sm:col-span-2">
            <label className="block text-xs font-bold text-slate-700 mb-1">
              Program / Specialization Track
            </label>
            <select
              value={courseTrack}
              onChange={(e) => setCourseTrack(e.target.value)}
              className="w-full text-xs font-semibold px-3 py-2.5 bg-slate-50 border border-slate-300 rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none"
            >
              {COURSE_TRACKS.map(t => (
                <option key={t.code} value={t.code}>
                  [{t.code}] {t.title}
                </option>
              ))}
            </select>
          </div>

          {/* Total Days */}
          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1">
              Total Duration Days
            </label>
            <input
              type="number"
              min={1}
              max={120}
              value={totalDays}
              onChange={(e) => setTotalDays(Math.max(1, parseInt(e.target.value) || 1))}
              className="w-full text-xs font-semibold px-3 py-2.5 bg-slate-50 border border-slate-300 rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none"
            />
          </div>

          {/* Start Date */}
          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1">
              Batch Commencement Date
            </label>
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="w-full text-xs font-semibold px-3 py-2.5 bg-slate-50 border border-slate-300 rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none"
            />
          </div>

          {/* Daily Timing */}
          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1">
              Daily Timing Window
            </label>
            <div className="grid grid-cols-2 gap-1.5">
              <input
                type="text"
                value={startTime}
                onChange={(e) => setStartTime(e.target.value)}
                placeholder="10:00 AM"
                className="text-xs px-2 py-2 bg-slate-50 border border-slate-300 rounded-lg text-center"
              />
              <input
                type="text"
                value={endTime}
                onChange={(e) => setEndTime(e.target.value)}
                placeholder="01:30 PM"
                className="text-xs px-2 py-2 bg-slate-50 border border-slate-300 rounded-lg text-center"
              />
            </div>
          </div>

          {/* Daily Hours */}
          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1">
              Daily Hours Logged
            </label>
            <input
              type="number"
              step={0.5}
              min={1}
              max={8}
              value={dailyHours}
              onChange={(e) => setDailyHours(parseFloat(e.target.value) || 3.5)}
              className="w-full text-xs font-semibold px-3 py-2.5 bg-slate-50 border border-slate-300 rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none"
            />
          </div>

          {/* Trainer / Mentor */}
          <div className="sm:col-span-2">
            <label className="block text-xs font-bold text-slate-700 mb-1">
              {institutionId === 2 ? 'Lead Technical Trainer' : 'Supervising Faculty Guide'}
            </label>
            <select
              value={mentorId}
              onChange={(e) => setMentorId(parseInt(e.target.value))}
              className="w-full text-xs font-semibold px-3 py-2.5 bg-slate-50 border border-slate-300 rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none"
            >
              <option value={1}>Mahesh Chand Saini (Trainer - Solar Energy & Power Systems)</option>
              <option value={2}>Krishlay (Faculty - Computing, Data Science & AI)</option>
              <option value={3}>Rahul (Faculty - Digital Technologies & Web Engineering)</option>
            </select>
          </div>
        </div>
      </div>

      {/* 3. Student Roster Quick Bar (Easy Entry) */}
      <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h2 className="text-sm font-bold uppercase tracking-wider text-slate-700 flex items-center space-x-2">
              <Users className="w-4 h-4 text-indigo-600" />
              <span>Step 3: Student Candidates ({students.length} Registered)</span>
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Easily add individual students, paste a batch list, or quickly load sample presets.
            </p>
          </div>

          {/* Quick Roster Action Buttons */}
          <div className="flex flex-wrap items-center gap-2">
            <button
              onClick={handleAddStudent}
              className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold shadow-xs transition-colors"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Add Student</span>
            </button>

            <button
              onClick={() => setShowPasteModal(true)}
              className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold border border-slate-300 transition-colors"
            >
              <ClipboardPaste className="w-3.5 h-3.5 text-slate-600" />
              <span>Paste Names</span>
            </button>

            <div className="h-4 w-px bg-slate-300 mx-1 hidden sm:block" />

            <button
              onClick={() => loadSampleStudents(5, 100)}
              className="px-2.5 py-1.5 rounded-lg bg-amber-50 hover:bg-amber-100 text-amber-800 text-xs font-bold border border-amber-200 transition-colors"
            >
              Load 5
            </button>

            <button
              onClick={() => loadSampleStudents(25, 100)}
              className="px-2.5 py-1.5 rounded-lg bg-amber-50 hover:bg-amber-100 text-amber-800 text-xs font-bold border border-amber-200 transition-colors"
            >
              Load 25
            </button>

            <button
              onClick={() => loadSampleStudents(50, 100)}
              className="px-2.5 py-1.5 rounded-lg bg-amber-50 hover:bg-amber-100 text-amber-800 text-xs font-bold border border-amber-200 transition-colors"
            >
              Load 50
            </button>

            <button
              onClick={handleClearAllStudents}
              className="px-2.5 py-1.5 rounded-lg bg-red-50 hover:bg-red-100 text-red-700 text-xs font-bold border border-red-200 transition-colors"
            >
              Clear
            </button>
          </div>
        </div>

        {/* Global Attendance Quick Sliders */}
        <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 flex flex-wrap items-center justify-between gap-3 text-xs">
          <div className="flex items-center space-x-2 text-slate-700 font-semibold">
            <Percent className="w-4 h-4 text-indigo-600" />
            <span>Set All Attendance To:</span>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <button
              onClick={() => setAllAttendance(100)}
              className="px-3 py-1 rounded-md bg-emerald-600 text-white font-bold hover:bg-emerald-700 transition-colors shadow-2xs"
            >
              100% (No Leave)
            </button>
            <button
              onClick={() => setAllAttendance(95)}
              className="px-3 py-1 rounded-md bg-blue-600 text-white font-bold hover:bg-blue-700 transition-colors shadow-2xs"
            >
              95% Attendance
            </button>
            <button
              onClick={() => setAllAttendance(90)}
              className="px-3 py-1 rounded-md bg-indigo-600 text-white font-bold hover:bg-indigo-700 transition-colors shadow-2xs"
            >
              90% Attendance
            </button>
            <button
              onClick={randomizeAttendance}
              className="px-3 py-1 rounded-md bg-amber-600 text-white font-bold hover:bg-amber-700 transition-colors shadow-2xs"
            >
              Realistic Random (88-100%)
            </button>
          </div>
        </div>
      </div>

      {/* 4. Tab Navigation Bar (Daily Day Sheet | Student Roster | Master Matrix) */}
      <div className="flex border-b border-slate-200 bg-white rounded-t-2xl px-4 pt-3 space-x-3 shadow-xs">
        <button
          onClick={() => setActiveTab('daily_sheet')}
          className={`pb-3 px-3 text-xs sm:text-sm font-bold flex items-center space-x-2 border-b-2 transition-colors ${
            activeTab === 'daily_sheet'
              ? 'border-indigo-600 text-indigo-600'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <Calendar className="w-4 h-4" />
          <span>Tab 1: Daily Day Sheets (A4 Day-by-Day)</span>
        </button>

        <button
          onClick={() => setActiveTab('roster')}
          className={`pb-3 px-3 text-xs sm:text-sm font-bold flex items-center space-x-2 border-b-2 transition-colors ${
            activeTab === 'roster'
              ? 'border-indigo-600 text-indigo-600'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <Users className="w-4 h-4" />
          <span>Tab 2: Roster Editor ({students.length} Students)</span>
        </button>

        <button
          onClick={() => setActiveTab('matrix_preview')}
          className={`pb-3 px-3 text-xs sm:text-sm font-bold flex items-center space-x-2 border-b-2 transition-colors ${
            activeTab === 'matrix_preview'
              ? 'border-indigo-600 text-indigo-600'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <FileSpreadsheet className="w-4 h-4" />
          <span>Tab 3: Master Attendance Matrix (All Days)</span>
        </button>
      </div>

      {/* Tab 1: Daily Day Sheet Generator View */}
      {activeTab === 'daily_sheet' && (
        <div className="bg-white p-6 rounded-b-2xl border border-slate-200 shadow-sm space-y-6">
          {/* Day Selector & Page Layout Controls */}
          <div className="p-4 rounded-2xl bg-indigo-50/70 border border-indigo-200 flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div className="flex flex-wrap items-center gap-3">
              <span className="text-xs font-bold uppercase tracking-wider text-indigo-950">Select Day:</span>
              <div className="flex items-center space-x-1 overflow-x-auto max-w-md py-1">
                {Array.from({ length: Math.min(totalDays, 50) }, (_, i) => i + 1).map(day => (
                  <button
                    key={day}
                    onClick={() => setSelectedDay(day)}
                    className={`px-2.5 py-1 rounded-lg text-xs font-bold transition-all ${
                      selectedDay === day
                        ? 'bg-indigo-600 text-white shadow-xs scale-105'
                        : 'bg-white text-slate-700 hover:bg-indigo-100 border border-indigo-100'
                    }`}
                  >
                    D{day}
                  </button>
                ))}
              </div>
            </div>

            {/* Layout Mode Selector (1 vs 2 Pages per Day) */}
            <div className="flex items-center space-x-3 text-xs">
              <span className="font-bold text-slate-700">Format:</span>
              <div className="inline-flex rounded-xl bg-white p-1 border border-slate-300">
                <button
                  onClick={() => setLayoutMode('1_page_per_day')}
                  className={`px-3 py-1 rounded-lg font-bold transition-colors ${
                    layoutMode === '1_page_per_day'
                      ? 'bg-indigo-600 text-white shadow-xs'
                      : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  1 Sheet / Day (Standard)
                </button>
                <button
                  onClick={() => setLayoutMode('2_pages_per_day')}
                  className={`px-3 py-1 rounded-lg font-bold transition-colors ${
                    layoutMode === '2_pages_per_day'
                      ? 'bg-indigo-600 text-white shadow-xs'
                      : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  2 Sheets / Day (Spacious)
                </button>
              </div>
            </div>
          </div>

          {/* Quick Actions on Day X */}
          <div className="flex flex-wrap items-center justify-between gap-3 text-xs bg-slate-50 p-3 rounded-xl border border-slate-200">
            <div className="flex items-center space-x-2 text-slate-700">
              <span className="font-bold">Day {selectedDay} Quick Actions:</span>
              <span className="text-slate-500">(Click any status badge below to toggle individual attendance)</span>
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setAllStudentsOnDay(selectedDay, 'PRESENT')}
                className="px-2.5 py-1 rounded bg-emerald-100 hover:bg-emerald-200 text-emerald-800 font-bold border border-emerald-300"
              >
                Mark All Present on Day {selectedDay}
              </button>
              <button
                onClick={() => setAllStudentsOnDay(selectedDay, 'LEAVE')}
                className="px-2.5 py-1 rounded bg-red-100 hover:bg-red-200 text-red-800 font-bold border border-red-300"
              >
                Mark All Leave on Day {selectedDay}
              </button>
            </div>
          </div>

          {/* Student Table for Selected Day */}
          <div className="overflow-x-auto rounded-xl border border-slate-200">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-100 text-slate-700 font-bold uppercase tracking-wider text-[11px] border-b border-slate-200">
                <tr>
                  <th className="p-3 w-12 text-center">S.No</th>
                  <th className="p-3">Student Name</th>
                  <th className="p-3">Roll Number</th>
                  <th className="p-3">Degree & Branch</th>
                  <th className="p-3 text-center">Day {selectedDay} Status</th>
                  <th className="p-3 text-center">Cumulative %</th>
                  <th className="p-3 text-center">Student Signature</th>
                  <th className="p-3 text-center">Trainer Verification</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200 font-medium">
                {students.map((s, idx) => {
                  const override = s.day_overrides?.[selectedDay];
                  const previewRec = previewData?.students?.[idx]?.records?.[selectedDay - 1];
                  const isPresent = override ? (override === 'PRESENT') : (previewRec ? previewRec.status === 'PRESENT' : true);

                  return (
                    <tr key={s.id} className="hover:bg-slate-50 transition-colors">
                      <td className="p-3 text-center text-slate-500 font-bold">{idx + 1}</td>
                      <td className="p-3 font-bold text-slate-900">{s.full_name}</td>
                      <td className="p-3 font-mono text-slate-600">{s.roll_no}</td>
                      <td className="p-3 text-slate-600">{s.degree} ({s.branch})</td>
                      <td className="p-3 text-center">
                        <button
                          onClick={() => toggleStudentDay(idx, selectedDay)}
                          className={`px-3 py-1 rounded-full text-[11px] font-bold inline-flex items-center space-x-1 shadow-2xs transition-all hover:scale-105 active:scale-95 ${
                            isPresent
                              ? 'bg-emerald-100 hover:bg-emerald-200 text-emerald-800 border border-emerald-300'
                              : 'bg-red-100 hover:bg-red-200 text-red-800 border border-red-300'
                          }`}
                        >
                          {isPresent ? <Check className="w-3 h-3 text-emerald-700" /> : <X className="w-3 h-3 text-red-700" />}
                          <span>{isPresent ? 'PRESENT' : 'LEAVE'}</span>
                        </button>
                      </td>
                      <td className="p-3 text-center font-bold text-slate-700">
                        {previewData?.students?.[idx]?.attendance_pct_actual !== undefined
                          ? `${previewData.students[idx].attendance_pct_actual}%`
                          : `${s.attendance_pct}%`}
                      </td>
                      <td className="p-3 text-center text-[10px] text-slate-500 font-serif italic">
                        Verified (Signed)
                      </td>
                      <td className="p-3 text-center text-[10px] text-emerald-700 font-semibold">
                        ✓ Verified
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {/* Download & Generation Action Bar */}
          <div className="flex flex-wrap items-center justify-between gap-4 p-5 rounded-2xl bg-slate-900 text-white shadow-md">
            <div>
              <h3 className="font-serif font-bold text-base text-amber-400">
                Official PDF Downloads ({institutionId === 2 ? 'Poswal Developers' : 'Poddar College'})
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Download single day sheet, all-days register book, master landscape matrix, or complete ZIP bundle.
              </p>
            </div>

            <div className="flex flex-wrap items-center gap-3">
              <button
                onClick={handleDownloadSingleDayPdf}
                disabled={isGeneratingDayPdf || students.length === 0}
                className="inline-flex items-center space-x-2 px-3.5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold shadow-md transition-all disabled:opacity-50"
              >
                <Download className="w-3.5 h-3.5" />
                <span>Download Day {selectedDay} PDF</span>
              </button>

              <button
                onClick={handleDownloadAllDailyBookPdf}
                disabled={isGeneratingDailyBook || students.length === 0}
                className="inline-flex items-center space-x-2 px-3.5 py-2.5 rounded-xl bg-amber-600 hover:bg-amber-500 text-white text-xs font-bold shadow-md transition-all disabled:opacity-50"
              >
                <BookOpen className="w-3.5 h-3.5" />
                <span>All {totalDays} Days Register Book</span>
              </button>

              <button
                onClick={handleDownloadMasterMatrixPdf}
                disabled={isGeneratingMatrixPdf || students.length === 0}
                className="inline-flex items-center space-x-2 px-3.5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold shadow-md transition-all disabled:opacity-50"
              >
                <FileSpreadsheet className="w-3.5 h-3.5" />
                <span>Master Matrix PDF</span>
              </button>

              <button
                onClick={handleDownloadZipBundle}
                disabled={isGeneratingZip || students.length === 0}
                className="inline-flex items-center space-x-2 px-4 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold shadow-md transition-all disabled:opacity-50"
              >
                <Download className="w-4 h-4" />
                <span>Complete ZIP Bundle</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Tab 2: Roster Editor */}
      {activeTab === 'roster' && (
        <div className="bg-white p-6 rounded-b-2xl border border-slate-200 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-bold text-sm text-slate-800">
              Student Candidates ({students.length} Total)
            </h3>
            <button
              onClick={handleAddStudent}
              className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-indigo-600 text-white text-xs font-bold hover:bg-indigo-700 transition-colors"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Add Candidate</span>
            </button>
          </div>

          <div className="space-y-3">
            {students.map((student, idx) => (
              <div
                key={student.id}
                className="p-4 rounded-xl border border-slate-200 bg-slate-50/60 hover:bg-white hover:border-indigo-200 hover:shadow-xs transition-all flex flex-col md:flex-row md:items-center justify-between gap-3 text-xs"
              >
                <div className="flex items-center space-x-3 w-full md:w-auto">
                  <span className="w-6 text-center font-bold text-slate-400">{idx + 1}.</span>
                  <div className="space-y-1 flex-1">
                    <input
                      type="text"
                      value={student.full_name}
                      onChange={(e) => handleUpdateStudent(student.id, 'full_name', e.target.value)}
                      placeholder="Candidate Full Name"
                      className="font-bold text-slate-900 text-sm bg-transparent border-b border-transparent hover:border-slate-300 focus:border-indigo-500 focus:bg-white px-1.5 py-0.5 rounded outline-none w-full sm:w-64"
                    />
                    <div className="flex flex-wrap items-center gap-2 text-[11px] text-slate-500">
                      <input
                        type="text"
                        value={student.roll_no}
                        onChange={(e) => handleUpdateStudent(student.id, 'roll_no', e.target.value)}
                        placeholder="Roll No"
                        className="font-mono bg-transparent border-b border-transparent hover:border-slate-300 focus:border-indigo-500 focus:bg-white px-1 py-0.5 rounded outline-none w-28"
                      />
                      <span>•</span>
                      <input
                        type="text"
                        value={student.college_name}
                        onChange={(e) => handleUpdateStudent(student.id, 'college_name', e.target.value)}
                        placeholder="College / Institution"
                        className="bg-transparent border-b border-transparent hover:border-slate-300 focus:border-indigo-500 focus:bg-white px-1 py-0.5 rounded outline-none w-48"
                      />
                    </div>
                  </div>
                </div>

                <div className="flex items-center space-x-4">
                  <div className="flex items-center space-x-2">
                    <span className="text-[11px] font-bold text-slate-600">Target %:</span>
                    <input
                      type="number"
                      min={50}
                      max={100}
                      value={student.attendance_pct}
                      onChange={(e) => handleUpdateStudent(student.id, 'attendance_pct', parseFloat(e.target.value) || 100)}
                      className="w-16 px-2 py-1 text-center font-bold text-slate-800 bg-white border border-slate-300 rounded-lg"
                    />
                    {student.day_overrides && Object.keys(student.day_overrides).length > 0 && (
                      <span className="px-1.5 py-0.5 rounded bg-amber-100 text-amber-800 text-[10px] font-bold">
                        {Object.keys(student.day_overrides).length} custom overrides
                      </span>
                    )}
                  </div>

                  <button
                    onClick={() => handleRemoveStudent(student.id)}
                    className="p-1.5 rounded-lg text-slate-400 hover:text-red-600 hover:bg-red-50 transition-colors"
                    title="Remove candidate"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tab 3: Master Attendance Matrix (All Days) */}
      {activeTab === 'matrix_preview' && (
        <div className="bg-white p-6 rounded-b-2xl border border-slate-200 shadow-sm space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div>
              <h3 className="font-bold text-sm text-slate-900">
                Master Matrix ({students.length} Students × {totalDays} Working Days)
              </h3>
              <p className="text-xs text-slate-500">
                Click any cell (D1..D{totalDays}) to toggle P (Present) ↔ L (Leave).
              </p>
            </div>
            <button
              onClick={fetchLivePreview}
              disabled={loadingPreview}
              className="px-3 py-1.5 rounded-lg bg-indigo-600 text-white font-bold text-xs hover:bg-indigo-700 transition-colors flex items-center space-x-1.5"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loadingPreview ? 'animate-spin' : ''}`} />
              <span>Refresh Matrix</span>
            </button>
          </div>

          <div className="overflow-x-auto rounded-xl border border-slate-200 max-h-[500px]">
            <table className="w-full text-left text-[11px] border-collapse">
              <thead className="bg-slate-800 text-white font-bold sticky top-0 z-20">
                <tr>
                  <th className="p-2 w-10 text-center border border-slate-700">#</th>
                  <th className="p-2 w-40 sticky left-0 bg-slate-800 border border-slate-700 z-30">Student</th>
                  {Array.from({ length: totalDays }, (_, i) => i + 1).map(d => (
                    <th key={d} className="p-1.5 text-center border border-slate-700 min-w-8">
                      D{d}
                    </th>
                  ))}
                  <th className="p-2 text-center border border-slate-700 bg-slate-900">Present</th>
                  <th className="p-2 text-center border border-slate-700 bg-slate-900">%</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200 font-medium">
                {students.map((stu, sIdx) => {
                  const studentPreview = previewData?.students?.[sIdx];
                  return (
                    <tr key={stu.id} className="hover:bg-slate-50">
                      <td className="p-2 text-center text-slate-500 font-bold border border-slate-200">{sIdx + 1}</td>
                      <td className="p-2 font-bold text-slate-900 border border-slate-200 sticky left-0 bg-white z-10 truncate max-w-[160px]">
                        {stu.full_name}
                      </td>
                      {Array.from({ length: totalDays }, (_, dIdx) => {
                        const dayNum = dIdx + 1;
                        const rec = studentPreview?.records?.[dIdx];
                        const isLeave = rec ? (rec.status === 'AUTHORIZED LEAVE' || rec.short_status === 'L') : false;

                        return (
                          <td
                            key={dayNum}
                            onClick={() => toggleStudentDay(sIdx, dayNum)}
                            className={`p-1 text-center font-bold cursor-pointer border border-slate-200 transition-colors select-none ${
                              isLeave
                                ? 'bg-red-100 text-red-800 hover:bg-red-200'
                                : 'bg-emerald-50 text-emerald-800 hover:bg-emerald-100'
                            }`}
                            title={`Day ${dayNum}: Click to toggle P/L`}
                          >
                            {isLeave ? 'L' : 'P'}
                          </td>
                        );
                      })}
                      <td className="p-2 text-center font-bold text-slate-800 border border-slate-200 bg-slate-50">
                        {studentPreview?.present_days !== undefined ? `${studentPreview.present_days}d` : `${totalDays}d`}
                      </td>
                      <td className="p-2 text-center font-bold text-emerald-700 border border-slate-200 bg-emerald-50/50">
                        {studentPreview?.attendance_pct_actual !== undefined ? `${studentPreview.attendance_pct_actual}%` : `${stu.attendance_pct}%`}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Quick Paste Modal */}
      {showPasteModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-xl w-full p-6 shadow-2xl border border-slate-200 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="font-bold text-base text-slate-900 flex items-center space-x-2">
                <ClipboardPaste className="w-5 h-5 text-indigo-600" />
                <span>Quick Paste Student Roster</span>
              </h3>
              <button
                onClick={() => setShowPasteModal(false)}
                className="text-slate-400 hover:text-slate-600 text-base font-bold"
              >
                ✕
              </button>
            </div>
            <p className="text-xs text-slate-500">
              Paste student names (one per line). Format: <code className="bg-slate-100 px-1 py-0.5 rounded text-indigo-600">Name [tab/comma] Father Name [tab/comma] Roll No [tab/comma] Attendance%</code>
            </p>
            <textarea
              rows={8}
              value={pasteText}
              onChange={(e) => setPasteText(e.target.value)}
              placeholder={`Aarav Sharma\tMr. Ramesh Sharma\t${institutionId === 2 ? 'POSWAL' : 'PCTM'}-2026-001\t100\nBhavya Gupta\tMr. Suresh Gupta\t${institutionId === 2 ? 'POSWAL' : 'PCTM'}-2026-002\t95`}
              className="w-full font-mono text-xs p-3 bg-slate-50 border border-slate-300 rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none"
            />
            <div className="flex items-center justify-end space-x-3">
              <button
                onClick={() => setShowPasteModal(false)}
                className="px-4 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold"
              >
                Cancel
              </button>
              <button
                onClick={handleBulkPaste}
                disabled={!pasteText.trim()}
                className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold disabled:opacity-50"
              >
                Import Candidates
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Reset Database Modal */}
      {showResetDbModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl border border-red-200 space-y-4">
            <div className="flex items-center space-x-3 text-red-600">
              <div className="w-10 h-10 rounded-full bg-red-100 flex items-center justify-center">
                <Trash2 className="w-5 h-5 text-red-600" />
              </div>
              <h3 className="font-bold text-base text-slate-900">
                Confirm Database Reset
              </h3>
            </div>
            <p className="text-xs text-slate-600 leading-relaxed">
              This will wipe all test student records, internships, daily logs, and certificates.
              <br/><br/>
              <b>Preserved:</b> Poddar College & Poswal Developers organizations, all courses & modules, faculty & authority profiles.
            </p>
            <div className="flex items-center justify-end space-x-3 pt-2">
              <button
                onClick={() => setShowResetDbModal(false)}
                className="px-4 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold"
              >
                Cancel
              </button>
              <button
                onClick={handleResetDatabase}
                disabled={isResettingDb}
                className="px-4 py-2 rounded-xl bg-red-600 hover:bg-red-700 text-white text-xs font-bold shadow-md disabled:opacity-50"
              >
                {isResettingDb ? 'Wiping DB...' : 'Yes, Reset Cleanly'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
