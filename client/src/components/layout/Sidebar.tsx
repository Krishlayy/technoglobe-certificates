import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, Users, UserPlus, CalendarCheck, BookOpen, 
  FolderKanban, Award, ShieldCheck, Settings, History, FileText,
  GraduationCap, Database, LayoutTemplate, Wand2, Layers
} from 'lucide-react';

export const Sidebar: React.FC = () => {
  const navItems = [
    { to: "/", icon: LayoutDashboard, label: "Admin Dashboard", end: true },
    { to: "/wizard", icon: Wand2, label: "Step-by-Step Generator", isSpecial: true },
    { to: "/bulk-attendance", icon: Layers, label: "Bulk Batch Attendance (50+)", isSpecial: true },
    { to: "/students", icon: Users, label: "Student Directory" },
    { to: "/students/new", icon: UserPlus, label: "Register New Student" },
    { to: "/courses", icon: GraduationCap, label: "Course Curriculums" },
    { to: "/attendance", icon: CalendarCheck, label: "Daily Attendance & Planner" },
    { to: "/daily-logs", icon: BookOpen, label: "Activity Logbooks" },
    { to: "/projects", icon: FolderKanban, label: "Capstone Projects" },
    { to: "/certificates", icon: Award, label: "Certificates & Packages" },
    { to: "/document-editor", icon: FileText, label: "Live Document Editor (50/50)" },
    { to: "/templates", icon: LayoutTemplate, label: "Document Templates" },
    { to: "/backup-restore", icon: Database, label: "Backup & Restore" },
    { to: "/centre-settings", icon: Settings, label: "Centre Configuration" },
    { to: "/audit-logs", icon: History, label: "System Audit Trail" },
  ];

  return (
    <aside className="no-print w-64 bg-white border-r border-slate-200 min-h-[calc(100vh-4rem)] flex flex-col justify-between p-4 shrink-0 shadow-sm">
      <div className="space-y-1">
        <div className="px-3 py-2">
          <h2 className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
            Operations & Documentation
          </h2>
        </div>
        <nav className="space-y-0.5">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.end}
                className={({ isActive }) =>
                  `flex items-center justify-between px-3 py-2.5 rounded-lg text-xs font-medium transition-all ${
                    item.isSpecial
                      ? isActive
                        ? "bg-gradient-to-r from-amber-100 to-amber-50 text-amber-950 font-bold border-l-4 border-amber-500 shadow-xs"
                        : "bg-amber-50/70 text-amber-900 hover:bg-amber-100/80 font-semibold border border-amber-200/60"
                      : isActive
                      ? "bg-brand-50 text-brand-700 border-l-4 border-brand-500 font-semibold shadow-xs"
                      : "text-slate-600 hover:text-brand-700 hover:bg-slate-50"
                  }`
                }
              >
                <div className="flex items-center space-x-3">
                  <Icon className={`w-4 h-4 shrink-0 ${item.isSpecial ? 'text-amber-700' : ''}`} />
                  <span>{item.label}</span>
                </div>
                {item.isSpecial && (
                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-amber-400 text-slate-950 font-extrabold uppercase tracking-wider">
                    New
                  </span>
                )}
              </NavLink>
            );
          })}
        </nav>
      </div>

      {/* Compliance / Notice Card */}
      <div className="mt-6 p-3 rounded-lg bg-amber-50/70 border border-amber-200/80 text-[11px] text-amber-900 leading-relaxed">
        <div className="flex items-center space-x-1.5 font-bold mb-1 text-amber-950">
          <ShieldCheck className="w-3.5 h-3.5 text-amber-700" />
          <span>Authorized Franchise</span>
        </div>
        <p className="text-[10px] text-amber-800">
          Official Bharatpur Centre franchise documentation. Documents require authorized physical signature & stamp before submission.
        </p>
      </div>
    </aside>
  );
};
