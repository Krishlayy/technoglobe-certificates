import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, Users, UserPlus, CalendarCheck, BookOpen, 
  FolderKanban, Award, ShieldCheck, Settings, History, FileText,
  GraduationCap, Database, LayoutTemplate, Wand2, Layers, Sun
} from 'lucide-react';
import { useInstitution } from '../../contexts/InstitutionContext';

export const Sidebar: React.FC = () => {
  const { activeInstitution, isPoddar, isPoswal } = useInstitution();

  const navItems = [
    { to: "/", icon: LayoutDashboard, label: "Admin Dashboard", end: true },
    { to: "/wizard", icon: Wand2, label: "Step-by-Step Generator", isSpecial: true },
    { to: "/bulk-attendance", icon: Layers, label: "Bulk Batch Attendance (50+)", isSpecial: true },
    { to: "/students", icon: Users, label: "Student Directory" },
    { to: "/students/new", icon: UserPlus, label: "Register New Student" },
    { to: "/courses", icon: GraduationCap, label: isPoswal ? "Solar Curriculums" : "Course Curriculums" },
    { to: "/attendance", icon: CalendarCheck, label: "Daily Attendance & Planner" },
    { to: "/daily-logs", icon: BookOpen, label: "Activity Logbooks" },
    { to: "/projects", icon: FolderKanban, label: "Capstone Projects" },
    { to: "/certificates", icon: Award, label: "Certificates & Packages" },
    { to: "/document-editor", icon: FileText, label: "Live Document Editor (50/50)" },
    { to: "/templates", icon: LayoutTemplate, label: "Document Templates" },
    { to: "/backup-restore", icon: Database, label: "Backup & Restore" },
    { to: "/centre-settings", icon: Settings, label: "Portal Configuration" },
    { to: "/audit-logs", icon: History, label: "System Audit Trail" },
  ];

  return (
    <aside className="no-print w-64 bg-white border-r border-slate-200 min-h-[calc(100vh-4rem)] flex flex-col justify-between p-4 shrink-0 shadow-sm">
      <div className="space-y-1">
        {/* Active Workspace Header Badge */}
        <div className={`px-3 py-2.5 rounded-xl mb-3 border text-left ${
          isPoddar 
            ? 'bg-blue-50/70 border-blue-200 text-blue-950' 
            : 'bg-amber-50/70 border-amber-200 text-amber-950'
        }`}>
          <div className="flex items-center space-x-1.5 text-[10px] font-bold uppercase tracking-wider text-slate-500">
            {isPoddar ? <GraduationCap className="w-3.5 h-3.5 text-blue-600" /> : <Sun className="w-3.5 h-3.5 text-amber-600" />}
            <span>Active Portal</span>
          </div>
          <div className="text-xs font-bold text-slate-900 mt-0.5 truncate">
            {activeInstitution.name}
          </div>
          <div className="text-[10px] text-slate-500 truncate">
            {isPoddar ? 'Authority: Nitin Agarwal' : 'Authority: Madhuvan Gurjar'}
          </div>
        </div>

        <div className="px-3 py-1">
          <h2 className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
            Operations & Records
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
                        ? isPoddar
                          ? "bg-blue-100 text-blue-950 font-bold border-l-4 border-blue-600 shadow-xs"
                          : "bg-amber-100 text-amber-950 font-bold border-l-4 border-amber-600 shadow-xs"
                        : isPoddar
                        ? "bg-blue-50/60 text-blue-900 hover:bg-blue-100/70 font-semibold border border-blue-200/60"
                        : "bg-amber-50/60 text-amber-900 hover:bg-amber-100/70 font-semibold border border-amber-200/60"
                      : isActive
                      ? isPoddar
                        ? "bg-blue-50 text-blue-800 border-l-4 border-blue-600 font-semibold shadow-xs"
                        : "bg-amber-50 text-amber-900 border-l-4 border-amber-600 font-semibold shadow-xs"
                      : "text-slate-600 hover:text-slate-900 hover:bg-slate-50"
                  }`
                }
              >
                <div className="flex items-center space-x-3">
                  <Icon className={`w-4 h-4 shrink-0 ${item.isSpecial ? (isPoddar ? 'text-blue-700' : 'text-amber-700') : ''}`} />
                  <span>{item.label}</span>
                </div>
                {item.isSpecial && (
                  <span className={`text-[10px] px-1.5 py-0.5 rounded font-extrabold uppercase tracking-wider ${
                    isPoddar ? 'bg-blue-600 text-white' : 'bg-amber-500 text-slate-950'
                  }`}>
                    New
                  </span>
                )}
              </NavLink>
            );
          })}
        </nav>
      </div>

      {/* Compliance / Notice Card */}
      <div className={`mt-6 p-3 rounded-lg border text-[11px] leading-relaxed text-left ${
        isPoddar ? 'bg-blue-50/70 border-blue-200 text-blue-950' : 'bg-amber-50/70 border-amber-200 text-amber-950'
      }`}>
        <div className="flex items-center space-x-1.5 font-bold mb-1">
          <ShieldCheck className={`w-3.5 h-3.5 ${isPoddar ? 'text-blue-700' : 'text-amber-700'}`} />
          <span>{isPoddar ? 'Academic Compliance' : 'Industrial Compliance'}</span>
        </div>
        <p className="text-[10px] text-slate-600">
          {isPoddar 
            ? 'Poddar College official records. Documents require physical ink stamp and signature of Nitin Agarwal (Authority).'
            : 'Poswal Developers solar credentials (GST: 08ABIFP2454N1ZQ | MSME: UDYAM-RJ-06-0052498). Authorized by Madhuvan Singh Gurjar.'}
        </p>
      </div>
    </aside>
  );
};

