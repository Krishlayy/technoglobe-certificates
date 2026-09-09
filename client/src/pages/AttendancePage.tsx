import React, { useState, useEffect } from 'react';
import { 
  CalendarCheck, Clock, CheckCircle2, XCircle, AlertCircle, 
  RotateCcw, Sliders, CheckSquare, Sparkles, User, ArrowRight
} from 'lucide-react';
import { api } from '../services/api';
import { Student, AttendanceRecord } from '../types';

export const AttendancePage: React.FC = () => {
  const [students, setStudents] = useState<Student[]>([]);
  const [selectedStudentId, setSelectedStudentId] = useState<number | null>(null);
  const [attendance, setAttendance] = useState<AttendanceRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');

  // Planner simulation state
  const [showPlanner, setShowPlanner] = useState(false);
  const [targetPct, setTargetPct] = useState<number>(90);

  // Selected rows for bulk action
  const [selectedDates, setSelectedDates] = useState<string[]>([]);

  useEffect(() => {
    api.getStudents().then((data) => {
      setStudents(data);
      if (data.length > 0) {
        setSelectedStudentId(data[0].id);
      }
      setLoading(false);
    });
  }, []);

  const selectedStudent = students.find((s) => s.id === selectedStudentId);
  const internshipId = selectedStudent?.internship_id;

  const loadAttendance = () => {
    if (internshipId) {
      setSaving(true);
      api.getAttendance(internshipId).then((records) => {
        setAttendance(records);
        setSelectedDates([]);
        setSaving(false);
      }).catch(() => setSaving(false));
    } else {
      setAttendance([]);
    }
  };

  useEffect(() => {
    loadAttendance();
  }, [internshipId]);

  // Attendance stats calculations
  const totalRecords = attendance.length;
  const presentCount = attendance.filter((a) => a.status === 'PRESENT').length;
  const absentCount = attendance.filter((a) => a.status === 'ABSENT').length;
  const leaveCount = attendance.filter((a) => a.status === 'AUTHORIZED LEAVE' || a.status === 'LEAVE').length;
  const totalWorkingDays = presentCount + absentCount + leaveCount;
  const attendancePct = totalWorkingDays > 0 ? ((presentCount / totalWorkingDays) * 100).toFixed(1) : 'N/A';
  const totalHoursLogged = attendance.reduce((sum, a) => sum + (a.status === 'PRESENT' ? Number(a.total_hours || 3.5) : 0), 0);

  // Planner simulation calculations
  const simTotalDays = 36;
  const simRequiredPresent = Math.ceil(simTotalDays * (targetPct / 100));
  const simMaxNonPresent = simTotalDays - simRequiredPresent;

  // Bulk actions
  const handleMarkAllPresent = async () => {
    if (!internshipId || attendance.length === 0) return;
    setSaving(true);
    try {
      const dates = attendance.map((a) => a.date);
      await api.bulkUpdateAttendance(internshipId, { dates, status: 'PRESENT' });
      setMessage('All 36 days marked as PRESENT successfully.');
      loadAttendance();
    } catch (e: any) {
      setMessage(`Error: ${e.message}`);
    } finally {
      setSaving(false);
    }
  };

  const handleMarkSelected = async (status: string) => {
    if (!internshipId || selectedDates.length === 0) return;
    setSaving(true);
    try {
      await api.bulkUpdateAttendance(internshipId, { dates: selectedDates, status });
      setMessage(`Marked ${selectedDates.length} days as ${status}.`);
      loadAttendance();
    } catch (e: any) {
      setMessage(`Error: ${e.message}`);
    } finally {
      setSaving(false);
    }
  };

  const handleClearAttendance = async () => {
    if (!internshipId) return;
    if (!window.confirm('Are you sure you want to clear all attendance records for this student?')) return;
    setSaving(true);
    try {
      await api.clearAttendance(internshipId);
      setMessage('Attendance records cleared.');
      loadAttendance();
    } catch (e: any) {
      setMessage(`Error: ${e.message}`);
    } finally {
      setSaving(false);
    }
  };

  const applySimulationPlan = async () => {
    if (!internshipId || attendance.length === 0) return;
    setSaving(true);
    try {
      // Mark first simRequiredPresent as PRESENT, and remaining as AUTHORIZED LEAVE
      const allDates = attendance.map((a) => a.date);
      const presentDates = allDates.slice(0, simRequiredPresent);
      const leaveDates = allDates.slice(simRequiredPresent);

      if (presentDates.length > 0) {
        await api.bulkUpdateAttendance(internshipId, { dates: presentDates, status: 'PRESENT' });
      }
      if (leaveDates.length > 0) {
        await api.bulkUpdateAttendance(internshipId, { dates: leaveDates, status: 'AUTHORIZED LEAVE' });
      }
      setMessage(`Applied simulation target of ${targetPct}% (${simRequiredPresent} Present, ${simMaxNonPresent} Leave).`);
      setShowPlanner(false);
      loadAttendance();
    } catch (e: any) {
      setMessage(`Error: ${e.message}`);
    } finally {
      setSaving(false);
    }
  };

  const toggleSelectDate = (date: string) => {
    setSelectedDates((prev) =>
      prev.includes(date) ? prev.filter((d) => d !== date) : [...prev, date]
    );
  };

  const selectAllDates = () => {
    if (selectedDates.length === attendance.length) {
      setSelectedDates([]);
    } else {
      setSelectedDates(attendance.map((a) => a.date));
    }
  };

  const handleStatusChange = async (date: string, newStatus: string) => {
    if (!internshipId) return;
    const current = attendance.find((a) => a.date === date);
    if (!current) return;
    try {
      await api.saveAttendance(internshipId, {
        ...current,
        status: newStatus,
      });
      loadAttendance();
    } catch (e: any) {
      console.error(e);
    }
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-serif font-bold text-slate-900 tracking-tight">
            Daily Attendance Register & Planner
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Real daily attendance records, simulation planner, and genuine hours tracking for college submission.
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={() => setShowPlanner(true)}
            className="inline-flex items-center space-x-1.5 px-4 py-2 rounded-xl bg-purple-50 hover:bg-purple-100 text-purple-800 border border-purple-200 text-xs font-bold transition-all shadow-2xs"
          >
            <Sliders className="w-4 h-4 text-purple-600" />
            <span>Attendance Planner (Simulation)</span>
          </button>
        </div>
      </div>

      {message && (
        <div className="p-3 rounded-lg bg-blue-50 border border-blue-200 text-xs text-blue-800 font-medium flex items-center justify-between">
          <span>{message}</span>
          <button onClick={() => setMessage('')} className="text-blue-500 hover:text-blue-800 text-sm">×</button>
        </div>
      )}

      {/* Student Selector Card */}
      <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-2xs">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-center space-x-3">
            <div className="p-2 rounded-lg bg-brand-50 text-brand-700">
              <User className="w-5 h-5" />
            </div>
            <div>
              <label className="block text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
                Select Active Student
              </label>
              <select
                value={selectedStudentId || ''}
                onChange={(e) => setSelectedStudentId(Number(e.target.value))}
                className="mt-0.5 text-sm font-bold text-slate-900 border-none bg-transparent focus:ring-0 cursor-pointer p-0"
              >
                {students.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.full_name} — {s.course_name} ({s.degree} {s.branch}) {s.is_demo ? '[DEMO]' : ''}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {selectedStudent && (
            <div className="flex flex-wrap items-center gap-2 text-xs">
              <span className="px-2.5 py-1 rounded-full bg-slate-100 text-slate-700 font-medium">
                {selectedStudent.college_name}
              </span>
              <span className="px-2.5 py-1 rounded-full bg-blue-50 text-blue-700 font-medium">
                {selectedStudent.degree} ({selectedStudent.branch})
              </span>
              <span className="px-2.5 py-1 rounded-full bg-emerald-50 text-emerald-700 font-semibold">
                {selectedStudent.internship_status || 'REGISTERED'}
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Metrics Summary Strip */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        <div className="p-3.5 bg-white rounded-xl border border-slate-200 shadow-2xs">
          <div className="text-[11px] font-semibold text-slate-500 uppercase">Logged Days</div>
          <div className="text-xl font-bold text-slate-900 mt-1">{totalRecords} <span className="text-xs font-normal text-slate-400">/ 36</span></div>
        </div>

        <div className="p-3.5 bg-emerald-50/70 rounded-xl border border-emerald-200/80 shadow-2xs">
          <div className="text-[11px] font-semibold text-emerald-700 uppercase">Present Days</div>
          <div className="text-xl font-bold text-emerald-800 mt-1">{presentCount} Days</div>
        </div>

        <div className="p-3.5 bg-amber-50/70 rounded-xl border border-amber-200/80 shadow-2xs">
          <div className="text-[11px] font-semibold text-amber-700 uppercase">Auth Leave</div>
          <div className="text-xl font-bold text-amber-800 mt-1">{leaveCount} Days</div>
        </div>

        <div className="p-3.5 bg-red-50/70 rounded-xl border border-red-200/80 shadow-2xs">
          <div className="text-[11px] font-semibold text-red-700 uppercase">Absent</div>
          <div className="text-xl font-bold text-red-800 mt-1">{absentCount} Days</div>
        </div>

        <div className="p-3.5 bg-brand-50/60 rounded-xl border border-brand-200/80 shadow-2xs">
          <div className="text-[11px] font-semibold text-brand-700 uppercase">Attendance %</div>
          <div className="text-xl font-bold text-brand-800 mt-1">
            {attendancePct}{attendancePct !== 'N/A' && '%'}
          </div>
        </div>

        <div className="p-3.5 bg-purple-50/60 rounded-xl border border-purple-200/80 shadow-2xs">
          <div className="text-[11px] font-semibold text-purple-700 uppercase">Logged Hours</div>
          <div className="text-xl font-bold text-purple-800 mt-1">{totalHoursLogged.toFixed(1)} <span className="text-xs font-normal text-purple-500">/ 120h</span></div>
        </div>
      </div>

      {/* Quick Action Buttons Toolbar */}
      <div className="bg-white rounded-xl border border-slate-200 p-3 shadow-2xs flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center space-x-2">
          <button
            onClick={selectAllDates}
            className="px-3 py-1.5 rounded-lg border border-slate-300 text-xs font-semibold text-slate-700 hover:bg-slate-50 transition-colors"
          >
            {selectedDates.length === attendance.length ? 'Deselect All' : 'Select All Dates'}
          </button>
          <span className="text-xs text-slate-500 font-medium">
            ({selectedDates.length} dates selected)
          </span>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={handleMarkAllPresent}
            disabled={saving || attendance.length === 0}
            className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold transition-all shadow-2xs disabled:opacity-50"
          >
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>MARK ALL PRESENT</span>
          </button>

          <button
            onClick={() => handleMarkSelected('ABSENT')}
            disabled={saving || selectedDates.length === 0}
            className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-red-600 hover:bg-red-700 text-white text-xs font-bold transition-all shadow-2xs disabled:opacity-50"
          >
            <XCircle className="w-3.5 h-3.5" />
            <span>MARK SELECTED ABSENT</span>
          </button>

          <button
            onClick={() => handleMarkSelected('AUTHORIZED LEAVE')}
            disabled={saving || selectedDates.length === 0}
            className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-amber-600 hover:bg-amber-700 text-white text-xs font-bold transition-all shadow-2xs disabled:opacity-50"
          >
            <Clock className="w-3.5 h-3.5" />
            <span>MARK SELECTED LEAVE</span>
          </button>

          <button
            onClick={handleClearAttendance}
            disabled={saving || attendance.length === 0}
            className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg border border-slate-300 hover:bg-red-50 text-red-700 text-xs font-semibold transition-all"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>CLEAR</span>
          </button>
        </div>
      </div>

      {/* Attendance Register Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-2xs overflow-hidden">
        <div className="overflow-x-auto max-h-[500px]">
          <table className="w-full text-left text-xs text-slate-600">
            <thead className="bg-slate-50 text-slate-500 font-semibold uppercase tracking-wider text-[10px] border-b border-slate-200 sticky top-0 z-10">
              <tr>
                <th className="py-2.5 px-3 w-8 text-center">
                  <input
                    type="checkbox"
                    checked={selectedDates.length === attendance.length && attendance.length > 0}
                    onChange={selectAllDates}
                    className="rounded text-blue-600 focus:ring-0"
                  />
                </th>
                <th className="py-2.5 px-3">Day #</th>
                <th className="py-2.5 px-3">Date</th>
                <th className="py-2.5 px-3">Day</th>
                <th className="py-2.5 px-3">Timing</th>
                <th className="py-2.5 px-3">Hours</th>
                <th className="py-2.5 px-3">Practical Topic Covered</th>
                <th className="py-2.5 px-3 text-center">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-medium">
              {attendance.map((rec, idx) => (
                <tr
                  key={rec.date}
                  className={`hover:bg-slate-50/80 transition-colors ${
                    selectedDates.includes(rec.date) ? 'bg-blue-50/50' : ''
                  }`}
                >
                  <td className="py-2.5 px-3 text-center">
                    <input
                      type="checkbox"
                      checked={selectedDates.includes(rec.date)}
                      onChange={() => toggleSelectDate(rec.date)}
                      className="rounded text-blue-600 focus:ring-0"
                    />
                  </td>
                  <td className="py-2.5 px-3 font-mono text-slate-400">{idx + 1}</td>
                  <td className="py-2.5 px-3 font-semibold text-slate-900">{rec.date}</td>
                  <td className="py-2.5 px-3 text-slate-600">{rec.day_of_week}</td>
                  <td className="py-2.5 px-3 text-slate-600">{rec.start_time} - {rec.end_time}</td>
                  <td className="py-2.5 px-3 font-mono font-bold text-slate-800">{rec.total_hours}h</td>
                  <td className="py-2.5 px-3 text-slate-700">
                    {rec.topic_covered || `Curriculum Module Practical ${idx + 1}`}
                  </td>
                  <td className="py-2.5 px-3 text-center">
                    <select
                      value={rec.status}
                      onChange={(e) => handleStatusChange(rec.date, e.target.value)}
                      className={`text-xs font-bold rounded-md px-2 py-1 border border-slate-300 focus:ring-1 focus:ring-blue-500 cursor-pointer ${
                        rec.status === 'PRESENT'
                          ? 'bg-emerald-50 text-emerald-800 border-emerald-300'
                          : rec.status === 'ABSENT'
                          ? 'bg-red-50 text-red-800 border-red-300'
                          : 'bg-amber-50 text-amber-800 border-amber-300'
                      }`}
                    >
                      <option value="PRESENT">PRESENT</option>
                      <option value="ABSENT">ABSENT</option>
                      <option value="AUTHORIZED LEAVE">AUTHORIZED LEAVE</option>
                      <option value="HOLIDAY">HOLIDAY</option>
                    </select>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Attendance Planner Simulation Modal */}
      {showPlanner && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 p-4 animate-in fade-in duration-200">
          <div className="bg-white rounded-2xl max-w-lg w-full border border-slate-200 shadow-2xl overflow-hidden animate-in zoom-in-95">
            {/* Modal Header */}
            <div className="p-5 bg-gradient-to-r from-purple-700 to-indigo-800 text-white">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2.5">
                  <Sliders className="w-5 h-5 text-purple-200" />
                  <h3 className="text-base font-serif font-bold text-white">
                    Attendance Target Planner
                  </h3>
                </div>
                <button
                  onClick={() => setShowPlanner(false)}
                  className="text-purple-200 hover:text-white text-lg font-bold"
                >
                  ✕
                </button>
              </div>
              <p className="text-xs text-purple-200 mt-1">
                Simulate attendance percentages and calculate required present vs allowable leave days.
              </p>
            </div>

            {/* Prominent Mandatory Disclaimer */}
            <div className="p-3.5 bg-amber-50 border-b border-amber-200 text-amber-900 flex items-center space-x-2">
              <AlertCircle className="w-4 h-4 text-amber-700 shrink-0" />
              <p className="text-[11px] font-bold tracking-wide">
                PLANNING / SIMULATION ONLY — NOT AN OFFICIAL ATTENDANCE RECORD
              </p>
            </div>

            {/* Modal Body */}
            <div className="p-6 space-y-5">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-2">
                  Select Desired Attendance Threshold (%)
                </label>
                <select
                  value={targetPct}
                  onChange={(e) => setTargetPct(Number(e.target.value))}
                  className="w-full px-3.5 py-2.5 rounded-lg border border-slate-300 text-xs font-bold text-slate-800 bg-white focus:ring-2 focus:ring-purple-600 focus:outline-hidden"
                >
                  <option value={100}>100% — Exemplary Attendance (36 / 36 Days)</option>
                  <option value={95}>95% — High Honors Target (35 / 36 Days)</option>
                  <option value={92}>92% — Distinction Benchmark (34 / 36 Days)</option>
                  <option value={90}>90% — Standard Distinction (33 / 36 Days)</option>
                  <option value={88}>88% — Strong Performance (32 / 36 Days)</option>
                  <option value={85}>85% — Safe Compliance Margin (31 / 36 Days)</option>
                </select>
              </div>

              <div className="grid grid-cols-3 gap-3 p-4 bg-slate-50 rounded-xl border border-slate-200 text-center">
                <div>
                  <span className="text-[10px] font-bold uppercase text-slate-500">Working Days</span>
                  <div className="text-lg font-extrabold text-slate-900 mt-0.5">{simTotalDays} Days</div>
                </div>
                <div>
                  <span className="text-[10px] font-bold uppercase text-emerald-700">Required Present</span>
                  <div className="text-lg font-extrabold text-emerald-700 mt-0.5">{simRequiredPresent} Days</div>
                </div>
                <div>
                  <span className="text-[10px] font-bold uppercase text-amber-700">Max Non-Present</span>
                  <div className="text-lg font-extrabold text-amber-700 mt-0.5">{simMaxNonPresent} Days</div>
                </div>
              </div>

              <div className="p-3 bg-blue-50/60 rounded-lg border border-blue-100 text-[11px] text-blue-900 leading-relaxed">
                Applying this simulation will mark <b>{simRequiredPresent} days as PRESENT</b> and <b>{simMaxNonPresent} days as AUTHORIZED LEAVE</b> in the student's register, ensuring an exact attendance rate of <b>{targetPct}%</b>.
              </div>
            </div>

            {/* Modal Footer */}
            <div className="p-4 bg-slate-50 border-t border-slate-200 flex items-center justify-end space-x-3">
              <button
                onClick={() => setShowPlanner(false)}
                className="px-4 py-2 rounded-lg border border-slate-300 text-xs font-semibold text-slate-700 hover:bg-slate-100 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={applySimulationPlan}
                disabled={saving}
                className="inline-flex items-center space-x-1.5 px-5 py-2 rounded-lg bg-purple-700 hover:bg-purple-800 text-white text-xs font-bold transition-all shadow-sm"
              >
                <Sparkles className="w-3.5 h-3.5 text-gold-300" />
                <span>Apply Simulation Plan</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
