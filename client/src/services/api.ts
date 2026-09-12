import {
  Student, Course, Mentor, Batch, CentreSettings, Institution,
  ComplianceRecord, AttendanceRecord, DailyLogRecord, WeeklyReportRecord,
  ProjectRecord, EvaluationRecord, ComplianceCheckResult
} from '../types';

const API_BASE = '/api';

function authHeaders(): HeadersInit {
  const token = localStorage.getItem('tg_token');
  const headers: HeadersInit = { 'Content-Type': 'application/json' };
  if (token) headers['Authorization'] = `Bearer ${token}`;
  return headers;
}


export const api = {
  // Auth
  login: async (email: string, password: string) => {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify({ email, password }),
    });
    if (!res.ok) throw new Error((await res.json()).detail || 'Login failed');
    return res.json();
  },

  getCurrentUser: async () => {
    const res = await fetch(`${API_BASE}/auth/me`, { headers: authHeaders() });
    return res.json();
  },

  // Dashboard
  getDashboardStats: async () => {
    const res = await fetch(`${API_BASE}/dashboard/stats`);
    return res.json();
  },

  // Institutions (Multi-Institution Support: TechnoGlobe & Poddar College)
  getInstitutions: async (): Promise<Institution[]> => {
    const res = await fetch(`${API_BASE}/institutions`);
    return res.json();
  },

  // Students
  getStudents: async (params?: { search?: string; course?: string; status?: string; institution_id?: number }): Promise<Student[]> => {
    const q = new URLSearchParams();
    if (params?.search) q.set('search', params.search);
    if (params?.course) q.set('course', params.course);
    if (params?.status) q.set('status', params.status);
    if (params?.institution_id) q.set('institution_id', params.institution_id.toString());
    const res = await fetch(`${API_BASE}/students?${q.toString()}`);
    return res.json();
  },

  getStudent: async (id: number) => {
    const res = await fetch(`${API_BASE}/students/${id}`);
    if (!res.ok) throw new Error('Student not found');
    return res.json();
  },

  createStudent: async (data: any) => {
    const res = await fetch(`${API_BASE}/students`, {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error((await res.json()).detail || 'Failed to create student');
    return res.json();
  },

  // Courses
  getCourses: async (): Promise<Course[]> => {
    const res = await fetch(`${API_BASE}/courses`);
    return res.json();
  },

  getCourse: async (id: number): Promise<Course> => {
    const res = await fetch(`${API_BASE}/courses/${id}`);
    return res.json();
  },

  updateModule: async (id: number, data: any) => {
    const res = await fetch(`${API_BASE}/modules/${id}`, {
      method: 'PUT',
      headers: authHeaders(),
      body: JSON.stringify(data),
    });
    return res.json();
  },

  // Mentors & Batches
  getMentors: async (): Promise<Mentor[]> => {
    const res = await fetch(`${API_BASE}/mentors`);
    return res.json();
  },

  getBatches: async (): Promise<Batch[]> => {
    const res = await fetch(`${API_BASE}/batches`);
    return res.json();
  },

  // Internship Full Details
  getInternship: async (id: number) => {
    const res = await fetch(`${API_BASE}/internships/${id}`);
    if (!res.ok) throw new Error('Internship not found');
    return res.json();
  },

  // Compliance Module
  updateCompliance: async (internshipId: number, data: ComplianceRecord) => {
    const res = await fetch(`${API_BASE}/internships/${internshipId}/compliance`, {
      method: 'PUT',
      headers: authHeaders(),
      body: JSON.stringify(data),
    });
    return res.json();
  },

  getComplianceCheck: async (internshipId: number): Promise<ComplianceCheckResult> => {
    const res = await fetch(`${API_BASE}/internships/${internshipId}/compliance-check`);
    return res.json();
  },

  finalizeCertificate: async (internshipId: number) => {
    const res = await fetch(`${API_BASE}/internships/${internshipId}/finalize-certificate`, {
      method: 'POST',
    });
    if (!res.ok) throw new Error((await res.json()).detail || 'Finalization failed');
    return res.json();
  },

  // Attendance
  getAttendance: async (internshipId: number): Promise<AttendanceRecord[]> => {
    const res = await fetch(`${API_BASE}/internships/${internshipId}/attendance`);
    return res.json();
  },

  saveAttendance: async (internshipId: number, item: AttendanceRecord) => {
    const res = await fetch(`${API_BASE}/internships/${internshipId}/attendance`, {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify(item),
    });
    return res.json();
  },

  // Daily Logs
  getDailyLogs: async (internshipId: number): Promise<DailyLogRecord[]> => {
    const res = await fetch(`${API_BASE}/internships/${internshipId}/logs`);
    return res.json();
  },

  saveDailyLog: async (internshipId: number, item: DailyLogRecord) => {
    const res = await fetch(`${API_BASE}/internships/${internshipId}/logs`, {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify(item),
    });
    return res.json();
  },

  // Project
  getProject: async (internshipId: number): Promise<ProjectRecord> => {
    const res = await fetch(`${API_BASE}/internships/${internshipId}/project`);
    return res.json();
  },

  saveProject: async (internshipId: number, data: { project_title: string; fields: Record<string, any>; status?: string }) => {
    const res = await fetch(`${API_BASE}/internships/${internshipId}/project`, {
      method: 'PUT',
      headers: authHeaders(),
      body: JSON.stringify(data),
    });
    return res.json();
  },

  // Evaluation
  getEvaluation: async (internshipId: number): Promise<EvaluationRecord> => {
    const res = await fetch(`${API_BASE}/internships/${internshipId}/evaluation`);
    return res.json();
  },

  saveEvaluation: async (internshipId: number, data: { mentor_id: number; criteria_scores: Record<string, any>; overall_score: number; final_remark: string }) => {
    const res = await fetch(`${API_BASE}/internships/${internshipId}/evaluation`, {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify(data),
    });
    return res.json();
  },

  // Settings
  getSettings: async (): Promise<CentreSettings> => {
    const res = await fetch(`${API_BASE}/settings`, { headers: authHeaders() });
    return res.json();
  },

  updateSettings: async (data: Partial<CentreSettings>) => {
    const res = await fetch(`${API_BASE}/settings`, {
      method: 'PUT',
      headers: authHeaders(),
      body: JSON.stringify(data),
    });
    return res.json();
  },

  // Verification & Self-Contained QR
  getCertificateQrData: async (internshipId: number) => {
    const res = await fetch(`${API_BASE}/certificates/${internshipId}/qr-data`);
    if (!res.ok) throw new Error('Certificate record not found');
    return res.json();
  },

  // Audit logs
  getAuditLogs: async () => {
    const res = await fetch(`${API_BASE}/audit-logs`, { headers: authHeaders() });
    return res.json();
  },

  // Document URLs
  getDocumentPdfUrl: (internshipId: number, docType: string) => {
    return `${API_BASE}/documents/${internshipId}/${docType}/pdf`;
  },

  getPackageZipUrl: (internshipId: number) => {
    return `${API_BASE}/documents/${internshipId}/package-zip`;
  },

  getBatchPrintUrl: (internshipIds?: number[]) => {
    if (internshipIds && internshipIds.length > 0) {
      return `${API_BASE}/certificates/batch-print?ids=${internshipIds.join(',')}`;
    }
    return `${API_BASE}/certificates/batch-print`;
  },

  // Backup & Restore
  getBackupDbUrl: () => `${API_BASE}/backup/database`,

  restoreBackup: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${API_BASE}/backup/restore`, {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to restore database');
    }
    return res.json();
  },

  exportJson: async () => {
    const res = await fetch(`${API_BASE}/backup/export-json`);
    return res.json();
  },

  resetDemoData: async () => {
    const res = await fetch(`${API_BASE}/admin/demo/reset`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to reset demo data');
    return res.json();
  },

  deleteDemoData: async () => {
    const res = await fetch(`${API_BASE}/admin/demo/delete`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to delete demo data');
    return res.json();
  },

  // Document Templates
  getTemplates: async () => {
    const res = await fetch(`${API_BASE}/templates`);
    return res.json();
  },

  getTemplate: async (key: string) => {
    const res = await fetch(`${API_BASE}/templates/${key}`);
    return res.json();
  },

  updateTemplate: async (key: string, title: string, blocks: any[]) => {
    const res = await fetch(`${API_BASE}/templates/${key}`, {
      method: 'PUT',
      headers: authHeaders(),
      body: JSON.stringify({ title, blocks }),
    });
    return res.json();
  },

  // Bulk Attendance
  bulkUpdateAttendance: async (internshipId: number, data: { dates: string[]; status: string; topic_covered?: string; start_time?: string; end_time?: string; total_hours?: number }) => {
    const res = await fetch(`${API_BASE}/internships/${internshipId}/attendance/bulk`, {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify(data),
    });
    return res.json();
  },

  clearAttendance: async (internshipId: number) => {
    const res = await fetch(`${API_BASE}/internships/${internshipId}/attendance/clear`, {
      method: 'POST',
    });
    return res.json();
  },

  // Step-by-Step Quick Generator
  quickGenerateInternship: async (data: {
    institution_id?: number;
    full_name: string;
    father_mother_name: string;
    dob?: string;
    gender?: string;
    mobile?: string;
    email?: string;
    address?: string;
    city?: string;
    state?: string;
    college_name?: string;
    degree?: string;
    branch?: string;
    semester_year?: string;
    academic_session?: string;
    course_track: string;
    mentor_id?: number;
    start_date?: string;
    end_date?: string;
    custom_project_title?: string;
    attendance_preset?: string;
    evaluation_score?: number;
    mentor_remarks?: string;
  }) => {
    const res = await fetch(`${API_BASE}/wizard/quick-generate`, {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to quickly generate internship documentation package');
    }
    return res.json();
  },

  // Bulk & Multi-Student Batch Attendance Engine (50+ Students)
  bulkAttendancePreview: async (data: {
    institution_id: number;
    course_track: string;
    custom_track_name?: string;
    total_days: number;
    start_date: string;
    start_time?: string;
    end_time?: string;
    daily_hours?: number;
    mentor_id?: number;
    students: Array<{
      full_name: string;
      father_mother_name?: string;
      roll_no?: string;
      college_name?: string;
      degree?: string;
      branch?: string;
      attendance_pct: number;
    }>;
  }) => {
    const res = await fetch(`${API_BASE}/attendance/bulk-generate-preview`, {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to generate bulk attendance preview');
    }
    return res.json();
  },

  downloadMasterAttendancePdf: async (data: any) => {
    const res = await fetch(`${API_BASE}/attendance/bulk-generate-pdf`, {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to generate Master Batch Attendance PDF');
    }
    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `Master_Batch_Attendance_Register_${data.total_days}Days.pdf`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  },

  downloadBatchAttendanceZip: async (data: any) => {
    const res = await fetch(`${API_BASE}/attendance/bulk-generate-zip`, {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to generate Batch Attendance ZIP Package');
    }
    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `Batch_Attendance_Package_${data.total_days}Days_${data.students?.length || 0}Students.zip`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  },

  bulkEnrollStudents: async (data: any) => {
    const res = await fetch(`${API_BASE}/attendance/bulk-enroll-and-save`, {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to bulk enroll students');
    }
    return res.json();
  }
};
