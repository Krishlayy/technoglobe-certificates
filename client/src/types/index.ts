export interface CentreSettings {
  id: number;
  org_name: string;
  centre_name: string;
  centre_code: string;
  address: string;
  phone: string;
  email: string;
  website: string;
  auth_ref?: string;
  signatory_name: string;
  signatory_designation: string;
  logo_url?: string;
  signature_url?: string;
  stamp_url?: string;
  show_digital_signature: number;
  show_digital_stamp: number;
  cert_prefix: string;
  doc_prefix: string;
  default_required_hours: number;
  default_required_attendance_pct: number;
  verification_base_url?: string;
}

export interface Institution {
  id: number;
  name: string;
  code: string;
  full_name: string;
  address: string;
  centre_head: string;
  stamp_mode: string; // 'DIGITAL_BADGE' | 'EMPTY_INK_PAD_BOX'
  cert_prefix: string;
  logo_path: string;
  watermark_path: string;
  primary_color: string;
  secondary_color: string;
  is_active: number;
}

export interface Student {
  id: number;
  full_name: string;
  father_mother_name: string;
  dob: string;
  gender: string;
  mobile: string;
  email: string;
  address: string;
  city: string;
  state: string;
  college_name: string;
  enrollment_roll_no?: string;
  registration_no?: string;
  degree: string;
  branch: string;
  semester_year: string;
  academic_session: string;
  is_demo: number;
  created_at?: string;
  internship_id?: number;
  internship_title?: string;
  internship_status?: string;
  institution_id?: number;
  institution_name?: string;
  institution_code?: string;
  certificate_number?: string;
  verification_code?: string;
  course_name?: string;
  course_code?: string;
  mentor_name?: string;
  start_date?: string;
  end_date?: string;
  total_training_hours?: number;
}

export interface Course {
  id: number;
  code: string;
  name: string;
  title: string;
  description: string;
  duration_weeks: number;
  total_hours: number;
  default_mode: string;
  is_active: number;
  modules?: CourseModule[];
}

export interface CourseModule {
  id: number;
  course_id: number;
  module_number: number;
  title: string;
  description: string;
  topics_json: string;
  practical_activities_json: string;
  learning_outcomes_json: string;
  hours: number;
}

export interface Mentor {
  id: number;
  name: string;
  designation: string;
  email?: string;
  phone?: string;
  bio?: string;
  is_active: number;
}

export interface Batch {
  id: number;
  course_id: number;
  batch_code: string;
  name: string;
  start_date: string;
  end_date: string;
  mentor_id?: number;
  max_students: number;
  course_name?: string;
  mentor_name?: string;
}

export interface ComplianceRecord {
  id?: number;
  internship_id: number;
  university_name?: string;
  department?: string;
  affiliation_ref?: string;
  faculty_coordinator?: string;
  faculty_designation?: string;
  approval_status: 'PENDING' | 'APPROVED' | 'NOT_REQUIRED' | 'REJECTED';
  approval_ref?: string;
  approval_date?: string;
  noc_document_url?: string;
  approval_letter_url?: string;
  mou_doc_url?: string;
  required_duration?: string;
  required_hours?: number;
  required_attendance_pct?: number;
  checklist_json?: string | Record<string, any>;
  supporting_docs_json?: string;
}

export interface AttendanceRecord {
  id?: number;
  internship_id: number;
  date: string;
  day_of_week: string;
  start_time: string;
  end_time: string;
  total_hours: number;
  topic_covered?: string;
  status: 'PRESENT' | 'ABSENT' | 'LEAVE' | 'AUTHORIZED LEAVE' | 'HOLIDAY' | string;
  student_signed?: number;
  mentor_signed?: number;
  remarks?: string;
}

export interface DailyLogRecord {
  id?: number;
  internship_id: number;
  date: string;
  day_of_week: string;
  module_name: string;
  topic: string;
  work_performed: string;
  practical_activity: string;
  tools_used: string;
  learning_outcome: string;
  hours: number;
  mentor_remarks?: string;
  student_signed?: number;
  mentor_signed?: number;
}

export interface WeeklyReportRecord {
  id?: number;
  internship_id: number;
  week_number: number;
  start_date: string;
  end_date: string;
  topics_covered: string;
  practical_work: string;
  project_progress: string;
  skills_learned: string;
  hours_completed: number;
  mentor_remarks?: string;
  student_signed?: number;
  mentor_signed?: number;
}

export interface ProjectRecord {
  id?: number;
  internship_id: number;
  project_title: string;
  fields_json?: string;
  fields?: Record<string, any>;
  file_attachments_json?: string;
  status: 'IN_PROGRESS' | 'SUBMITTED' | 'APPROVED';
  submitted_at?: string;
  approved_at?: string;
}

export interface EvaluationRecord {
  id?: number;
  internship_id: number;
  mentor_id: number;
  criteria_scores_json?: string;
  criteria_scores?: Record<string, { score: number; max: number; rating: string }>;
  overall_score: number;
  final_remark?: string;
  evaluated_at?: string;
  mentor_signed?: number;
}

export interface CertificateRecord {
  id?: number;
  internship_id: number;
  cert_type: 'COMPLETION' | 'EXPERIENCE';
  certificate_number: string;
  verification_code: string;
  issue_date: string;
  is_finalized: number;
  finalized_by?: string;
  pdf_path?: string;
}

export interface ComplianceCheckResult {
  is_ready_for_finalization: boolean;
  badge_message: string;
  checklist: Array<{
    name: string;
    passed: boolean;
    detail: string;
  }>;
  is_locked: boolean;
  certificate_number?: string;
}

export interface TemplateBlock {
  id: string;
  label: string;
  enabled: boolean;
}

export interface DocumentTemplate {
  id: number;
  template_key: string;
  title: string;
  blocks: TemplateBlock[];
  updated_at?: string;
}
