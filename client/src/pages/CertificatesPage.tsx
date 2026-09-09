import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Award, ShieldCheck, Download, Printer, ExternalLink, PackageOpen, ArrowUpRight, CheckSquare, Square } from 'lucide-react';
import { api } from '../services/api';
import { Student } from '../types';

export const CertificatesPage: React.FC = () => {
  const [students, setStudents] = useState<Student[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedIds, setSelectedIds] = useState<number[]>([]);

  useEffect(() => {
    loadStudents();
  }, []);

  const loadStudents = () => {
    setLoading(true);
    api.getStudents().then((data) => {
      setStudents(data);
      setLoading(false);
    });
  };

  const validInternshipIds = students
    .map((s) => s.internship_id)
    .filter((id): id is number => typeof id === 'number');

  const certifiedInternshipIds = students
    .filter((s) => s.internship_status === 'CERTIFIED' && s.internship_id)
    .map((s) => s.internship_id as number);

  const toggleSelect = (internshipId: number) => {
    setSelectedIds((prev) =>
      prev.includes(internshipId)
        ? prev.filter((id) => id !== internshipId)
        : [...prev, internshipId]
    );
  };

  const toggleSelectAll = () => {
    if (selectedIds.length === validInternshipIds.length) {
      setSelectedIds([]);
    } else {
      setSelectedIds(validInternshipIds);
    }
  };

  const handleBatchPrint = (ids?: number[]) => {
    const url = api.getBatchPrintUrl(ids);
    window.open(url, '_blank');
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-serif font-bold text-slate-900 tracking-tight">
            Certificate & Package Register
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Officially numbered certificates and one-click batch PDF printing for colour cardstock printing.
          </p>
        </div>

        {/* Batch Print Actions */}
        <div className="flex flex-wrap items-center gap-2">
          {selectedIds.length > 0 && (
            <button
              onClick={() => handleBatchPrint(selectedIds)}
              className="inline-flex items-center space-x-2 px-3.5 py-2 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs shadow-sm transition-all transform active:scale-95 cursor-pointer"
              title="Merge and open selected certificates for printing"
            >
              <Printer className="w-3.5 h-3.5" />
              <span>Print Selected ({selectedIds.length})</span>
            </button>
          )}

          <button
            onClick={() => handleBatchPrint(certifiedInternshipIds.length > 0 ? certifiedInternshipIds : undefined)}
            className="inline-flex items-center space-x-2 px-4 py-2 rounded-xl bg-brand-700 hover:bg-brand-800 text-white font-bold text-xs shadow-sm transition-all transform active:scale-95 cursor-pointer"
            title="Batch print all certified candidates in one continuous print-ready document"
          >
            <Printer className="w-3.5 h-3.5 text-gold-400" />
            <span>Batch Print All ({certifiedInternshipIds.length || validInternshipIds.length})</span>
          </button>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-600">
            <thead className="bg-slate-50 text-slate-500 font-semibold uppercase tracking-wider text-[10px] border-b border-slate-200">
              <tr>
                <th className="py-3 px-3 w-10 text-center">
                  <input
                    type="checkbox"
                    checked={validInternshipIds.length > 0 && selectedIds.length === validInternshipIds.length}
                    onChange={toggleSelectAll}
                    className="rounded border-slate-300 text-blue-600 focus:ring-blue-500 cursor-pointer"
                    title="Select / Deselect All"
                  />
                </th>
                <th className="py-3 px-4">Candidate & College</th>
                <th className="py-3 px-4">Course Track</th>
                <th className="py-3 px-4">Certificate Number</th>
                <th className="py-3 px-4">Verification Code</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4 text-right">Downloads & Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {students.map((st) => {
                const isSelected = st.internship_id ? selectedIds.includes(st.internship_id) : false;
                return (
                  <tr
                    key={st.id}
                    className={`transition-colors ${
                      isSelected ? 'bg-blue-50/60' : 'hover:bg-slate-50/80'
                    }`}
                  >
                    <td className="py-3 px-3 text-center">
                      {st.internship_id ? (
                        <input
                          type="checkbox"
                          checked={isSelected}
                          onChange={() => toggleSelect(st.internship_id!)}
                          className="rounded border-slate-300 text-blue-600 focus:ring-blue-500 cursor-pointer"
                        />
                      ) : (
                        <span className="text-slate-300">—</span>
                      )}
                    </td>
                    <td className="py-3 px-4">
                      <div className="font-semibold text-slate-900">{st.full_name}</div>
                      <div className="text-[11px] text-slate-400">{st.college_name}</div>
                    </td>
                    <td className="py-3 px-4">
                      <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-brand-50 text-brand-700">
                        {st.course_name}
                      </span>
                    </td>
                    <td className="py-3 px-4 font-mono font-bold text-brand-800">
                      {st.certificate_number || 'PENDING FINALIZATION'}
                    </td>
                    <td className="py-3 px-4 font-mono text-slate-500">
                      {st.verification_code || '—'}
                    </td>
                    <td className="py-3 px-4">
                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                        st.internship_status === 'CERTIFIED'
                          ? 'bg-emerald-100 text-emerald-800'
                          : 'bg-amber-100 text-amber-800'
                      }`}>
                        {st.internship_status || 'PENDING'}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-right space-x-2">
                      {st.internship_id && (
                        <>
                          <a
                            href={api.getDocumentPdfUrl(st.internship_id, 'certificate')}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center space-x-1 px-2.5 py-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold text-xs transition-colors"
                            title="Print / View Certificate PDF"
                          >
                            <Award className="w-3.5 h-3.5 text-gold-600" />
                            <span>Cert PDF</span>
                          </a>

                          <a
                            href={api.getPackageZipUrl(st.internship_id)}
                            className="inline-flex items-center space-x-1 px-3 py-1.5 rounded-lg bg-gold-400 hover:bg-gold-300 text-brand-950 font-bold text-xs transition-colors shadow-2xs"
                            title="Download Complete 15-Document Package (.ZIP)"
                          >
                            <PackageOpen className="w-3.5 h-3.5" />
                            <span>ZIP Package</span>
                          </a>

                          <Link
                            to={`/students/${st.id}`}
                            className="inline-flex items-center p-1.5 rounded-lg text-slate-400 hover:text-slate-800 hover:bg-slate-100"
                          >
                            <ArrowUpRight className="w-4 h-4" />
                          </Link>
                        </>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

