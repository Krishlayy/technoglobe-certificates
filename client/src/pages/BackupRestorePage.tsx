import React, { useState } from 'react';
import { 
  Database, Download, Upload, AlertTriangle, CheckCircle2, 
  RotateCcw, Trash2, FileJson, ShieldAlert, Sparkles, HardDrive
} from 'lucide-react';
import { api } from '../services/api';

export const BackupRestorePage: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [restoring, setRestoring] = useState(false);
  const [resetting, setResetting] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [statusMessage, setStatusMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const handleDownloadBackup = () => {
    const url = api.getBackupDbUrl();
    window.open(url, '_blank');
  };

  const handleExportJson = async () => {
    setExporting(true);
    try {
      const data = await api.exportJson();
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `technoglobe_export_${new Date().toISOString().slice(0, 10)}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      setStatusMessage({ type: 'success', text: 'Full database export downloaded successfully in JSON format.' });
    } catch (e: any) {
      setStatusMessage({ type: 'error', text: `Export failed: ${e.message}` });
    } finally {
      setExporting(false);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleRestore = async () => {
    if (!selectedFile) {
      setStatusMessage({ type: 'error', text: 'Please select a valid SQLite database (.db) file to restore.' });
      return;
    }
    if (!window.confirm('Are you sure you want to restore the database? Current records will be overwritten (a safety snapshot will be kept on the server).')) {
      return;
    }
    setRestoring(true);
    setStatusMessage(null);
    try {
      const res = await api.restoreBackup(selectedFile);
      setStatusMessage({ type: 'success', text: res.message || 'Database successfully restored.' });
      setSelectedFile(null);
    } catch (e: any) {
      setStatusMessage({ type: 'error', text: e.message || 'Database restore failed.' });
    } finally {
      setRestoring(false);
    }
  };

  const handleResetDemo = async () => {
    if (!window.confirm('Reset demo data? This will recreate exactly 1 Data Analytics student and 1 Digital Marketing student.')) {
      return;
    }
    setResetting(true);
    setStatusMessage(null);
    try {
      const res = await api.resetDemoData();
      setStatusMessage({ type: 'success', text: res.message || 'Demo data successfully reset.' });
    } catch (e: any) {
      setStatusMessage({ type: 'error', text: e.message || 'Failed to reset demo data.' });
    } finally {
      setResetting(false);
    }
  };

  const handleDeleteDemo = async () => {
    if (!window.confirm('Delete all demo records? Official real student entries will remain untouched.')) {
      return;
    }
    setDeleting(true);
    setStatusMessage(null);
    try {
      const res = await api.deleteDemoData();
      setStatusMessage({ type: 'success', text: res.message || 'Demo data removed.' });
    } catch (e: any) {
      setStatusMessage({ type: 'error', text: e.message || 'Failed to delete demo data.' });
    } finally {
      setDeleting(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-in fade-in duration-300">
      <div>
        <h1 className="text-2xl font-serif font-bold text-slate-900 tracking-tight">
          Database Backup, Restore & Demo Data Management
        </h1>
        <p className="text-xs text-slate-500 mt-0.5">
          Download SQLite database snapshots, restore from verified backups, or manage system demo records.
        </p>
      </div>

      {statusMessage && (
        <div
          className={`p-4 rounded-xl border flex items-center justify-between text-xs font-semibold ${
            statusMessage.type === 'success'
              ? 'bg-emerald-50 border-emerald-200 text-emerald-800'
              : 'bg-red-50 border-red-200 text-red-800'
          }`}
        >
          <div className="flex items-center space-x-2">
            {statusMessage.type === 'success' ? (
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
            ) : (
              <AlertTriangle className="w-4 h-4 text-red-600" />
            )}
            <span>{statusMessage.text}</span>
          </div>
          <button
            onClick={() => setStatusMessage(null)}
            className="text-slate-400 hover:text-slate-700 text-sm"
          >
            ✕
          </button>
        </div>
      )}

      {/* SECTION 1: BACKUP & EXPORT */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="p-5 bg-slate-50 border-b border-slate-200 flex items-center space-x-3">
          <div className="p-2 rounded-lg bg-blue-50 text-blue-700">
            <Download className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-sm font-serif font-bold text-slate-900">
              Database Snapshots & Data Export
            </h2>
            <p className="text-xs text-slate-500">
              Download the active SQLite database or export complete structured JSON records.
            </p>
          </div>
        </div>

        <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 rounded-xl border border-slate-200 bg-slate-50/50 space-y-3">
            <div className="flex items-center space-x-2 text-xs font-bold text-slate-800">
              <Database className="w-4 h-4 text-brand-600" />
              <span>SQLite Database Backup (.db)</span>
            </div>
            <p className="text-[11px] text-slate-600 leading-relaxed">
              Downloads a binary snapshot of the entire database including all students, attendance logs, evaluations, and certificates.
            </p>
            <button
              onClick={handleDownloadBackup}
              className="w-full inline-flex items-center justify-center space-x-2 px-4 py-2 rounded-lg bg-brand-700 hover:bg-brand-800 text-white text-xs font-bold shadow-2xs transition-all"
            >
              <Download className="w-3.5 h-3.5 text-gold-400" />
              <span>Download technoglobe.db</span>
            </button>
          </div>

          <div className="p-4 rounded-xl border border-slate-200 bg-slate-50/50 space-y-3">
            <div className="flex items-center space-x-2 text-xs font-bold text-slate-800">
              <FileJson className="w-4 h-4 text-emerald-600" />
              <span>Complete Data Export (.json)</span>
            </div>
            <p className="text-[11px] text-slate-600 leading-relaxed">
              Exports all 17 system tables as a human-readable JSON dump suitable for external archival or cross-system auditing.
            </p>
            <button
              onClick={handleExportJson}
              disabled={exporting}
              className="w-full inline-flex items-center justify-center space-x-2 px-4 py-2 rounded-lg border border-slate-300 bg-white hover:bg-slate-50 text-slate-800 text-xs font-bold shadow-2xs transition-all disabled:opacity-50"
            >
              <Download className="w-3.5 h-3.5 text-emerald-600" />
              <span>{exporting ? 'Exporting...' : 'Export All Tables (JSON)'}</span>
            </button>
          </div>
        </div>
      </div>

      {/* SECTION 2: DATABASE RESTORE */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="p-5 bg-slate-50 border-b border-slate-200 flex items-center space-x-3">
          <div className="p-2 rounded-lg bg-amber-50 text-amber-700">
            <Upload className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-sm font-serif font-bold text-slate-900">
              Restore Database from File
            </h2>
            <p className="text-xs text-slate-500">
              Upload a previously downloaded SQLite database file (.db) to restore centre records.
            </p>
          </div>
        </div>

        <div className="p-6 space-y-4">
          <div className="p-3.5 bg-amber-50 rounded-xl border border-amber-200 flex items-start space-x-3 text-amber-900 text-xs">
            <AlertTriangle className="w-4 h-4 text-amber-700 shrink-0 mt-0.5" />
            <p className="leading-relaxed">
              <b>Important Notice:</b> Restoring will replace existing student and attendance records. An automatic safety snapshot (.bak) is created on the local server prior to restoration.
            </p>
          </div>

          <div className="border-2 border-dashed border-slate-300 rounded-xl p-6 text-center space-y-2 hover:border-brand-500 transition-colors bg-slate-50/40">
            <HardDrive className="w-8 h-8 text-slate-400 mx-auto" />
            <div className="text-xs text-slate-700 font-medium">
              {selectedFile ? (
                <span className="font-bold text-brand-700">{selectedFile.name} ({(selectedFile.size / 1024).toFixed(1)} KB)</span>
              ) : (
                <span>Select a .db database file from your local disk</span>
              )}
            </div>
            <input
              type="file"
              accept=".db,.sqlite,.sqlite3"
              onChange={handleFileChange}
              className="hidden"
              id="db-upload"
            />
            <label
              htmlFor="db-upload"
              className="inline-block px-4 py-1.5 rounded-lg border border-slate-300 bg-white hover:bg-slate-50 text-xs font-semibold text-slate-700 cursor-pointer shadow-2xs"
            >
              Browse Local Files
            </label>
          </div>

          <div className="flex justify-end">
            <button
              onClick={handleRestore}
              disabled={!selectedFile || restoring}
              className="inline-flex items-center space-x-2 px-5 py-2.5 rounded-xl bg-amber-600 hover:bg-amber-700 text-white text-xs font-bold shadow-sm transition-all disabled:opacity-50"
            >
              <Upload className="w-4 h-4" />
              <span>{restoring ? 'Verifying & Restoring...' : 'Restore Database Now'}</span>
            </button>
          </div>
        </div>
      </div>

      {/* SECTION 3: DEMO DATA MANAGEMENT */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="p-5 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="p-2 rounded-lg bg-purple-50 text-purple-700">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-sm font-serif font-bold text-slate-900">
                System Demo Data Controls
              </h2>
              <p className="text-xs text-slate-500">
                Pre-populated sample candidates for training staff and verifying document pipelines.
              </p>
            </div>
          </div>
          <span className="px-3 py-1 rounded-full bg-purple-100 text-purple-800 font-bold text-[10px] tracking-wide">
            DEMO DATA — NOT OFFICIAL
          </span>
        </div>

        <div className="p-6 space-y-4">
          <div className="p-3.5 bg-slate-50 rounded-xl border border-slate-200 text-xs text-slate-700 space-y-1">
            <div className="font-bold text-slate-900">Standard Demo Records:</div>
            <ul className="list-disc list-inside text-[11px] text-slate-600 space-y-0.5">
              <li><b>Aarav Sharma</b> — Data Analytics Track (BCA, Poddar College, Bharatpur)</li>
              <li><b>Priya Verma</b> — Digital Marketing Track (B.Sc Bio, Poddar College, Bharatpur)</li>
            </ul>
          </div>

          <div className="flex flex-wrap items-center justify-end gap-3 pt-2">
            <button
              onClick={handleDeleteDemo}
              disabled={deleting}
              className="inline-flex items-center space-x-1.5 px-4 py-2 rounded-lg border border-red-200 bg-red-50 hover:bg-red-100 text-red-700 text-xs font-semibold transition-all disabled:opacity-50"
            >
              <Trash2 className="w-3.5 h-3.5" />
              <span>{deleting ? 'Deleting...' : 'Delete Demo Data'}</span>
            </button>

            <button
              onClick={handleResetDemo}
              disabled={resetting}
              className="inline-flex items-center space-x-1.5 px-5 py-2 rounded-lg bg-purple-700 hover:bg-purple-800 text-white text-xs font-bold shadow-2xs transition-all disabled:opacity-50"
            >
              <RotateCcw className="w-3.5 h-3.5 text-purple-200" />
              <span>{resetting ? 'Resetting...' : 'Reset Demo Data'}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
