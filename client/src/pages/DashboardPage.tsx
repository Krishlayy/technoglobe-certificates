import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { 
  Users, Award, CalendarCheck, Clock, CheckCircle2, AlertCircle, 
  BarChart3, Megaphone, UserPlus, FileText, ArrowUpRight, Search, 
  Filter, ShieldCheck, Download, PackageOpen, Wand2, ArrowRight
} from 'lucide-react';
import { StatCard } from '../components/common/StatCard';
import { api } from '../services/api';
import { Student } from '../types';

export const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState<any>(null);
  const [students, setStudents] = useState<Student[]>([]);
  const [search, setSearch] = useState('');
  const [courseFilter, setCourseFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboard();
  }, [courseFilter, statusFilter]);

  const loadDashboard = async () => {
    setLoading(true);
    try {
      const [sData, stData] = await Promise.all([
        api.getDashboardStats(),
        api.getStudents({ search, course: courseFilter, status: statusFilter })
      ]);
      setStats(sData);
      setStudents(stData);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    api.getStudents({ search, course: courseFilter, status: statusFilter }).then(setStudents);
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Top Banner */}
      <div className="bg-linear-to-r from-brand-700 via-brand-600 to-brand-800 rounded-2xl p-6 text-white shadow-md border border-brand-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2 text-gold-300 text-xs font-semibold tracking-wider uppercase mb-1">
            <ShieldCheck className="w-4 h-4" />
            <span>Authorized Bharatpur Franchise Portal</span>
          </div>
          <h1 className="text-2xl md:text-3xl font-serif font-bold text-white tracking-tight">
            Course Internship Management System
          </h1>
          <p className="text-xs md:text-sm text-slate-200 mt-1 max-w-2xl leading-relaxed">
            Single-entry student registration, automated curriculum logbooks, mentor evaluation rubrics, institutional compliance, and one-click 15-document internship package generation.
          </p>
        </div>

        <div className="flex items-center space-x-3 shrink-0">
          <Link
            to="/wizard"
            className="inline-flex items-center space-x-2 px-5 py-3 rounded-xl bg-amber-400 hover:bg-amber-300 text-slate-950 font-bold text-xs shadow-md transition-transform active:scale-95"
          >
            <Wand2 className="w-4 h-4 text-slate-950" />
            <span>5-Step Generator</span>
          </Link>
          <Link
            to="/document-editor"
            className="inline-flex items-center space-x-2 px-4 py-3 rounded-xl bg-brand-800 hover:bg-brand-900 text-gold-200 border border-brand-500 font-semibold text-xs shadow-sm transition-colors"
          >
            <FileText className="w-4 h-4 text-gold-400" />
            <span>Live Editor (50/50)</span>
          </Link>
        </div>
      </div>

      {/* Quick Wizard Callout Card */}
      <div className="bg-linear-to-r from-amber-500/15 via-blue-500/10 to-indigo-500/15 border-2 border-amber-300 rounded-2xl p-5 shadow-xs flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="flex items-center space-x-4">
          <div className="w-12 h-12 rounded-xl bg-amber-400 text-slate-950 flex items-center justify-center shrink-0 shadow-sm">
            <Wand2 className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-extrabold text-slate-950 text-base">New: 5-Step Guided Generator</span>
              <span className="text-[10px] font-extrabold uppercase px-2 py-0.5 rounded-full bg-amber-400 text-slate-950">100% Autofill</span>
            </div>
            <p className="text-xs text-slate-700 mt-0.5">
              Enter student name once. 36-day attendance, 126 hours, curriculum logbooks, mentor rubric, and offline JSON QR certificates are automatically pre-filled and ready for instant download.
            </p>
          </div>
        </div>
        <Link
          to="/wizard"
          className="shrink-0 px-6 py-3 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs shadow-md flex items-center space-x-2 transition-all cursor-pointer"
        >
          <span>Open 5-Step Generator</span>
          <ArrowRight className="w-4 h-4" />
        </Link>
      </div>

      {/* 8 Core Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Students"
          value={stats?.total_students ?? 0}
          subtitle="Registered Candidates"
          icon={Users}
          color="navy"
          onClick={() => navigate('/students')}
        />
        <StatCard
          title="Active Internships"
          value={stats?.active_internships ?? 0}
          subtitle="In-Progress Training"
          icon={Clock}
          color="blue"
        />
        <StatCard
          title="Completed Programs"
          value={stats?.completed_internships ?? 0}
          subtitle="Fulfilled & Certified"
          icon={CheckCircle2}
          color="emerald"
        />
        <StatCard
          title="Certificates Generated"
          value={stats?.certificates_generated ?? 0}
          subtitle="Officially Numbered & Locked"
          icon={Award}
          color="gold"
          onClick={() => navigate('/certificates')}
        />

        <StatCard
          title="Data Analytics Track"
          value={stats?.da_students ?? 0}
          subtitle="Python, SQL & Power BI"
          icon={BarChart3}
          color="purple"
        />
        <StatCard
          title="Digital Marketing Track"
          value={stats?.dm_students ?? 0}
          subtitle="SEO, Ads & Growth"
          icon={Megaphone}
          color="amber"
        />
        <StatCard
          title="Average Attendance"
          value={`${stats?.avg_attendance_pct ?? 0}%`}
          subtitle="Verified Logbook Hours"
          icon={CalendarCheck}
          color="emerald"
        />
        <StatCard
          title="Pending Evaluations"
          value={stats?.pending_evaluations ?? 0}
          subtitle="Awaiting Mentor Scoring"
          icon={AlertCircle}
          color={stats?.pending_evaluations > 0 ? "amber" : "navy"}
        />
      </div>

      {/* Quick Action Buttons */}
      <div className="bg-white p-4 rounded-xl border border-slate-200/90 shadow-xs">
        <h2 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-3">
          Quick Workflow Actions
        </h2>
        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-2.5">
          {[
            { label: "1. Add Student", icon: UserPlus, to: "/students/new" },
            { label: "2. View Syllabi", icon: FileText, to: "/courses" },
            { label: "3. Mark Attendance", icon: CalendarCheck, to: "/attendance" },
            { label: "4. Daily Logs", icon: Clock, to: "/daily-logs" },
            { label: "5. Projects", icon: BarChart3, to: "/projects" },
            { label: "6. Evaluations", icon: Award, to: "/certificates" },
            { label: "7. Certificates", icon: Award, to: "/certificates" },
            { label: "8. Verify QR", icon: ShieldCheck, to: "/verify" },
          ].map((act, i) => {
            const Icon = act.icon;
            return (
              <Link
                key={i}
                to={act.to}
                className="flex flex-col items-center justify-center p-2.5 rounded-lg bg-slate-50 hover:bg-brand-50 hover:text-brand-700 border border-slate-200/80 text-slate-700 text-xs font-medium transition-all text-center group shadow-2xs"
              >
                <Icon className="w-4 h-4 mb-1 text-slate-500 group-hover:text-brand-600 transition-colors" />
                <span className="text-[11px] leading-tight">{act.label}</span>
              </Link>
            );
          })}
        </div>
      </div>

      {/* Student Records Table & Search */}
      <div className="bg-white rounded-xl border border-slate-200/90 shadow-xs overflow-hidden">
        <div className="p-5 border-b border-slate-200 flex flex-col md:flex-row md:items-center justify-between gap-3">
          <div>
            <h2 className="text-base font-serif font-bold text-slate-900">
              Student Internship Records
            </h2>
            <p className="text-xs text-slate-500">
              Select a student to manage compliance, attendance, evaluation, and generate complete documentation packages.
            </p>
          </div>

          <form onSubmit={handleSearchSubmit} className="flex items-center space-x-2">
            <div className="relative">
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search name, college, roll no, cert #..."
                className="pl-9 pr-3 py-1.5 text-xs rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-brand-500 w-64"
              />
            </div>

            <select
              value={courseFilter}
              onChange={(e) => setCourseFilter(e.target.value)}
              className="px-2.5 py-1.5 text-xs rounded-lg border border-slate-300 bg-white focus:outline-none focus:ring-2 focus:ring-brand-500"
            >
              <option value="">All Courses</option>
              <option value="DA">Data Analytics</option>
              <option value="DM">Digital Marketing</option>
            </select>

            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-2.5 py-1.5 text-xs rounded-lg border border-slate-300 bg-white focus:outline-none focus:ring-2 focus:ring-brand-500"
            >
              <option value="">All Statuses</option>
              <option value="REGISTERED">Registered</option>
              <option value="TRAINING">Training</option>
              <option value="CERTIFIED">Certified</option>
            </select>
          </form>
        </div>

        {/* Table Content */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-600">
            <thead className="bg-slate-50 text-slate-500 font-semibold uppercase tracking-wider text-[10px] border-b border-slate-200">
              <tr>
                <th className="py-3 px-4">Student</th>
                <th className="py-3 px-4">College / University</th>
                <th className="py-3 px-4">Internship Track</th>
                <th className="py-3 px-4">Duration & Hours</th>
                <th className="py-3 px-4">Assigned Mentor</th>
                <th className="py-3 px-4">Status & Certificate</th>
                <th className="py-3 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {students.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-8 text-center text-slate-400">
                    No student records found matching your filters.
                  </td>
                </tr>
              ) : (
                students.map((st) => (
                  <tr key={st.id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="py-3 px-4">
                      <div className="font-semibold text-slate-900 text-sm">
                        {st.full_name}
                      </div>
                      <div className="text-[11px] text-slate-500">
                        {st.degree} ({st.branch})
                      </div>
                      {st.is_demo === 1 && (
                        <span className="inline-block mt-0.5 px-1.5 py-0.2 rounded text-[9px] font-bold bg-amber-100 text-amber-800 border border-amber-300">
                          DEMO RECORD
                        </span>
                      )}
                    </td>

                    <td className="py-3 px-4">
                      <div className="font-medium text-slate-800">{st.college_name}</div>
                      <div className="text-[11px] text-slate-400">{st.degree} - {st.branch} ({st.semester_year})</div>
                    </td>

                    <td className="py-3 px-4">
                      <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-semibold ${
                        st.course_code === 'DA' ? 'bg-indigo-100 text-indigo-800' : 'bg-amber-100 text-amber-800'
                      }`}>
                        {st.course_name}
                      </span>
                    </td>

                    <td className="py-3 px-4">
                      <div>{st.start_date} to {st.end_date}</div>
                      <div className="text-[11px] text-slate-400">{st.total_training_hours || 120} Hours</div>
                    </td>

                    <td className="py-3 px-4 font-medium text-slate-700">
                      {st.mentor_name || "Unassigned"}
                    </td>

                    <td className="py-3 px-4">
                      <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold ${
                        st.internship_status === 'CERTIFIED'
                          ? 'bg-emerald-100 text-emerald-800'
                          : 'bg-blue-100 text-blue-800'
                      }`}>
                        {st.internship_status || 'REGISTERED'}
                      </span>
                      {st.certificate_number && (
                        <div className="text-[10px] font-mono text-slate-500 mt-0.5">
                          {st.certificate_number}
                        </div>
                      )}
                    </td>

                    <td className="py-3 px-4 text-right">
                      <Link
                        to={`/students/${st.id}`}
                        className="inline-flex items-center space-x-1 px-3 py-1.5 rounded-lg bg-brand-50 hover:bg-brand-100 text-brand-700 font-semibold text-xs transition-colors"
                      >
                        <span>Manage Package</span>
                        <ArrowUpRight className="w-3.5 h-3.5" />
                      </Link>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
