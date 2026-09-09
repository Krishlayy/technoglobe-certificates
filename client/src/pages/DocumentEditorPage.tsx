import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { 
  FileText, Download, Printer, Save, RefreshCw, Award, 
  Sparkles, CheckCircle2, ShieldCheck, User, QrCode
} from 'lucide-react';
import { QRCodeSVG } from 'qrcode.react';
import { api } from '../services/api';
import { Student, CentreSettings, Course, Mentor } from '../types';

export const DocumentEditorPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const [students, setStudents] = useState<Student[]>([]);
  const [settings, setSettings] = useState<CentreSettings | null>(null);
  const [selectedStudentId, setSelectedStudentId] = useState<number | null>(null);
  const [docType, setDocType] = useState<string>(searchParams.get('doc') || 'certificate');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  // Live editable fields
  const [formData, setFormData] = useState({
    student_name: '',
    college_name: 'Poddar College, Bharatpur',
    degree: 'BCA',
    branch: 'Computer Science',
    academic_session: '2025-2026',
    course_name: 'Data Analytics',
    internship_title: 'Course-Based Internship in Data Analytics & Business Intelligence',
    start_date: '2026-06-01',
    end_date: '2026-07-12',
    total_hours: 120,
    duration_weeks: 6,
    project_title: 'Retail Sales Performance & Customer Churn Analytics Dashboard',
    mentor_name: 'Prof. Krishlay Sharma',
    mentor_designation: 'Professor',
    signatory_name: 'Nitin Sir',
    signatory_designation: 'Centre Head & Authorized Signatory',
    issue_date: '2026-07-14',
    certificate_no: 'TG-BPT-DA-2026-0001',
    verification_code: 'VER-TG-DA-98214',
    custom_remarks: 'Exemplary diligence, academic discipline, and technical proficiency demonstrated throughout the training tenure.',
  });

  useEffect(() => {
    Promise.all([api.getStudents(), api.getSettings()]).then(([sData, settData]) => {
      setStudents(sData);
      setSettings(settData);
      if (sData.length > 0) {
        const initId = Number(searchParams.get('student_id')) || sData[0].id;
        setSelectedStudentId(initId);
        loadStudentDetails(initId, sData, settData);
      }
      setLoading(false);
    });
  }, []);

  const loadStudentDetails = (sId: number, sList: Student[], sett: CentreSettings | null) => {
    const st = sList.find((s) => s.id === sId);
    if (st) {
      setFormData((prev) => ({
        ...prev,
        student_name: st.full_name,
        college_name: st.college_name || 'Poddar College, Bharatpur',
        degree: st.degree || 'BCA',
        branch: st.branch || 'Computer Science',
        academic_session: st.academic_session || '2025-2026',
        course_name: st.course_name || 'Data Analytics',
        internship_title: st.internship_title || 'Course-Based Internship',
        start_date: st.start_date || '2026-06-01',
        end_date: st.end_date || '2026-07-12',
        certificate_no: st.certificate_number || 'TG-BPT-DA-2026-0001',
        verification_code: st.verification_code || 'VER-TG-DA-98214',
        mentor_name: st.mentor_name || (sett?.signatory_name || 'Prof. Krishlay Sharma'),
        signatory_name: sett?.signatory_name || 'Nitin Sir',
        signatory_designation: sett?.signatory_designation || 'Centre Head & Authorized Signatory',
      }));
    }
  };

  const handleStudentChange = (id: number) => {
    setSelectedStudentId(id);
    loadStudentDetails(id, students, settings);
  };

  const selectedStudent = students.find((s) => s.id === selectedStudentId);

  // Construct direct verification URL for mobile cameras to open the verification portal
  const verifyUrl = `${window.location.protocol}//${window.location.host}/verify?cert=${encodeURIComponent(formData.certificate_no || '')}&name=${encodeURIComponent(formData.student_name || '')}&course=${encodeURIComponent(formData.course_name || '')}&sem=${encodeURIComponent(`${formData.degree || 'BCA'} (${formData.academic_session || '6th Semester'})`)}&college=${encodeURIComponent(formData.college_name || '')}&ver_id=${encodeURIComponent(formData.verification_code || '')}`;

  const handleDownloadPdf = () => {
    if (!selectedStudent?.internship_id) return;
    const url = api.getDocumentPdfUrl(selectedStudent.internship_id, docType);
    window.open(url, '_blank');
  };

  const handlePrint = () => {
    window.print();
  };

  const inputClass = "w-full px-3 py-2 text-xs rounded-lg border border-slate-300 bg-white text-slate-900 placeholder:text-slate-400 focus:ring-2 focus:ring-blue-600 focus:border-blue-600 font-normal shadow-2xs";

  return (
    <div className="space-y-4 animate-in fade-in duration-300">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-serif font-bold text-slate-900 tracking-tight">
            50/50 Live Document Preview & Editor
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Type adjustments in the left editor and view instant real-time updates on the authentic A4 layout.
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={handlePrint}
            className="inline-flex items-center space-x-1.5 px-3 py-2 rounded-lg border border-slate-300 bg-white text-slate-700 hover:bg-slate-50 text-xs font-semibold shadow-2xs transition-all"
          >
            <Printer className="w-3.5 h-3.5 text-slate-500" />
            <span>Print Preview</span>
          </button>
          <button
            onClick={handleDownloadPdf}
            disabled={!selectedStudent?.internship_id}
            className="inline-flex items-center space-x-1.5 px-4 py-2 rounded-lg bg-brand-700 hover:bg-brand-800 text-white text-xs font-bold shadow-sm transition-all"
          >
            <Download className="w-3.5 h-3.5 text-gold-400" />
            <span>Download Vector PDF</span>
          </button>
        </div>
      </div>

      {/* Selectors Bar */}
      <div className="bg-white rounded-xl border border-slate-200 p-3.5 shadow-2xs grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-[10px] font-bold uppercase tracking-wider text-slate-500 mb-1">
            Active Student Record
          </label>
          <select
            value={selectedStudentId || ''}
            onChange={(e) => handleStudentChange(Number(e.target.value))}
            className="w-full px-3 py-2 text-xs font-bold text-slate-900 border border-slate-300 rounded-lg bg-white focus:ring-2 focus:ring-blue-600"
          >
            {students.map((s) => (
              <option key={s.id} value={s.id}>
                {s.full_name} — {s.course_name} ({s.degree} {s.branch}) {s.is_demo ? '[DEMO]' : ''}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-[10px] font-bold uppercase tracking-wider text-slate-500 mb-1">
            Document Template
          </label>
          <select
            value={docType}
            onChange={(e) => setDocType(e.target.value)}
            className="w-full px-3 py-2 text-xs font-bold text-slate-900 border border-slate-300 rounded-lg bg-white focus:ring-2 focus:ring-blue-600"
          >
            <option value="certificate">14. Certificate of Internship Completion (Landscape)</option>
            <option value="experience">15. Industrial Training & Experience Certificate</option>
            <option value="offer">01. Internship Enrollment & Offer Letter</option>
            <option value="joining">02. Internship Commencement / Joining Report</option>
            <option value="schedule">04. Detailed Training Plan & Weekly Schedule</option>
            <option value="attendance_summary">06. Attendance Summary & Hours Audit Report</option>
            <option value="evaluation">11. Formal Mentor Assessment & Evaluation Rubric</option>
            <option value="performance">12. Comprehensive Internship Performance Report</option>
            <option value="consolidated">Consolidated 25+ Page Academic Dossier</option>
          </select>
        </div>
      </div>

      {/* 50 / 50 Split Screen Container */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">
        {/* LEFT PANE (50%): Form Controls */}
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 space-y-6 overflow-y-auto max-h-[820px]">
          <div className="flex items-center justify-between pb-3 border-b border-slate-200">
            <h2 className="text-sm font-serif font-bold text-slate-900">
              Live Parameter Editor
            </h2>
            <span className="text-[11px] font-mono text-slate-400">INSTANT 2-WAY BINDING</span>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-800 mb-1">Candidate Full Name</label>
              <input
                type="text"
                value={formData.student_name}
                onChange={(e) => setFormData({ ...formData, student_name: e.target.value })}
                className={inputClass}
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-semibold text-slate-800 mb-1">Degree Program</label>
                <input
                  type="text"
                  value={formData.degree}
                  onChange={(e) => setFormData({ ...formData, degree: e.target.value })}
                  className={inputClass}
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-800 mb-1">Branch / Specialization</label>
                <input
                  type="text"
                  value={formData.branch}
                  onChange={(e) => setFormData({ ...formData, branch: e.target.value })}
                  className={inputClass}
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-800 mb-1">
                College / Institution Name (Fixed Franchise)
              </label>
              <input
                type="text"
                readOnly
                value={formData.college_name}
                className="w-full px-3 py-2 text-xs rounded-lg border border-slate-300 bg-slate-100 text-slate-700 font-semibold cursor-not-allowed"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-800 mb-1">Internship Title</label>
              <input
                type="text"
                value={formData.internship_title}
                onChange={(e) => setFormData({ ...formData, internship_title: e.target.value })}
                className={inputClass}
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-semibold text-slate-800 mb-1">Commencement Date</label>
                <input
                  type="date"
                  value={formData.start_date}
                  onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
                  className={inputClass}
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-800 mb-1">Completion Date</label>
                <input
                  type="date"
                  value={formData.end_date}
                  onChange={(e) => setFormData({ ...formData, end_date: e.target.value })}
                  className={inputClass}
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-semibold text-slate-800 mb-1">Total Training Hours</label>
                <input
                  type="number"
                  value={formData.total_hours}
                  onChange={(e) => setFormData({ ...formData, total_hours: Number(e.target.value) })}
                  className={inputClass}
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-800 mb-1">Duration (Weeks)</label>
                <input
                  type="number"
                  value={formData.duration_weeks}
                  onChange={(e) => setFormData({ ...formData, duration_weeks: Number(e.target.value) })}
                  className={inputClass}
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-800 mb-1">Capstone Project Title</label>
              <input
                type="text"
                value={formData.project_title}
                onChange={(e) => setFormData({ ...formData, project_title: e.target.value })}
                className={inputClass}
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-semibold text-slate-800 mb-1">Certificate Number</label>
                <input
                  type="text"
                  value={formData.certificate_no}
                  onChange={(e) => setFormData({ ...formData, certificate_no: e.target.value })}
                  className={inputClass}
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-800 mb-1">Verification Reference</label>
                <input
                  type="text"
                  value={formData.verification_code}
                  onChange={(e) => setFormData({ ...formData, verification_code: e.target.value })}
                  className={inputClass}
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-semibold text-slate-800 mb-1">Industry Mentor Name</label>
                <input
                  type="text"
                  value={formData.mentor_name}
                  onChange={(e) => setFormData({ ...formData, mentor_name: e.target.value })}
                  className={inputClass}
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-800 mb-1">Authorized Signatory</label>
                <input
                  type="text"
                  value={formData.signatory_name}
                  onChange={(e) => setFormData({ ...formData, signatory_name: e.target.value })}
                  className={inputClass}
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-800 mb-1">Statement of Performance</label>
              <textarea
                rows={3}
                value={formData.custom_remarks}
                onChange={(e) => setFormData({ ...formData, custom_remarks: e.target.value })}
                className={inputClass}
              />
            </div>

            {/* Direct Mobile Verification Link Preview Box */}
            <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2 text-xs font-bold text-slate-700">
                  <QrCode className="w-4 h-4 text-purple-600" />
                  <span>Direct Mobile Verification Link (Camera Scannable)</span>
                </div>
                <a
                  href={verifyUrl}
                  target="_blank"
                  rel="noreferrer"
                  className="text-[10px] font-bold text-blue-700 hover:text-blue-800 bg-blue-100 px-2 py-0.5 rounded border border-blue-300 inline-flex items-center space-x-1"
                >
                  <span>Open Verification Portal</span>
                </a>
              </div>
              <p className="text-[11px] text-slate-500">
                Scanning this QR with any mobile phone camera or Google Lens opens the official verified student record directly:
              </p>
              <pre className="text-[10px] bg-white p-2.5 rounded-lg border border-slate-200 text-slate-700 font-mono overflow-x-auto break-all whitespace-pre-wrap">
                {verifyUrl}
              </pre>
            </div>
          </div>
        </div>

        {/* RIGHT PANE (50%): Live A4 Document Preview */}
        <div className="bg-slate-100/90 rounded-2xl border border-slate-300 p-6 flex flex-col items-center justify-center min-h-[820px] shadow-inner overflow-y-auto">
          {/* Certificate Landscape Preview */}
          {docType === 'certificate' ? (
            <div className="w-full max-w-[580px] aspect-[297/210] bg-[#FAF9F5] rounded-xs border-4 border-brand-900 p-5 shadow-2xl relative flex flex-col justify-between text-center select-none">
              {/* Inner Gold Border */}
              <div className="absolute inset-1.5 border border-gold-500 pointer-events-none" />
              
              {/* Header with Official Logo */}
              <div className="space-y-0.5 mt-1 flex flex-col items-center">
                <img src="/technoglobe_logo.png" alt="TechnoGlobe" className="h-7 w-auto object-contain mb-0.5" />
                <h4 className="text-[10px] font-serif font-bold tracking-wider text-brand-700 uppercase">
                  {settings?.centre_name || 'TECHNOGLOBE – BHARATPUR CENTRE'}
                </h4>
                <p className="text-[7.5px] text-slate-500">
                  {settings?.address || 'Poddar College, Bharatpur, Near SP Office, Bharatpur, Rajasthan'} | Website: {settings?.website || 'https://www.technoglobe.co.in'}
                </p>
                <div className="w-48 h-[1px] bg-gold-400 mx-auto mt-0.5" />
              </div>

              {/* Title & Body */}
              <div className="space-y-1.5 my-auto">
                <div className="text-sm font-serif font-black tracking-wider text-brand-900 uppercase">
                  CERTIFICATE OF INTERNSHIP COMPLETION
                </div>
                <div className="text-[10px] italic text-slate-600">
                  This is to certify that
                </div>
                <div className="text-lg font-serif font-bold text-brand-800 tracking-wide underline decoration-gold-400 decoration-1 underline-offset-4">
                  {formData.student_name || 'STUDENT NAME'}
                </div>
                <div className="text-[9px] text-slate-700 font-medium">
                  Student of {formData.college_name} | {formData.degree} ({formData.branch}) | Session: {formData.academic_session}
                </div>
                <div className="text-[9px] text-slate-600 max-w-md mx-auto leading-tight">
                  has successfully completed a course-based industrial training program in
                </div>
                <div className="text-xs font-serif font-bold text-brand-900">
                  {formData.internship_title}
                </div>
                <div className="text-[8.5px] text-slate-600">
                  conducted from <b>{formData.start_date}</b> to <b>{formData.end_date}</b> ({formData.duration_weeks} Weeks, {formData.total_hours} Hours).
                </div>
                <div className="text-[8.5px] font-semibold italic text-brand-800">
                  Capstone Project: "{formData.project_title}"
                </div>
              </div>

              {/* Footer Section: QR Code Box + Signatures */}
              <div className="pt-2 grid grid-cols-12 gap-2 items-end text-left border-t border-slate-200/60 mt-1">
                {/* QR Block (Cols 1-5) */}
                <div className="col-span-5 flex items-center space-x-2 bg-white/95 p-1.5 rounded-sm border border-slate-300">
                  <div className="shrink-0 flex flex-col items-center bg-white p-0.5 rounded border border-slate-200">
                    <QRCodeSVG
                      value={verifyUrl}
                      size={48}
                      level="L"
                      includeMargin={false}
                    />
                    <span className="text-[5px] text-brand-900 font-bold uppercase tracking-tighter mt-0.5">
                      SCAN TO VIEW
                    </span>
                  </div>
                  <div className="text-[7.5px] leading-tight text-slate-700 font-mono">
                    <div className="font-bold text-brand-900">OFFICIAL RECORD</div>
                    <div className="truncate max-w-[120px]">Candidate: {formData.student_name}</div>
                    <div className="truncate max-w-[120px]">Course: {formData.course_name}</div>
                    <div>Cert: {formData.certificate_no}</div>
                    <div className="text-[6.5px] text-emerald-700 font-bold">✓ 100% Offline Verified</div>
                  </div>
                </div>

                {/* Stamp Box (Cols 6-7) */}
                <div className="col-span-2 text-center">
                  <div className="w-14 h-14 mx-auto border border-dashed border-slate-400 rounded-sm flex flex-col items-center justify-center text-[6.5px] text-slate-400 uppercase font-semibold">
                    <span>OFFICIAL</span>
                    <span>CENTRE</span>
                    <span>SEAL</span>
                  </div>
                </div>

                {/* Signatures (Cols 8-12) */}
                <div className="col-span-5 grid grid-cols-2 gap-2 text-center">
                  <div>
                    <div className="h-6" />
                    <div className="border-t border-slate-800 text-[8px] font-bold text-slate-900 pt-0.5">
                      {formData.mentor_name}
                    </div>
                    <div className="text-[7px] text-slate-500 italic">Industry Mentor</div>
                  </div>
                  <div>
                    <div className="h-6" />
                    <div className="border-t border-slate-800 text-[8px] font-bold text-slate-900 pt-0.5">
                      {formData.signatory_name}
                    </div>
                    <div className="text-[7px] text-slate-500 italic">Authorized Signatory</div>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            /* Portrait Document Preview (Offer, Joining, Performance, etc.) */
            <div className="w-full max-w-[500px] aspect-[210/297] bg-white rounded-xs border border-slate-300 p-6 shadow-2xl flex flex-col justify-between text-left text-xs text-slate-800 select-none">
              {/* Official Header */}
              <div className="pb-3 border-b-2 border-brand-900">
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="text-xs font-serif font-black tracking-wider text-brand-900 uppercase">
                      {settings?.org_name || 'TECHNOGLOBE IT SOLUTIONS PVT. LTD.'}
                    </h3>
                    <h4 className="text-[10px] font-serif font-bold text-brand-700 uppercase">
                      {settings?.centre_name || 'TECHNOGLOBE – BHARATPUR CENTRE'}
                    </h4>
                    <p className="text-[7.5px] text-slate-500">
                      {settings?.address || 'Poddar College, Bharatpur, Near SP Office, Bharatpur, Rajasthan'}
                    </p>
                  </div>
                  <div className="text-right text-[8px] font-mono text-slate-500">
                    <div>REF: TG/BPT/2026/001</div>
                    <div>DATE: {formData.issue_date}</div>
                  </div>
                </div>
                <div className="w-full h-1 bg-gold-400 mt-2" />
              </div>

              {/* Document Body */}
              <div className="space-y-3 my-4 text-[10px] leading-relaxed text-slate-700">
                <div className="text-center font-serif font-bold text-xs text-brand-900 uppercase tracking-wide underline decoration-gold-400 underline-offset-4">
                  {docType.toUpperCase().replace('_', ' ')}
                </div>

                <div className="p-2.5 bg-slate-50 rounded border border-slate-200">
                  <div className="font-bold text-slate-900">Candidate: {formData.student_name}</div>
                  <div>Degree & Branch: {formData.degree} ({formData.branch})</div>
                  <div>Institution: {formData.college_name}</div>
                  <div>Training Period: {formData.start_date} to {formData.end_date} ({formData.total_hours} Hours)</div>
                </div>

                <p>
                  This official document verifies that <b>{formData.student_name}</b> has fulfilled the prescribed curriculum requirements for <b>{formData.internship_title}</b> at our authorized centre.
                </p>

                <p>
                  <b>Capstone Project:</b> <i>"{formData.project_title}"</i><br />
                  <b>Performance Determination:</b> {formData.custom_remarks}
                </p>
              </div>

              {/* Signature Section */}
              <div className="pt-4 border-t border-slate-200 grid grid-cols-2 gap-6 text-center text-[9px]">
                <div>
                  <div className="h-8" />
                  <div className="border-t border-slate-800 font-bold text-slate-900 pt-1">
                    {formData.mentor_name}
                  </div>
                  <div className="text-[7.5px] text-slate-500 italic">{formData.mentor_designation}</div>
                </div>
                <div>
                  <div className="h-8" />
                  <div className="border-t border-slate-800 font-bold text-slate-900 pt-1">
                    {formData.signatory_name}
                  </div>
                  <div className="text-[7.5px] text-slate-500 italic">{formData.signatory_designation}</div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
