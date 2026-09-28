import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { 
  FileText, CheckCircle2, AlertCircle, Printer, Download, Award, 
  CalendarCheck, BookOpen, FolderKanban, ShieldCheck, Lock, Unlock, 
  ExternalLink, ArrowLeft, Loader2, Save, Sparkles, Building2, User, 
  PackageOpen, Check, AlertTriangle
} from 'lucide-react';
import { QRCodeSVG } from 'qrcode.react';
import { api } from '../services/api';
import { ProgressStepper } from '../components/common/ProgressStepper';
import { DocumentModal } from '../components/documents/DocumentModal';
import { ComplianceCheckResult } from '../types';

export const StudentDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const internshipId = Number(id);

  const [ctx, setCtx] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'documents' | 'compliance' | 'attendance' | 'logs' | 'project' | 'evaluation' | 'certificate'>('documents');
  const [complianceCheck, setComplianceCheck] = useState<ComplianceCheckResult | null>(null);
  const [finalizing, setFinalizing] = useState(false);
  const [saveMessage, setSaveMessage] = useState('');

  // Modal State
  const [modalOpen, setModalOpen] = useState(false);
  const [activeDoc, setActiveDoc] = useState<{ type: string; title: string }>({ type: 'offer', title: 'Offer Letter' });

  // Form states for active tabs
  const [complianceForm, setComplianceForm] = useState<any>({});
  const [projectForm, setProjectForm] = useState<{ project_title: string; fields: Record<string, any>; status: string }>({
    project_title: '',
    fields: {},
    status: 'IN_PROGRESS'
  });
  const [evalForm, setEvalForm] = useState<any>({
    mentor_id: 1,
    criteria_scores: {},
    overall_score: 90,
    final_remark: ''
  });

  useEffect(() => {
    loadData();
  }, [internshipId]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [detailData, checkData] = await Promise.all([
        api.getInternship(internshipId),
        api.getComplianceCheck(internshipId)
      ]);
      setCtx(detailData);
      setComplianceCheck(checkData);
      setComplianceForm(detailData.compliance || {});
      setProjectForm({
        project_title: detailData.project?.project_title || '',
        fields: detailData.project_fields || {},
        status: detailData.project?.status || 'IN_PROGRESS'
      });
      setEvalForm({
        mentor_id: detailData.evaluation?.mentor_id || detailData.internship.mentor_id,
        criteria_scores: detailData.eval_criteria || {},
        overall_score: detailData.evaluation?.overall_score || 90,
        final_remark: detailData.evaluation?.final_remark || ''
      });
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleFinalize = async () => {
    if (!complianceCheck?.is_ready_for_finalization) {
      alert("Cannot finalize: Please ensure all compliance checklist items are completed.");
      return;
    }
    if (!window.confirm("Are you sure you want to finalize and officially lock this certificate? Once finalized, official certificate numbering is assigned.")) {
      return;
    }
    setFinalizing(true);
    try {
      await api.finalizeCertificate(internshipId);
      await loadData();
      alert("Certificate officially finalized and locked!");
    } catch (err: any) {
      alert(err.message || "Failed to finalize certificate");
    } finally {
      setFinalizing(false);
    }
  };

  const handleSaveCompliance = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.updateCompliance(internshipId, complianceForm);
      setSaveMessage('Compliance records updated successfully!');
      setTimeout(() => setSaveMessage(''), 3000);
      loadData();
    } catch (err: any) {
      alert(err.message || 'Failed to update compliance');
    }
  };

  const handleSaveProject = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.saveProject(internshipId, projectForm);
      setSaveMessage('Capstone project record updated successfully!');
      setTimeout(() => setSaveMessage(''), 3000);
      loadData();
    } catch (err: any) {
      alert(err.message || 'Failed to update project');
    }
  };

  const handleSaveEvaluation = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.saveEvaluation(internshipId, evalForm);
      setSaveMessage('Mentor evaluation rubric saved successfully!');
      setTimeout(() => setSaveMessage(''), 3000);
      loadData();
    } catch (err: any) {
      alert(err.message || 'Failed to save evaluation');
    }
  };

  const openDocPreview = (type: string, title: string) => {
    setActiveDoc({ type, title });
    setModalOpen(true);
  };

  if (loading || !ctx) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh] text-slate-500">
        <Loader2 className="w-8 h-8 animate-spin text-brand-600 mb-2" />
        <p className="text-xs font-medium">Loading student records & documents...</p>
      </div>
    );
  }

  const { internship: it, settings: s, compliance: comp, att_stats: stats } = ctx;

  const docList = [
    { type: "offer", title: "01. Offer & Enrollment Letter", desc: "Formal admission and program specifications" },
    { type: "joining", title: "02. Joining & Commencement Report", desc: "Official confirmation of reporting to centre" },
    { type: "syllabus", title: "03. Course Syllabus & Curriculum", desc: "Structured module outline and competencies" },
    { type: "schedule", title: "04. Training Schedule & Deliverables", desc: "Week-by-week timeline and practical deliverables" },
    { type: "attendance_sheet", title: "05. Attendance Register", desc: "Daily time-in/out and activity log sheet" },
    { type: "attendance_summary", title: "06. Attendance Summary Audit", desc: "Verified percentage and training hours report" },
    { type: "daily_log", title: "07. Daily Internship Logbook", desc: "Comprehensive diary of daily tasks and outcomes" },
    { type: "weekly_report", title: "08. Weekly Progress Report", desc: "Weekly review, project milestones and mentor remarks" },
    { type: "project_assignment", title: "09. Project Assignment Brief", desc: "Capstone scope, objective, and requirements" },
    { type: "project_report", title: "10. Project Technical Report", desc: "Complete technical findings, charts, and analysis" },
    { type: "evaluation", title: "11. Mentor Evaluation Form", desc: "9-criteria performance rubric scored out of 100" },
    { type: "performance", title: "12. Performance Summary Report", desc: "Consolidated completion status and grade" },
    { type: "feedback", title: "13. Student Feedback Form", desc: "Authentic student appraisal of course and mentor" },
    { type: "certificate", title: "14. Completion Certificate", desc: "A4 Landscape Security Certificate with QR Code" },
    { type: "experience", title: "15. Experience / Training Certificate", desc: "A4 Portrait formal industrial training credential" },
    { type: "consolidated", title: "Complete Academic Report", desc: "Bound 25+ page complete university submission report" },
  ];

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Back button & Title Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="space-y-1">
          <Link
            to="/students"
            className="inline-flex items-center space-x-1 text-xs font-semibold text-slate-500 hover:text-slate-800 transition-colors"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Back to Student Directory</span>
          </Link>
          <div className="flex items-center space-x-3">
            <h1 className="text-2xl font-serif font-bold text-slate-900 tracking-tight">
              {it.student_name}
            </h1>
            <span className={`px-2.5 py-0.5 rounded-full text-xs font-bold ${
              it.status === 'CERTIFIED' ? 'bg-emerald-100 text-emerald-800 border border-emerald-300' : 'bg-blue-100 text-blue-800 border border-blue-300'
            }`}>
              {it.status}
            </span>
            {it.is_locked === 1 && (
              <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-full text-[11px] font-semibold bg-slate-100 text-slate-700 border border-slate-300">
                <Lock className="w-3 h-3 text-slate-500" />
                <span>Locked Record</span>
              </span>
            )}
          </div>
          <p className="text-xs text-slate-500">
            {it.college_name} | {it.degree} ({it.branch}) | {it.course_name} ({it.course_code}) | Mentor: {it.mentor_name}
          </p>
        </div>

        {/* Global Action: Generate Complete Package */}
        <div className="flex items-center space-x-2 shrink-0">
          <a
            href={api.getPackageZipUrl(internshipId)}
            className="inline-flex items-center space-x-2 px-4 py-2.5 rounded-xl bg-gold-400 hover:bg-gold-300 text-brand-950 font-bold text-xs shadow-md transition-transform active:scale-95"
          >
            <PackageOpen className="w-4 h-4" />
            <span>GENERATE COMPLETE PACKAGE (.ZIP)</span>
          </a>
        </div>
      </div>

      {/* Progress Stepper */}
      <ProgressStepper status={it.status} isLocked={it.is_locked === 1} />

      {/* Compliance Gatekeeper Banner */}
      {complianceCheck && (
        <div className={`p-4 rounded-xl border flex flex-col md:flex-row md:items-center justify-between gap-4 transition-all ${
          complianceCheck.is_ready_for_finalization
            ? 'bg-emerald-50/90 border-emerald-300 text-emerald-950'
            : 'bg-amber-50/90 border-amber-300 text-amber-950'
        }`}>
          <div className="flex items-start space-x-3">
            {complianceCheck.is_ready_for_finalization ? (
              <CheckCircle2 className="w-6 h-6 text-emerald-600 shrink-0 mt-0.5" />
            ) : (
              <AlertTriangle className="w-6 h-6 text-amber-600 shrink-0 mt-0.5" />
            )}
            <div>
              <div className="text-xs font-bold uppercase tracking-wider">
                Compliance Gatekeeper Status
              </div>
              <div className="text-sm font-bold font-serif mt-0.5">
                {complianceCheck.badge_message}
              </div>
              <div className="text-[11px] opacity-80 mt-1">
                {complianceCheck.checklist.filter(c => c.passed).length} of {complianceCheck.checklist.length} compliance prerequisites fulfilled.
              </div>
            </div>
          </div>

          <div className="flex items-center space-x-3 shrink-0">
            {it.is_locked === 1 ? (
              <div className="text-right">
                <div className="text-xs font-mono font-bold text-emerald-800">
                  {it.certificate_number}
                </div>
                <div className="text-[10px] text-slate-500">
                  Officially Finalized & Locked
                </div>
              </div>
            ) : (
              <button
                onClick={handleFinalize}
                disabled={!complianceCheck.is_ready_for_finalization || finalizing}
                className="inline-flex items-center space-x-1.5 px-4 py-2 rounded-lg bg-emerald-700 hover:bg-emerald-800 disabled:opacity-50 text-white text-xs font-bold shadow-sm transition-transform active:scale-95"
              >
                <Award className="w-4 h-4 text-gold-300" />
                <span>{finalizing ? "Finalizing..." : "Finalize Certificate"}</span>
              </button>
            )}
          </div>
        </div>
      )}

      {saveMessage && (
        <div className="p-3 rounded-lg bg-emerald-100 border border-emerald-300 text-emerald-900 text-xs font-semibold animate-in fade-in">
          {saveMessage}
        </div>
      )}

      {/* Tabs Header */}
      <div className="border-b border-slate-200">
        <nav className="flex space-x-4 overflow-x-auto scrollbar-none text-xs font-medium">
          {[
            { id: 'documents', label: '15 Documentation Package', icon: FileText },
            { id: 'compliance', label: 'University Compliance', icon: ShieldCheck },
            { id: 'attendance', label: 'Attendance Register', icon: CalendarCheck },
            { id: 'logs', label: 'Daily & Weekly Logs', icon: BookOpen },
            { id: 'project', label: 'Capstone Project', icon: FolderKanban },
            { id: 'evaluation', label: 'Mentor Evaluation', icon: Award },
            { id: 'certificate', label: 'Certificate & QR', icon: Sparkles },
          ].map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center space-x-2 py-3 px-3 border-b-2 font-semibold transition-colors whitespace-nowrap ${
                  isActive
                    ? 'border-brand-600 text-brand-700 bg-brand-50/50 rounded-t-lg'
                    : 'border-transparent text-slate-500 hover:text-slate-800 hover:border-slate-300'
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? 'text-brand-600' : 'text-slate-400'}`} />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </nav>
      </div>

      {/* TAB 1: 15 DOCUMENTATION PACKAGE */}
      {activeTab === 'documents' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider">
              Official Academic Documentation Package (15 Forms & Letters)
            </h2>
            <span className="text-xs text-slate-400">
              Each document features official TechnoGlobe Bharatpur branding, reference numbers, and signature zones.
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {docList.map((doc, idx) => (
              <div
                key={doc.type}
                className="p-4 rounded-xl bg-white border border-slate-200/90 shadow-2xs hover:shadow-md transition-all flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-brand-50 text-brand-700 font-bold border border-brand-200">
                      PDF #{idx + 1}
                    </span>
                    <FileText className="w-4 h-4 text-slate-400" />
                  </div>
                  <h3 className="text-xs font-bold text-slate-900 font-serif leading-snug">
                    {doc.title}
                  </h3>
                  <p className="text-[11px] text-slate-500 mt-1 leading-relaxed">
                    {doc.desc}
                  </p>
                </div>

                <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between gap-2">
                  <button
                    onClick={() => openDocPreview(doc.type, doc.title)}
                    className="flex-1 inline-flex items-center justify-center space-x-1 py-1.5 px-2 rounded-lg bg-slate-50 hover:bg-brand-50 text-brand-700 text-xs font-semibold border border-slate-200 transition-colors"
                  >
                    <Printer className="w-3.5 h-3.5" />
                    <span>Preview & Print</span>
                  </button>
                  <a
                    href={api.getDocumentPdfUrl(internshipId, doc.type)}
                    download
                    className="p-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 transition-colors"
                    title="Direct PDF Download"
                  >
                    <Download className="w-3.5 h-3.5" />
                  </a>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* TAB 2: UNIVERSITY / COLLEGE COMPLIANCE MODULE */}
      {activeTab === 'compliance' && (
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-xs space-y-6">
          <div>
            <h2 className="text-base font-serif font-bold text-slate-900">
              University / College Compliance Module
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Strictly verify genuine institutional approval, faculty coordination, and college-mandated requirements. The system never fabricates college approvals.
            </p>
          </div>

          <form onSubmit={handleSaveCompliance} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="md:col-span-2">
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  University / College Name
                </label>
                <input
                  type="text"
                  value={complianceForm.university_name || ''}
                  onChange={(e) => setComplianceForm({ ...complianceForm, university_name: e.target.value })}
                  placeholder="e.g. Rajasthan Technical University, Kota"
                  className="w-full px-3 py-2 text-xs rounded-lg border border-slate-300 focus:ring-2 focus:ring-brand-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Department / Faculty
                </label>
                <input
                  type="text"
                  value={complianceForm.department || ''}
                  onChange={(e) => setComplianceForm({ ...complianceForm, department: e.target.value })}
                  placeholder="e.g. Dept of Computer Science & Engg"
                  className="w-full px-3 py-2 text-xs rounded-lg border border-slate-300 focus:ring-2 focus:ring-brand-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  University Affiliation / Reg Ref (Optional)
                </label>
                <input
                  type="text"
                  value={complianceForm.affiliation_ref || ''}
                  onChange={(e) => setComplianceForm({ ...complianceForm, affiliation_ref: e.target.value })}
                  placeholder="Only if provided by institution"
                  className="w-full px-3 py-2 text-xs rounded-lg border border-slate-300 focus:ring-2 focus:ring-brand-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Faculty Coordinator / HOD Name
                </label>
                <input
                  type="text"
                  value={complianceForm.faculty_coordinator || ''}
                  onChange={(e) => setComplianceForm({ ...complianceForm, faculty_coordinator: e.target.value })}
                  placeholder="e.g. Dr. S. K. Gupta"
                  className="w-full px-3 py-2 text-xs rounded-lg border border-slate-300 focus:ring-2 focus:ring-brand-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Faculty Designation
                </label>
                <input
                  type="text"
                  value={complianceForm.faculty_designation || ''}
                  onChange={(e) => setComplianceForm({ ...complianceForm, faculty_designation: e.target.value })}
                  placeholder="e.g. Associate Professor & HOD"
                  className="w-full px-3 py-2 text-xs rounded-lg border border-slate-300 focus:ring-2 focus:ring-brand-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Approval Status *
                </label>
                <select
                  value={complianceForm.approval_status || 'PENDING'}
                  onChange={(e) => setComplianceForm({ ...complianceForm, approval_status: e.target.value })}
                  className="w-full px-3 py-2 text-xs rounded-lg border border-slate-300 bg-white font-semibold focus:ring-2 focus:ring-brand-500 focus:outline-none"
                >
                  <option value="APPROVED">APPROVED (Verified by College NOC / Letter)</option>
                  <option value="PENDING">PENDING (Awaiting College Documentation)</option>
                  <option value="NOT_REQUIRED">NOT_REQUIRED (Direct / Non-affiliated)</option>
                  <option value="REJECTED">REJECTED</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Approval / NOC Reference Number
                </label>
                <input
                  type="text"
                  value={complianceForm.approval_ref || ''}
                  onChange={(e) => setComplianceForm({ ...complianceForm, approval_ref: e.target.value })}
                  placeholder="e.g. GECB/TPO/INT/2026/108"
                  className="w-full px-3 py-2 text-xs rounded-lg border border-slate-300 focus:ring-2 focus:ring-brand-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Approval / Issue Date
                </label>
                <input
                  type="date"
                  value={complianceForm.approval_date || ''}
                  onChange={(e) => setComplianceForm({ ...complianceForm, approval_date: e.target.value })}
                  className="w-full px-3 py-2 text-xs rounded-lg border border-slate-300 focus:ring-2 focus:ring-brand-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Required Minimum Hours
                </label>
                <input
                  type="number"
                  value={complianceForm.required_hours || 120}
                  onChange={(e) => setComplianceForm({ ...complianceForm, required_hours: Number(e.target.value) })}
                  className="w-full px-3 py-2 text-xs rounded-lg border border-slate-300 focus:ring-2 focus:ring-brand-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Required Attendance %
                </label>
                <input
                  type="number"
                  value={complianceForm.required_attendance_pct || 75}
                  onChange={(e) => setComplianceForm({ ...complianceForm, required_attendance_pct: Number(e.target.value) })}
                  className="w-full px-3 py-2 text-xs rounded-lg border border-slate-300 focus:ring-2 focus:ring-brand-500 focus:outline-none"
                />
              </div>
            </div>

            <div className="pt-4 border-t border-slate-200 flex justify-end">
              <button
                type="submit"
                className="inline-flex items-center space-x-2 px-5 py-2 rounded-xl bg-brand-700 hover:bg-brand-800 text-white text-xs font-bold shadow-sm transition-all"
              >
                <Save className="w-4 h-4 text-gold-400" />
                <span>Save Compliance Settings</span>
              </button>
            </div>
          </form>
        </div>
      )}

      {/* TAB 3: ATTENDANCE MANAGEMENT */}
      {activeTab === 'attendance' && (
        <div className="space-y-6">
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-2xs">
              <span className="text-[11px] text-slate-500 font-medium">Scheduled Days</span>
              <p className="text-xl font-bold text-slate-900 mt-1">{stats.total_days} Days</p>
            </div>
            <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-2xs">
              <span className="text-[11px] text-emerald-600 font-medium">Days Present</span>
              <p className="text-xl font-bold text-emerald-700 mt-1">{stats.present_days} Days</p>
            </div>
            <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-2xs">
              <span className="text-[11px] text-slate-500 font-medium">Total Hours Logged</span>
              <p className="text-xl font-bold text-slate-900 mt-1">{stats.total_hours_logged || 120} Hours</p>
            </div>
            <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-2xs">
              <span className="text-[11px] text-brand-600 font-medium">Attendance Rate</span>
              <p className="text-xl font-bold text-brand-700 mt-1">
                {stats.total_days > 0 ? ((stats.present_days / stats.total_days) * 100).toFixed(1) : 0}%
              </p>
            </div>
          </div>

          <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
            <div className="p-4 border-b border-slate-200 flex items-center justify-between">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700">
                Verified Daily Attendance Register ({stats.total_days} Days)
              </h3>
              <div className="flex space-x-2">
                <button
                  onClick={() => openDocPreview('attendance_sheet', '05. Attendance Register Sheet')}
                  className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-xs font-semibold text-slate-800"
                >
                  <Printer className="w-3.5 h-3.5" />
                  <span>Print Sheet</span>
                </button>
                <button
                  onClick={() => openDocPreview('attendance_summary', '06. Attendance Summary Report')}
                  className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-brand-50 hover:bg-brand-100 text-xs font-semibold text-brand-700"
                >
                  <FileText className="w-3.5 h-3.5" />
                  <span>Print Summary</span>
                </button>
              </div>
            </div>

            <div className="max-h-96 overflow-y-auto">
              <table className="w-full text-left text-xs text-slate-600">
                <thead className="bg-slate-50 text-slate-500 sticky top-0 font-semibold uppercase tracking-wider text-[10px] border-b border-slate-200">
                  <tr>
                    <th className="py-2.5 px-4">Date & Day</th>
                    <th className="py-2.5 px-4">Time In/Out</th>
                    <th className="py-2.5 px-4">Hours</th>
                    <th className="py-2.5 px-4">Topic Covered</th>
                    <th className="py-2.5 px-4">Status</th>
                    <th className="py-2.5 px-4">Verification</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {(ctx.attendance_records || []).map((att: any, i: number) => (
                    <tr key={i} className="hover:bg-slate-50">
                      <td className="py-2 px-4 font-medium text-slate-800">{att.date} ({att.day_of_week})</td>
                      <td className="py-2 px-4">{att.start_time} - {att.end_time}</td>
                      <td className="py-2 px-4 font-mono">{att.total_hours}h</td>
                      <td className="py-2 px-4">{att.topic_covered || 'Practical training'}</td>
                      <td className="py-2 px-4">
                        <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                          att.status === 'PRESENT' ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'
                        }`}>
                          {att.status}
                        </span>
                      </td>
                      <td className="py-2 px-4 text-emerald-600 font-semibold text-[11px]">
                        ✓ Signed
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* TAB 4: DAILY LOGS & WEEKLY REPORTS */}
      {activeTab === 'logs' && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider">
              Recorded Daily Logbook & Weekly Milestone Dossiers
            </h3>
            <div className="flex space-x-2">
              <button
                onClick={() => openDocPreview('daily_log', '07. Daily Internship Logbook')}
                className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-xs font-semibold text-slate-800"
              >
                <Printer className="w-3.5 h-3.5" />
                <span>Print Daily Logbook</span>
              </button>
              <button
                onClick={() => openDocPreview('weekly_report', '08. Weekly Progress Report')}
                className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-brand-50 hover:bg-brand-100 text-xs font-semibold text-brand-700"
              >
                <FileText className="w-3.5 h-3.5" />
                <span>Print Weekly Reviews</span>
              </button>
            </div>
          </div>

          <div className="grid grid-cols-1 gap-3 max-h-[500px] overflow-y-auto pr-1">
            {(ctx.weeks || []).map((w: any) => (
              <div key={w.week_number} className="p-4 rounded-xl bg-white border border-slate-200 shadow-2xs space-y-2">
                <div className="flex items-center justify-between border-b border-slate-100 pb-2">
                  <div className="font-serif font-bold text-brand-800 text-sm">
                    Week {w.week_number}: {w.topics_covered}
                  </div>
                  <span className="text-[11px] font-mono text-slate-500">
                    {w.start_date} to {w.end_date} | {w.hours_completed} Hours
                  </span>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                  <div>
                    <span className="font-semibold text-slate-700">Practical Tasks:</span>
                    <p className="text-slate-600 mt-0.5">{w.practical_work}</p>
                  </div>
                  <div>
                    <span className="font-semibold text-slate-700">Competencies Acquired:</span>
                    <p className="text-slate-600 mt-0.5">{w.skills_learned}</p>
                  </div>
                </div>
                <div className="bg-slate-50 p-2.5 rounded-lg text-xs italic text-slate-600 border border-slate-100">
                  <b>Mentor Remark:</b> "{w.mentor_remarks}"
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* TAB 5: CAPSTONE / LIVE PROJECT */}
      {activeTab === 'project' && (
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-xs space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-base font-serif font-bold text-slate-900">
                Capstone Project Technical Dossier
              </h2>
              <p className="text-xs text-slate-500 mt-0.5">
                Structured for {it.course_name} curriculum. Complete documentation is embedded in the academic internship report.
              </p>
            </div>
            <button
              onClick={() => openDocPreview('project_report', '10. Project Technical Report')}
              className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-brand-50 hover:bg-brand-100 text-xs font-semibold text-brand-700"
            >
              <Printer className="w-3.5 h-3.5" />
              <span>Print Project Report</span>
            </button>
          </div>

          <form onSubmit={handleSaveProject} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Project Title *
              </label>
              <input
                type="text"
                required
                value={projectForm.project_title}
                onChange={(e) => setProjectForm({ ...projectForm, project_title: e.target.value })}
                className="w-full px-3 py-2 text-xs rounded-lg border border-slate-300 focus:ring-2 focus:ring-brand-500 focus:outline-none font-semibold text-brand-900"
              />
            </div>

            {/* Dynamic fields based on track */}
            {it.course_code === 'DA' ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="md:col-span-2">
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Problem Statement</label>
                  <textarea
                    rows={3}
                    value={projectForm.fields.problem_statement || ''}
                    onChange={(e) => setProjectForm({ ...projectForm, fields: { ...projectForm.fields, problem_statement: e.target.value } })}
                    className="w-full px-3 py-2 text-xs rounded-lg border border-slate-300 focus:ring-2 focus:ring-brand-500 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Enterprise Dataset Architecture</label>
                  <textarea
                    rows={2}
                    value={projectForm.fields.dataset || ''}
                    onChange={(e) => setProjectForm({ ...projectForm, fields: { ...projectForm.fields, dataset: e.target.value } })}
                    className="w-full px-3 py-2 text-xs rounded-lg border border-slate-300 focus:ring-2 focus:ring-brand-500 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Tools & Technology Stack</label>
                  <textarea
                    rows={2}
                    value={projectForm.fields.tools || ''}
                    onChange={(e) => setProjectForm({ ...projectForm, fields: { ...projectForm.fields, tools: e.target.value } })}
                    className="w-full px-3 py-2 text-xs rounded-lg border border-slate-300 focus:ring-2 focus:ring-brand-500 focus:outline-none"
                  />
                </div>
                <div className="md:col-span-2">
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Key Analytical Findings & Recommendations</label>
                  <textarea
                    rows={3}
                    value={projectForm.fields.findings || ''}
                    onChange={(e) => setProjectForm({ ...projectForm, fields: { ...projectForm.fields, findings: e.target.value } })}
                    className="w-full px-3 py-2 text-xs rounded-lg border border-slate-300 focus:ring-2 focus:ring-brand-500 focus:outline-none"
                  />
                </div>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Client / Business Brand</label>
                  <input
                    type="text"
                    value={projectForm.fields.brand_business || ''}
                    onChange={(e) => setProjectForm({ ...projectForm, fields: { ...projectForm.fields, brand_business: e.target.value } })}
                    className="w-full px-3 py-2 text-xs rounded-lg border border-slate-300 focus:ring-2 focus:ring-brand-500 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Campaign Objective</label>
                  <input
                    type="text"
                    value={projectForm.fields.campaign_objective || ''}
                    onChange={(e) => setProjectForm({ ...projectForm, fields: { ...projectForm.fields, campaign_objective: e.target.value } })}
                    className="w-full px-3 py-2 text-xs rounded-lg border border-slate-300 focus:ring-2 focus:ring-brand-500 focus:outline-none"
                  />
                </div>
                <div className="md:col-span-2">
                  <label className="block text-xs font-semibold text-slate-700 mb-1">SEO & Advertising Strategy Blueprint</label>
                  <textarea
                    rows={3}
                    value={projectForm.fields.seo_strategy || ''}
                    onChange={(e) => setProjectForm({ ...projectForm, fields: { ...projectForm.fields, seo_strategy: e.target.value } })}
                    className="w-full px-3 py-2 text-xs rounded-lg border border-slate-300 focus:ring-2 focus:ring-brand-500 focus:outline-none"
                  />
                </div>
              </div>
            )}

            <div className="flex items-center justify-between pt-4 border-t border-slate-200">
              <div className="flex items-center space-x-2">
                <span className="text-xs font-semibold text-slate-700">Project Status:</span>
                <select
                  value={projectForm.status}
                  onChange={(e) => setProjectForm({ ...projectForm, status: e.target.value })}
                  className="px-2.5 py-1 text-xs rounded-lg border border-slate-300 font-semibold bg-white"
                >
                  <option value="IN_PROGRESS">IN_PROGRESS</option>
                  <option value="SUBMITTED">SUBMITTED</option>
                  <option value="APPROVED">APPROVED & DEFENDED</option>
                </select>
              </div>

              <button
                type="submit"
                className="inline-flex items-center space-x-2 px-5 py-2 rounded-xl bg-brand-700 hover:bg-brand-800 text-white text-xs font-bold shadow-sm"
              >
                <Save className="w-4 h-4 text-gold-400" />
                <span>Save Project Data</span>
              </button>
            </div>
          </form>
        </div>
      )}

      {/* TAB 6: MENTOR EVALUATION */}
      {activeTab === 'evaluation' && (
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-xs space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-base font-serif font-bold text-slate-900">
                Formal Mentor Assessment Rubric
              </h2>
              <p className="text-xs text-slate-500 mt-0.5">
                Appraisal conducted by assigned mentor {it.mentor_name} across 9 institutional parameters.
              </p>
            </div>
            <button
              onClick={() => openDocPreview('evaluation', '11. Mentor Evaluation Rubric')}
              className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-brand-50 hover:bg-brand-100 text-xs font-semibold text-brand-700"
            >
              <Printer className="w-3.5 h-3.5" />
              <span>Print Rubric</span>
            </button>
          </div>

          <form onSubmit={handleSaveEvaluation} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Overall Score (Out of 100) *
                </label>
                <input
                  type="number"
                  min={0}
                  max={100}
                  value={evalForm.overall_score}
                  onChange={(e) => setEvalForm({ ...evalForm, overall_score: Number(e.target.value) })}
                  className="w-full px-3 py-2 text-base font-bold text-brand-700 rounded-lg border border-slate-300 focus:ring-2 focus:ring-brand-500 focus:outline-none"
                />
              </div>

              <div className="md:col-span-2">
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Mentor Remarks & Final Observation *
                </label>
                <textarea
                  rows={2}
                  required
                  value={evalForm.final_remark}
                  onChange={(e) => setEvalForm({ ...evalForm, final_remark: e.target.value })}
                  placeholder="Enter mentor's evaluative remarks..."
                  className="w-full px-3 py-2 text-xs rounded-lg border border-slate-300 focus:ring-2 focus:ring-brand-500 focus:outline-none"
                />
              </div>
            </div>

            <div className="pt-4 border-t border-slate-200 flex justify-end">
              <button
                type="submit"
                className="inline-flex items-center space-x-2 px-5 py-2 rounded-xl bg-brand-700 hover:bg-brand-800 text-white text-xs font-bold shadow-sm"
              >
                <Save className="w-4 h-4 text-gold-400" />
                <span>Save Mentor Rubric</span>
              </button>
            </div>
          </form>
        </div>
      )}

      {/* TAB 7: CERTIFICATE & QR VERIFICATION */}
      {activeTab === 'certificate' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Certificate Preview Card */}
          <div className="lg:col-span-2 bg-linear-to-b from-amber-50/40 via-white to-amber-50/40 p-8 rounded-2xl border-4 border-brand-700 shadow-lg relative overflow-hidden">
            {/* Guilloche border mockup */}
            <div className="absolute inset-2 border-2 border-gold-400/70 pointer-events-none rounded-xl" />

            <div className="text-center space-y-2 mb-6">
              <span className="text-[10px] tracking-widest text-slate-500 uppercase font-semibold">
                {s.org_name}
              </span>
              <h3 className="text-lg font-serif font-bold text-brand-700">
                {s.centre_name}
              </h3>
              <div className="h-0.5 w-24 bg-gold-400 mx-auto" />
              <h4 className="text-xl font-serif font-bold text-slate-900 tracking-wide pt-2">
                CERTIFICATE OF INTERNSHIP COMPLETION
              </h4>
              <p className="text-xs text-slate-500 italic">This is to certify that</p>
              <p className="text-2xl font-serif font-bold text-brand-800 underline decoration-gold-400 underline-offset-8">
                {it.student_name.toUpperCase()}
              </p>
              <p className="text-xs text-slate-600 max-w-lg mx-auto pt-2">
                of <b>{it.college_name}</b> pursuing <b>{it.degree} in {it.branch}</b> has successfully completed the course-based internship in
              </p>
              <p className="text-base font-serif font-bold text-brand-700">
                {it.course_title}
              </p>
              <p className="text-xs text-slate-500">
                Conducted from {it.start_date} to {it.end_date} with a total of {it.total_training_hours} Hours.
              </p>
            </div>

            <div className="mt-8 pt-4 border-t border-slate-200/80 flex items-center justify-between text-xs">
              <div className="space-y-0.5">
                <p className="font-mono text-[10px] text-slate-500">Cert #: {it.certificate_number || 'PENDING ISSUE'}</p>
                <p className="font-mono text-[10px] text-slate-500">Ref: {it.verification_code || 'PENDING'}</p>
              </div>

              <div className="flex items-center space-x-6">
                <div className="text-center">
                  <div className="h-8 border-b border-slate-400 w-28 mx-auto" />
                  <p className="text-[10px] font-bold text-slate-800 mt-1">{it.mentor_name}</p>
                  <p className="text-[9px] text-slate-400">Industry Mentor</p>
                </div>
                <div className="text-center">
                  <div className="h-8 border-b border-slate-400 w-28 mx-auto" />
                  <p className="text-[10px] font-bold text-slate-800 mt-1">{s.signatory_name}</p>
                  <p className="text-[9px] text-slate-400">{s.signatory_designation}</p>
                </div>
              </div>
            </div>
          </div>

          {/* Self-Contained Verification & QR Info Box */}
          <div className="space-y-4">
            <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-xs space-y-4">
              <div className="flex items-center space-x-2 text-brand-700 font-serif font-bold text-sm">
                <ShieldCheck className="w-5 h-5 text-gold-500" />
                <span>Self-Contained Digital Verification</span>
              </div>
              <p className="text-xs text-slate-500 leading-relaxed">
                Self-contained QR code encoding complete authenticated certificate metadata, verifiable offline on any smartphone without external URLs.
              </p>

              {it.certificate_number ? (() => {
                const verifyUrl = `${window.location.protocol}//${window.location.host}/verify?cert=${encodeURIComponent(it.certificate_number)}&name=${encodeURIComponent(it.student_name)}&course=${encodeURIComponent(it.course_name)}&sem=${encodeURIComponent(`${it.degree || 'BCA'} (${it.semester_year || '6th Semester'})`)}&college=${encodeURIComponent(it.college_name)}&ver_id=${encodeURIComponent(it.verification_code || '')}`;
                const qrValue = it.qr_payload_json?.startsWith('http') ? it.qr_payload_json : verifyUrl;
                return (
                  <div className="flex flex-col items-center justify-center p-4 bg-slate-50 rounded-xl border border-slate-200 text-center space-y-3">
                    <div className="p-3 bg-white rounded-xl shadow-xs border border-slate-200 inline-block">
                      <QRCodeSVG
                        value={qrValue}
                        size={140}
                        level="M"
                        includeMargin={false}
                      />
                    </div>
                    <div>
                      <span className="font-mono text-[10px] font-bold text-brand-900 tracking-wide uppercase block">
                        SCAN WITH PHONE CAMERA TO VERIFY
                      </span>
                      <span className="text-[10px] text-slate-500 font-mono block">
                        {it.certificate_number} • {it.verification_code}
                      </span>
                    </div>

                    <a
                      href={verifyUrl}
                      target="_blank"
                      rel="noreferrer"
                      className="w-full inline-flex items-center justify-center space-x-1.5 px-3 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold transition-all shadow-xs cursor-pointer"
                    >
                      <ShieldCheck className="w-4 h-4" />
                      <span>Open Live Verification Link</span>
                      <ExternalLink className="w-3 h-3 ml-0.5" />
                    </a>

                    <div className="w-full text-left bg-white p-3 rounded-lg border border-slate-200 space-y-1">
                      <div className="text-[9px] font-bold text-emerald-700 uppercase tracking-wider">
                        ✓ Decoded Link & Data:
                      </div>
                      <p className="text-[9.5px] text-slate-600 font-mono break-all bg-slate-50 p-2 rounded border border-slate-100">
                        {qrValue}
                      </p>
                    </div>
                  </div>
                );
              })() : (
                <div className="p-4 bg-amber-50 rounded-lg border border-amber-200 text-amber-800 text-xs text-center font-medium">
                  Certificate number and self-contained QR will be generated automatically upon finalization.
                </div>
              )}

              <div className="pt-2 space-y-2">
                <Link
                  to={`/document-editor?student_id=${it.student_id}&doc=certificate`}
                  className="w-full inline-flex items-center justify-center space-x-2 px-4 py-2 rounded-xl bg-purple-50 hover:bg-purple-100 text-purple-800 border border-purple-200 text-xs font-bold transition-all shadow-2xs"
                >
                  <span>Open in 50/50 Live Document Editor</span>
                </Link>

                <button
                  onClick={() => openDocPreview('certificate', '14. Completion Certificate (A4 Landscape)')}
                  className="w-full inline-flex items-center justify-center space-x-2 px-4 py-2.5 rounded-xl bg-brand-700 hover:bg-brand-800 text-white text-xs font-bold shadow-sm transition-all"
                >
                  <Printer className="w-4 h-4 text-gold-300" />
                  <span>Preview & Print Official Certificate</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Document Modal */}
      <DocumentModal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        internshipId={internshipId}
        docType={activeDoc.type}
        docTitle={activeDoc.title}
        studentName={it.student_name}
      />
    </div>
  );
};
