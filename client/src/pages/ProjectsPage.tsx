import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { FolderKanban, ArrowUpRight, BarChart3, Megaphone } from 'lucide-react';
import { api } from '../services/api';
import { Student } from '../types';

export const ProjectsPage: React.FC = () => {
  const [students, setStudents] = useState<Student[]>([]);

  useEffect(() => {
    api.getStudents().then(setStudents);
  }, []);

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      <div>
        <h1 className="text-2xl font-serif font-bold text-slate-900 tracking-tight">
          Capstone & Live Campaign Projects
        </h1>
        <p className="text-xs text-slate-500 mt-0.5">
          Review, edit, and approve student capstone projects for Data Analytics and Digital Marketing.
        </p>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-600">
            <thead className="bg-slate-50 text-slate-500 font-semibold uppercase tracking-wider text-[10px] border-b border-slate-200">
              <tr>
                <th className="py-3 px-4">Student</th>
                <th className="py-3 px-4">Track</th>
                <th className="py-3 px-4">Project Focus Area</th>
                <th className="py-3 px-4">Supervising Mentor</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4 text-right">Project Dossier</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {students.map((st) => (
                <tr key={st.id} className="hover:bg-slate-50/80 transition-colors">
                  <td className="py-3 px-4">
                    <div className="font-semibold text-slate-900">{st.full_name}</div>
                    <div className="text-[11px] text-slate-400">{st.college_name}</div>
                  </td>
                  <td className="py-3 px-4">
                    <span className={`px-2 py-0.5 rounded-full text-[10px] font-semibold ${
                      st.course_code === 'DA' ? 'bg-indigo-100 text-indigo-800' : 'bg-amber-100 text-amber-800'
                    }`}>
                      {st.course_name}
                    </span>
                  </td>
                  <td className="py-3 px-4 font-serif font-bold text-slate-800">
                    {st.course_code === 'DA'
                      ? 'Retail Sales Performance & Customer Churn Analytics'
                      : 'Omnichannel Lead Generation & SEO Growth Campaign'}
                  </td>
                  <td className="py-3 px-4 text-slate-700">{st.mentor_name}</td>
                  <td className="py-3 px-4">
                    <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800">
                      APPROVED
                    </span>
                  </td>
                  <td className="py-3 px-4 text-right">
                    <Link
                      to={`/students/${st.id}`}
                      className="inline-flex items-center space-x-1 px-3 py-1.5 rounded-lg bg-brand-50 hover:bg-brand-100 text-brand-700 font-semibold text-xs transition-colors"
                    >
                      <span>Review Project</span>
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
