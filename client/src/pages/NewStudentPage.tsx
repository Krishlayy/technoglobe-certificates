import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { UserPlus, ArrowLeft, Save, Building2, BookOpen, UserCheck, ShieldCheck, Wand2, ArrowRight } from 'lucide-react';
import { api } from '../services/api';
import { Course, Mentor, Batch } from '../types';

export const NewStudentPage: React.FC = () => {
  const navigate = useNavigate();
  const [courses, setCourses] = useState<Course[]>([]);
  const [mentors, setMentors] = useState<Mentor[]>([]);
  const [batches, setBatches] = useState<Batch[]>([]);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  const [formData, setFormData] = useState({
    // Personal Details
    full_name: '',
    father_mother_name: '',
    dob: '2004-05-15',
    gender: 'Male',
    mobile: '',
    email: '',
    address: '',
    city: 'Bharatpur',
    state: 'Rajasthan',

    // Academic Details (Simplified: College fixed to Poddar College; No PRN/Roll)
    college_name: 'Poddar College, Bharatpur',
    degree: 'BCA',
    branch: 'Computer Science',
    semester_year: '6th Semester',
    academic_session: '2025-2026',

    // Internship Details
    course_id: 1,
    mentor_id: 1,
    batch_id: 1,
    internship_title: '',
    internship_type: 'Course-Based Internship',
    start_date: '2026-06-01',
    end_date: '2026-07-12',
    total_days: 36,
    total_training_hours: 120,
    mode: 'Offline',
  });

  useEffect(() => {
    Promise.all([api.getCourses(), api.getMentors(), api.getBatches()]).then(
      ([cData, mData, bData]) => {
        setCourses(cData);
        setMentors(mData);
        setBatches(bData);
        if (cData.length > 0) {
          setFormData(prev => ({
            ...prev,
            course_id: cData[0].id,
            internship_title: cData[0].title
          }));
        }
        if (mData.length > 0) {
          setFormData(prev => ({ ...prev, mentor_id: mData[0].id }));
        }
      }
    );
  }, []);

  const handleCourseChange = (courseId: number) => {
    const selectedCourse = courses.find(c => c.id === courseId);
    setFormData(prev => ({
      ...prev,
      course_id: courseId,
      internship_title: selectedCourse ? selectedCourse.title : prev.internship_title
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.full_name || !formData.degree || !formData.branch) {
      setError('Please fill in all mandatory fields (Candidate Name, Degree, and Branch).');
      return;
    }
    setSaving(true);
    setError('');
    try {
      const res = await api.createStudent(formData);
      navigate(`/students/${res.student_id}`);
    } catch (err: any) {
      setError(err.message || 'Failed to create student registration.');
    } finally {
      setSaving(false);
    }
  };

  const inputClass = "w-full px-4 py-3 text-base font-semibold text-slate-950 bg-white border-2 border-slate-300 rounded-lg placeholder:text-slate-400 focus:border-blue-600 focus:ring-3 focus:ring-blue-100 transition-all shadow-xs";

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-in fade-in duration-300">
      {/* Recommended Wizard Callout */}
      <div className="p-4 rounded-xl bg-gradient-to-r from-blue-50 via-indigo-50 to-amber-50 border-2 border-blue-200 flex flex-col md:flex-row items-start md:items-center justify-between gap-4 shadow-xs">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-lg bg-blue-600 text-white flex items-center justify-center shrink-0 shadow-sm">
            <Wand2 className="w-5 h-5" />
          </div>
          <div>
            <div className="text-sm font-bold text-slate-950 flex items-center space-x-2">
              <span>Looking for fast error-free generation?</span>
              <span className="text-[10px] uppercase font-extrabold px-2 py-0.5 rounded-full bg-amber-400 text-slate-950">Recommended</span>
            </div>
            <p className="text-xs text-slate-600">
              Use the new 5-Step Generator to automatically populate 36 attendance days, logbooks, project, and all 15 PDFs with 100% autofill!
            </p>
          </div>
        </div>
        <Link
          to="/wizard"
          className="shrink-0 px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs shadow-sm flex items-center space-x-1.5 cursor-pointer"
        >
          <span>Use 5-Step Generator</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </Link>
      </div>

      <div className="flex items-center justify-between">
        <button
          onClick={() => navigate(-1)}
          className="inline-flex items-center space-x-1.5 text-xs font-semibold text-slate-600 hover:text-slate-900 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Students</span>
        </button>
        <span className="text-xs text-slate-500 font-mono font-medium">STANDARD MANUAL REGISTRATION</span>
      </div>

      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="bg-brand-700 text-white p-6 border-b border-brand-800">
          <div className="flex items-center space-x-3">
            <div className="p-2.5 rounded-lg bg-gold-400 text-brand-950 font-bold shadow-xs">
              <UserPlus className="w-5 h-5" />
            </div>
            <div>
              <h1 className="text-xl font-serif font-bold text-white tracking-wide">
                Single-Entry Student Registration
              </h1>
              <p className="text-xs text-gold-200 mt-0.5">
                Enter student details once. The system automatically populates all 15 official documents without spelling mismatches.
              </p>
            </div>
          </div>
        </div>

        {error && (
          <div className="p-4 bg-red-50 border-b border-red-200 text-xs font-semibold text-red-700">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="p-6 md:p-8 space-y-8">
          {/* SECTION 1: PERSONAL DETAILS */}
          <div className="space-y-4">
            <div className="flex items-center space-x-2 pb-2 border-b border-slate-200 text-brand-700 font-serif font-bold text-sm">
              <UserCheck className="w-4 h-4 text-gold-500" />
              <span>1. PERSONAL PARTICULARS</span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-800 mb-1">
                  Full Name (as per matriculation) *
                </label>
                <input
                  type="text"
                  required
                  value={formData.full_name}
                  onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                  placeholder="e.g. Aarav Sharma"
                  className={inputClass}
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-800 mb-1">
                  Father's / Mother's Name *
                </label>
                <input
                  type="text"
                  required
                  value={formData.father_mother_name}
                  onChange={(e) => setFormData({ ...formData, father_mother_name: e.target.value })}
                  placeholder="e.g. Sh. Rakesh Sharma"
                  className={inputClass}
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-800 mb-1">Date of Birth</label>
                <input
                  type="date"
                  value={formData.dob}
                  onChange={(e) => setFormData({ ...formData, dob: e.target.value })}
                  className={inputClass}
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-800 mb-1">Gender</label>
                <select
                  value={formData.gender}
                  onChange={(e) => setFormData({ ...formData, gender: e.target.value })}
                  className={inputClass}
                >
                  <option value="Male">Male</option>
                  <option value="Female">Female</option>
                  <option value="Other">Other</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-800 mb-1">Mobile Contact *</label>
                <input
                  type="tel"
                  required
                  value={formData.mobile}
                  onChange={(e) => setFormData({ ...formData, mobile: e.target.value })}
                  placeholder="+91 98765 43210"
                  className={inputClass}
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-800 mb-1">Email Address *</label>
                <input
                  type="email"
                  required
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  placeholder="student@example.com"
                  className={inputClass}
                />
              </div>

              <div className="md:col-span-2">
                <label className="block text-xs font-semibold text-slate-800 mb-1">Residential Address</label>
                <input
                  type="text"
                  value={formData.address}
                  onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                  placeholder="Street / Colony / Landmark"
                  className={inputClass}
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-800 mb-1">City & State</label>
                <div className="flex space-x-2">
                  <input
                    type="text"
                    value={formData.city}
                    onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                    className={inputClass}
                  />
                  <input
                    type="text"
                    value={formData.state}
                    onChange={(e) => setFormData({ ...formData, state: e.target.value })}
                    className={inputClass}
                  />
                </div>
              </div>
            </div>
          </div>

          {/* SECTION 2: ACADEMIC DETAILS */}
          <div className="space-y-4">
            <div className="flex items-center space-x-2 pb-2 border-b border-slate-200 text-brand-700 font-serif font-bold text-sm">
              <Building2 className="w-4 h-4 text-gold-500" />
              <span>2. INSTITUTION & ACADEMIC CREDENTIALS</span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="md:col-span-2">
                <label className="block text-xs font-semibold text-slate-800 mb-1">
                  College / Institution Name (Franchise Centre)
                </label>
                <div className="relative">
                  <input
                    type="text"
                    readOnly
                    value={formData.college_name}
                    className="w-full px-3.5 py-2.5 text-xs rounded-lg border border-slate-300 bg-slate-100 text-slate-800 font-semibold cursor-not-allowed shadow-2xs"
                  />
                  <div className="absolute right-3 top-2.5 flex items-center space-x-1 text-[11px] text-emerald-700 font-semibold">
                    <ShieldCheck className="w-4 h-4" />
                    <span>Fixed Centre</span>
                  </div>
                </div>
                <p className="text-[11px] text-slate-500 mt-1">
                  Default franchise college. Editable in Centre Settings if franchise host institution changes.
                </p>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-800 mb-1">Degree Program *</label>
                <select
                  required
                  value={formData.degree}
                  onChange={(e) => {
                    const deg = e.target.value;
                    let defBranch = formData.branch;
                    if (deg === 'BCA') defBranch = 'Computer Science';
                    else if (deg === 'B.Sc (Bio)') defBranch = 'Biology';
                    else if (deg === 'B.Sc (Math)') defBranch = 'Mathematics';
                    else if (deg === 'B.Sc (Physics)') defBranch = 'Physics';
                    setFormData({ ...formData, degree: deg, branch: defBranch });
                  }}
                  className={inputClass}
                >
                  <option value="BCA">BCA (Bachelor of Computer Applications)</option>
                  <option value="B.Sc (Bio)">B.Sc (Biology)</option>
                  <option value="B.Sc (Math)">B.Sc (Mathematics)</option>
                  <option value="B.Sc (Physics)">B.Sc (Physics)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-800 mb-1">Branch / Department *</label>
                <input
                  type="text"
                  required
                  value={formData.branch}
                  onChange={(e) => setFormData({ ...formData, branch: e.target.value })}
                  placeholder="e.g. Computer Science / Mathematics / Physics / Biology"
                  className={inputClass}
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-800 mb-1">Semester / Year</label>
                <input
                  type="text"
                  value={formData.semester_year}
                  onChange={(e) => setFormData({ ...formData, semester_year: e.target.value })}
                  placeholder="e.g. 6th Semester"
                  className={inputClass}
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-800 mb-1">Academic Session</label>
                <input
                  type="text"
                  value={formData.academic_session}
                  onChange={(e) => setFormData({ ...formData, academic_session: e.target.value })}
                  placeholder="2025-2026"
                  className={inputClass}
                />
              </div>
            </div>
          </div>

          {/* SECTION 3: INTERNSHIP CONFIGURATION */}
          <div className="space-y-4">
            <div className="flex items-center space-x-2 pb-2 border-b border-slate-200 text-brand-700 font-serif font-bold text-sm">
              <BookOpen className="w-4 h-4 text-gold-500" />
              <span>3. INTERNSHIP TRACK & MENTOR ASSIGNMENT</span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-800 mb-1">Select Course Track *</label>
                <select
                  value={formData.course_id}
                  onChange={(e) => handleCourseChange(Number(e.target.value))}
                  className="w-full px-3.5 py-2.5 text-xs rounded-lg border border-slate-300 bg-white font-semibold text-brand-700 focus:ring-2 focus:ring-blue-600 focus:border-blue-600 focus:outline-hidden shadow-2xs"
                >
                  {courses.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.name} ({c.code}) — {c.duration_weeks} Wks
                    </option>
                  ))}
                </select>
              </div>

              <div className="md:col-span-2">
                <label className="block text-xs font-semibold text-slate-800 mb-1">Internship Title *</label>
                <input
                  type="text"
                  required
                  value={formData.internship_title}
                  onChange={(e) => setFormData({ ...formData, internship_title: e.target.value })}
                  className={inputClass}
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-800 mb-1">Supervising Mentor *</label>
                <select
                  value={formData.mentor_id}
                  onChange={(e) => setFormData({ ...formData, mentor_id: Number(e.target.value) })}
                  className={inputClass}
                >
                  {mentors.map((m) => (
                    <option key={m.id} value={m.id}>
                      {m.name} ({m.designation})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-800 mb-1">Commencement Date *</label>
                <input
                  type="date"
                  required
                  value={formData.start_date}
                  onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
                  className={inputClass}
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-800 mb-1">Completion Date *</label>
                <input
                  type="date"
                  required
                  value={formData.end_date}
                  onChange={(e) => setFormData({ ...formData, end_date: e.target.value })}
                  className={inputClass}
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-800 mb-1">Total Training Hours</label>
                <input
                  type="number"
                  value={formData.total_training_hours}
                  onChange={(e) => setFormData({ ...formData, total_training_hours: Number(e.target.value) })}
                  className={inputClass}
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-800 mb-1">Training Mode</label>
                <select
                  value={formData.mode}
                  onChange={(e) => setFormData({ ...formData, mode: e.target.value })}
                  className={inputClass}
                >
                  <option value="Offline">Offline (Classroom & Lab)</option>
                  <option value="Hybrid">Hybrid</option>
                  <option value="Online">Online</option>
                </select>
              </div>
            </div>
          </div>

          <div className="pt-4 border-t border-slate-200 flex items-center justify-end space-x-3">
            <button
              type="button"
              onClick={() => navigate(-1)}
              className="px-4 py-2.5 rounded-lg border border-slate-300 text-xs font-semibold text-slate-700 hover:bg-slate-50 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={saving}
              className="inline-flex items-center space-x-2 px-6 py-2.5 rounded-xl bg-brand-700 hover:bg-brand-800 text-white text-xs font-bold shadow-md transition-transform active:scale-95 disabled:opacity-50"
            >
              <Save className="w-4 h-4 text-gold-400" />
              <span>{saving ? 'Registering...' : 'Register Student & Create Package'}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
