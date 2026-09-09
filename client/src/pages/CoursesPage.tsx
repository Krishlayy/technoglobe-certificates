import React, { useState, useEffect } from 'react';
import { GraduationCap, BookOpen, Clock, Edit, Save, Plus, ChevronDown, ChevronUp } from 'lucide-react';
import { api } from '../services/api';
import { Course, CourseModule } from '../types';

export const CoursesPage: React.FC = () => {
  const [courses, setCourses] = useState<Course[]>([]);
  const [selectedCourse, setSelectedCourse] = useState<Course | null>(null);
  const [expandedModule, setExpandedModule] = useState<number | null>(null);
  const [editingModule, setEditingModule] = useState<CourseModule | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadCourses();
  }, []);

  const loadCourses = async () => {
    setLoading(true);
    try {
      const data = await api.getCourses();
      setCourses(data);
      if (data.length > 0) {
        setSelectedCourse(data[0]);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectCourse = async (courseId: number) => {
    try {
      const c = await api.getCourse(courseId);
      setSelectedCourse(c);
      setExpandedModule(null);
      setEditingModule(null);
    } catch (err) {
      console.error(err);
    }
  };

  const handleSaveModule = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingModule) return;
    try {
      await api.updateModule(editingModule.id, {
        title: editingModule.title,
        description: editingModule.description,
        topics: JSON.parse(editingModule.topics_json),
        practical_activities: JSON.parse(editingModule.practical_activities_json),
        learning_outcomes: JSON.parse(editingModule.learning_outcomes_json),
        hours: editingModule.hours
      });
      alert('Module updated successfully!');
      if (selectedCourse) {
        handleSelectCourse(selectedCourse.id);
      }
    } catch (err) {
      console.error(err);
      alert('Failed to save module');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[50vh] text-slate-500 text-xs">
        Loading courses & curriculums...
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-serif font-bold text-slate-900 tracking-tight">
            Course Curriculums & Module Management
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Preconfigured, industry-standard curriculums for Data Analytics and Digital Marketing. Fully editable by administrators.
          </p>
        </div>

        {/* Course Selection Tabs */}
        <div className="flex space-x-2 bg-slate-200/70 p-1 rounded-xl">
          {courses.map((c) => (
            <button
              key={c.id}
              onClick={() => handleSelectCourse(c.id)}
              className={`px-4 py-2 rounded-lg text-xs font-bold transition-all ${
                selectedCourse?.id === c.id
                  ? 'bg-brand-700 text-white shadow-sm'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              {c.name} ({c.code})
            </button>
          ))}
        </div>
      </div>

      {selectedCourse && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left: Overview Card */}
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-xs space-y-4">
            <div className="flex items-center space-x-2 text-brand-700 font-serif font-bold text-base">
              <GraduationCap className="w-5 h-5 text-gold-500" />
              <span>{selectedCourse.title}</span>
            </div>
            <p className="text-xs text-slate-600 leading-relaxed">
              {selectedCourse.description}
            </p>

            <div className="pt-3 border-t border-slate-100 space-y-2 text-xs">
              <div className="flex justify-between py-1 border-b border-slate-50">
                <span className="text-slate-400">Course Code:</span>
                <span className="font-mono font-bold text-slate-800">{selectedCourse.code}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-50">
                <span className="text-slate-400">Scheduled Duration:</span>
                <span className="font-semibold text-slate-800">{selectedCourse.duration_weeks} Weeks</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-50">
                <span className="text-slate-400">Total Structured Hours:</span>
                <span className="font-semibold text-slate-800">{selectedCourse.total_hours} Training Hours</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-50">
                <span className="text-slate-400">Total Modules:</span>
                <span className="font-semibold text-slate-800">{selectedCourse.modules?.length || 0} Modules</span>
              </div>
              <div className="flex justify-between py-1">
                <span className="text-slate-400">Delivery Mode:</span>
                <span className="font-semibold text-slate-800">{selectedCourse.default_mode}</span>
              </div>
            </div>

            <div className="pt-2">
              <span className="inline-block px-2.5 py-1 rounded-full text-[11px] font-bold bg-emerald-100 text-emerald-800">
                Active Franchise Curriculum
              </span>
            </div>
          </div>

          {/* Right: Modules List */}
          <div className="lg:col-span-2 space-y-3">
            <h2 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-2">
              Curriculum Modules ({selectedCourse.modules?.length || 0})
            </h2>

            {selectedCourse.modules?.map((m) => {
              const isExpanded = expandedModule === m.id;
              const topics = JSON.parse(m.topics_json || '[]');
              const practicals = JSON.parse(m.practical_activities_json || '[]');
              const outcomes = JSON.parse(m.learning_outcomes_json || '[]');

              return (
                <div
                  key={m.id}
                  className="bg-white rounded-xl border border-slate-200/90 shadow-2xs overflow-hidden transition-all"
                >
                  <div
                    onClick={() => setExpandedModule(isExpanded ? null : m.id)}
                    className="p-4 flex items-center justify-between cursor-pointer hover:bg-slate-50/70"
                  >
                    <div className="flex items-center space-x-3">
                      <span className="w-7 h-7 rounded-lg bg-brand-50 text-brand-700 font-bold text-xs flex items-center justify-center font-mono shrink-0">
                        {m.module_number}
                      </span>
                      <div>
                        <h3 className="text-xs font-bold text-slate-900 font-serif">
                          {m.title}
                        </h3>
                        <p className="text-[11px] text-slate-400 mt-0.5">
                          {m.description}
                        </p>
                      </div>
                    </div>

                    <div className="flex items-center space-x-3 shrink-0">
                      <span className="text-[11px] font-mono text-slate-500 bg-slate-100 px-2 py-0.5 rounded">
                        {m.hours} hrs
                      </span>
                      {isExpanded ? <ChevronUp className="w-4 h-4 text-slate-400" /> : <ChevronDown className="w-4 h-4 text-slate-400" />}
                    </div>
                  </div>

                  {isExpanded && (
                    <div className="p-4 bg-slate-50/70 border-t border-slate-100 text-xs space-y-3">
                      <div>
                        <span className="font-bold text-brand-800 text-[11px] uppercase">Core Topics:</span>
                        <ul className="list-disc list-inside mt-1 text-slate-600 space-y-0.5">
                          {topics.map((t: string, i: number) => (
                            <li key={i}>{t}</li>
                          ))}
                        </ul>
                      </div>

                      <div>
                        <span className="font-bold text-brand-800 text-[11px] uppercase">Practical Exercises:</span>
                        <ul className="list-disc list-inside mt-1 text-slate-600 space-y-0.5">
                          {practicals.map((p: string, i: number) => (
                            <li key={i}>{p}</li>
                          ))}
                        </ul>
                      </div>

                      {outcomes.length > 0 && (
                        <div>
                          <span className="font-bold text-brand-800 text-[11px] uppercase">Learning Outcomes:</span>
                          <ul className="list-disc list-inside mt-1 text-slate-600 space-y-0.5">
                            {outcomes.map((o: string, i: number) => (
                              <li key={i}>{o}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};
