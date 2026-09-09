import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { BookOpen, Search, ArrowUpRight } from 'lucide-react';
import { api } from '../services/api';
import { Student } from '../types';

export const DailyLogsPage: React.FC = () => {
  const [students, setStudents] = useState<Student[]>([]);

  useEffect(() => {
    api.getStudents().then(setStudents);
  }, []);

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      <div>
        <h1 className="text-2xl font-serif font-bold text-slate-900 tracking-tight">
          Daily Activity Logbooks & Diaries
        </h1>
        <p className="text-xs text-slate-500 mt-0.5">
          Student activity logs, daily practical activities, tools used, and mentor verification remarks.
        </p>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-600">
            <thead className="bg-slate-50 text-slate-500 font-semibold uppercase tracking-wider text-[10px] border-b border-slate-200">
              <tr>
                <th className="py-3 px-4">Candidate</th>
                <th className="py-3 px-4">Course Track</th>
                <th className="py-3 px-4">College</th>
                <th className="py-3 px-4">Assigned Mentor</th>
                <th className="py-3 px-4 text-right">Logbook Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {students.map((st) => (
                <tr key={st.id} className="hover:bg-slate-50/80 transition-colors">
                  <td className="py-3 px-4">
                    <div className="font-semibold text-slate-900">{st.full_name}</div>
                    <div className="text-[11px] text-slate-400">{st.degree} ({st.branch})</div>
                  </td>
                  <td className="py-3 px-4">
                    <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-brand-50 text-brand-700">
                      {st.course_name}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-slate-700">{st.college_name}</td>
                  <td className="py-3 px-4 text-slate-700">{st.mentor_name}</td>
                  <td className="py-3 px-4 text-right">
                    <Link
                      to={`/students/${st.id}`}
                      className="inline-flex items-center space-x-1 px-3 py-1.5 rounded-lg bg-brand-50 hover:bg-brand-100 text-brand-700 font-semibold text-xs transition-colors"
                    >
                      <span>View & Print Logbook</span>
                      <ArrowUpRight className="w-3.5 h-3.5" />
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
