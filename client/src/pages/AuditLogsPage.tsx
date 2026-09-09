import React, { useState, useEffect } from 'react';
import { History, ShieldCheck } from 'lucide-react';
import { api } from '../services/api';

export const AuditLogsPage: React.FC = () => {
  const [logs, setLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getAuditLogs().then((data) => {
      setLogs(data);
      setLoading(false);
    });
  }, []);

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      <div>
        <h1 className="text-2xl font-serif font-bold text-slate-900 tracking-tight">
          System Audit Trail & Access Logs
        </h1>
        <p className="text-xs text-slate-500 mt-0.5">
          Immutable chronological record of registrations, certificate finalizations, and configuration updates.
        </p>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-600">
            <thead className="bg-slate-50 text-slate-500 font-semibold uppercase tracking-wider text-[10px] border-b border-slate-200">
              <tr>
                <th className="py-3 px-4">Timestamp</th>
                <th className="py-3 px-4">Operator</th>
                <th className="py-3 px-4">Action Event</th>
                <th className="py-3 px-4">Entity</th>
                <th className="py-3 px-4">Details</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {logs.length === 0 ? (
                <tr>
                  <td colSpan={5} className="py-8 text-center text-slate-400">
                    No audit records recorded yet.
                  </td>
                </tr>
              ) : (
                logs.map((log) => (
                  <tr key={log.id} className="hover:bg-slate-50">
                    <td className="py-2.5 px-4 font-mono text-slate-500">{log.timestamp}</td>
                    <td className="py-2.5 px-4 font-semibold text-slate-800">{log.user_name}</td>
                    <td className="py-2.5 px-4">
                      <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-brand-50 text-brand-700">
                        {log.action}
                      </span>
                    </td>
                    <td className="py-2.5 px-4 text-slate-600">{log.entity_type} #{log.entity_id}</td>
                    <td className="py-2.5 px-4 font-mono text-[11px] text-slate-500 max-w-xs truncate">
                      {log.details_json}
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
