import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Users, UserPlus, Search, Filter, ArrowUpRight, GraduationCap, Building2 } from 'lucide-react';
import { api } from '../services/api';
import { Student } from '../types';

export const StudentsPage: React.FC = () => {
  const [students, setStudents] = useState<Student[]>([]);
  const [search, setSearch] = useState('');
  const [courseFilter, setCourseFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [institutionFilter, setInstitutionFilter] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStudents();
  }, [courseFilter, statusFilter, institutionFilter]);

  const loadStudents = async () => {
    setLoading(true);
    try {
      const data = await api.getStudents({ 
        search, 
        course: courseFilter, 
        status: statusFilter,
        institution_id: institutionFilter ? Number(institutionFilter) : undefined 
      });
      setStudents(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    loadStudents();
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-serif font-bold text-slate-900 tracking-tight">
            Student & Internship Directory
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Search, filter and manage registered candidates across TechnoGlobe and Poddar College programs.
          </p>
        </div>

        <Link
          to="/students/new"
          className="inline-flex items-center space-x-2 px-4 py-2.5 rounded-xl bg-brand-700 hover:bg-brand-800 text-white font-bold text-xs shadow-md transition-all shrink-0"
        >
          <UserPlus className="w-4 h-4 text-gold-400" />
          <span>Register New Student</span>
        </Link>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
        {/* Filters */}
        <div className="p-4 border-b border-slate-200 bg-slate-50/50 flex flex-col md:flex-row md:items-center justify-between gap-3">
          <form onSubmit={handleSearch} className="flex-1 max-w-md relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search by student name, college, roll no, cert #..."
              className="w-full pl-9 pr-3 py-1.5 text-xs rounded-lg border border-slate-300 bg-white focus:outline-none focus:ring-2 focus:ring-brand-500"
            />
          </form>

          <div className="flex items-center flex-wrap gap-2">
            <select
              value={institutionFilter}
              onChange={(e) => setInstitutionFilter(e.target.value)}
              className="px-3 py-1.5 text-xs rounded-lg border border-slate-300 bg-white text-slate-700 focus:outline-none focus:ring-2 focus:ring-brand-500 font-medium"
            >
              <option value="">All Institutions</option>
              <option value="1">TechnoGlobe (TG)</option>
              <option value="2">Poddar College (PODDAR)</option>
            </select>

            <select
              value={courseFilter}
              onChange={(e) => setCourseFilter(e.target.value)}
              className="px-3 py-1.5 text-xs rounded-lg border border-slate-300 bg-white text-slate-700 focus:outline-none focus:ring-2 focus:ring-brand-500"
            >
              <option value="">All Courses</option>
              <option value="DA">Data Analytics (DA)</option>
              <option value="DM">Digital Marketing (DM)</option>
              <option value="FS">Full Stack Web (FS)</option>
              <option value="AI">Python AI & ML (AI)</option>
              <option value="CS">Cyber Security (CS)</option>
              <option value="CC">Cloud & DevOps (CC)</option>
              <option value="JV">Java Enterprise (JV)</option>
              <option value="BI">Bioinformatics (BI)</option>
              <option value="AD">Android Apps (AD)</option>
            </select>

            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-3 py-1.5 text-xs rounded-lg border border-slate-300 bg-white text-slate-700 focus:outline-none focus:ring-2 focus:ring-brand-500"
            >
              <option value="">All Statuses</option>
              <option value="REGISTERED">Registered</option>
              <option value="IN_PROGRESS">In Training</option>
              <option value="CERTIFIED">Certified & Finalized</option>
            </select>
          </div>
        </div>

        {/* Directory Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-600">
            <thead className="bg-slate-100/70 text-slate-600 font-semibold uppercase tracking-wider text-[10px] border-b border-slate-200">
              <tr>
                <th className="py-3 px-4">Candidate & Roll No</th>
                <th className="py-3 px-4">Institution & College</th>
                <th className="py-3 px-4">Enrolled Course</th>
                <th className="py-3 px-4">Dates</th>
                <th className="py-3 px-4">Mentor</th>
                <th className="py-3 px-4">Status & Certificate</th>
                <th className="py-3 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {students.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-10 text-center text-slate-400">
                    No student records found. Click "Register New Student" or use Step-by-Step Generator.
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
                      <div className="flex items-center space-x-1.5 mb-0.5">
                        <span className={`inline-block px-1.5 py-0.2 rounded text-[9px] font-extrabold border ${
                          st.institution_code === 'PODDAR' || st.institution_id === 2
                            ? 'bg-amber-100 text-amber-900 border-amber-300'
                            : 'bg-blue-100 text-blue-900 border-blue-300'
                        }`}>
                          {st.institution_code || (st.institution_id === 2 ? 'PODDAR' : 'TG')}
                        </span>
                        <span className="font-medium text-slate-800 truncate max-w-[180px]">{st.college_name}</span>
                      </div>
                      <div className="text-[11px] text-slate-400">{st.degree} ({st.branch})</div>
                    </td>

                    <td className="py-3 px-4">
                      <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-semibold ${
                        st.course_code === 'DA' ? 'bg-indigo-100 text-indigo-800' : 'bg-amber-100 text-amber-800'
                      }`}>
                        {st.course_name}
                      </span>
                    </td>

                    <td className="py-3 px-4 text-slate-600">
                      <div>{st.start_date} to {st.end_date}</div>
                      <div className="text-[10px] text-slate-400">120 Hours</div>
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
