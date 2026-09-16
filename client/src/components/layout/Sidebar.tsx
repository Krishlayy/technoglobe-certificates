import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, Users, UserPlus, CalendarCheck, BookOpen, 
  FolderKanban, Award, ShieldCheck, Settings, History, FileText,
  GraduationCap, Database, LayoutTemplate, Wand2, Layers, Sun, Globe, RefreshCw
} from 'lucide-react';
import { useInstitution } from '../../contexts/InstitutionContext';

export const Sidebar: React.FC = () => {
  const { activeInstitution, isPoddar, isPoswal, isTechnoglobe, selectInstitution } = useInstitution();

  const handleCycleInstitution = () => {
    if (isPoddar) {
      selectInstitution(2); // Poswal
    } else if (isPoswal) {
      selectInstitution(3); // Technoglobe
    } else {
      selectInstitution(1); // Poddar
    }
  };

  const navItems = [
    { to: "/", icon: LayoutDashboard, label: "Admin Dashboard", end: true },
    { to: "/wizard", icon: Wand2, label: "15-Doc Dossier Wizard", isSpecial: true, badgeText: "Core" },
    { to: "/appreciation", icon: Award, label: "Appreciation Certificates", isSpecial: true, badgeText: "Custom" },
    { to: "/bulk-attendance", icon: Layers, label: "Bulk Attendance (50+)", isSpecial: true, badgeText: "Register" },
    { to: "/students", icon: Users, label: "Student Directory" },
    { to: "/courses", icon: GraduationCap, label: isPoswal ? "Solar Curriculums" : "Course Curriculums" },
    { to: "/attendance", icon: CalendarCheck, label: "Daily Attendance Register" },
    { to: "/certificates", icon: Award, label: "Certificates & Packages" },
    { to: "/document-editor", icon: FileText, label: "Live Document Editor" },
    { to: "/templates", icon: LayoutTemplate, label: "Document Templates" },
    { to: "/backup-restore", icon: Database, label: "Backup & Restore" },
    { to: "/centre-settings", icon: Settings, label: "Portal Configuration" },
    { to: "/audit-logs", icon: History, label: "System Audit Trail" },
  ];

  return (
    <aside className="no-print w-64 bg-white border-r border-slate-200 min-h-[calc(100vh-4rem)] flex flex-col justify-between p-4 shrink-0 shadow-sm">
      <div className="space-y-1">
        {/* Active Portal Workspace Card */}
        <div className={`p-3 rounded-2xl mb-3 border text-left shadow-xs transition-all ${
          isPoswal
            ? 'bg-amber-50/90 border-amber-200 text-amber-950 ring-1 ring-amber-300/40'
            : isTechnoglobe
            ? 'bg-indigo-50/90 border-indigo-200 text-indigo-950 ring-1 ring-indigo-300/40'
            : 'bg-blue-50/90 border-blue-200 text-blue-950 ring-1 ring-blue-300/40'
        }`}>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-1.5 text-[10px] font-black uppercase tracking-wider text-slate-500">
              {isPoswal ? <Sun className="w-3.5 h-3.5 text-amber-600" /> : isTechnoglobe ? <Globe className="w-3.5 h-3.5 text-indigo-600" /> : <GraduationCap className="w-3.5 h-3.5 text-blue-600" />}
              <span>Active Portal</span>
            </div>
            <span className={`text-[9px] px-2 py-0.5 rounded-full font-black uppercase ${
              isPoswal ? 'bg-amber-200 text-amber-900' : isTechnoglobe ? 'bg-indigo-200 text-indigo-900' : 'bg-blue-200 text-blue-900'
            }`}>
              {isPoswal ? 'Option 2' : isTechnoglobe ? 'Option 3' : 'Option 1'}
            </span>
          </div>

          <div className="text-xs font-black text-slate-900 mt-1.5 truncate">
            {activeInstitution.name}
          </div>
          <div className="text-[10px] text-slate-500 truncate mt-0.5">
            Authority: {isPoswal ? 'Madhuvan Gurjar' : 'Nitin Agarwal'}
          </div>

          {/* 1-Click Switch Button */}
          <button
            onClick={handleCycleInstitution}
            className={`w-full mt-2.5 py-1.5 px-2 rounded-xl text-[11px] font-black flex items-center justify-center space-x-1.5 transition-all cursor-pointer shadow-xs border ${
              isPoswal
                ? 'bg-white hover:bg-amber-100 text-amber-900 border-amber-300'
                : isTechnoglobe
                ? 'bg-white hover:bg-indigo-100 text-indigo-900 border-indigo-300'
                : 'bg-white hover:bg-blue-100 text-blue-900 border-blue-300'
            }`}
            title="Switch portal workspace"
          >
            <RefreshCw className="w-3 h-3" />
            <span>{isPoddar ? 'Switch to Poswal ☀️' : isPoswal ? 'Switch to Techno 🌐' : 'Switch to Poddar 🎓'}</span>
          </button>
        </div>

        <div className="px-3 py-1">
          <h2 className="text-[10px] font-black uppercase tracking-wider text-slate-400">
            Core Operations
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
                  `flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-bold transition-all ${
                    item.isSpecial
                      ? isActive
                        ? isPoswal
                          ? "bg-amber-100 text-amber-950 font-black border-l-4 border-amber-600 shadow-xs"
                          : isTechnoglobe
                          ? "bg-indigo-100 text-indigo-950 font-black border-l-4 border-indigo-600 shadow-xs"
                          : "bg-blue-100 text-blue-950 font-black border-l-4 border-blue-600 shadow-xs"
                        : isPoswal
                        ? "bg-amber-50/60 text-amber-900 hover:bg-amber-100/70 border border-amber-200/60"
                        : isTechnoglobe
                        ? "bg-indigo-50/60 text-indigo-900 hover:bg-indigo-100/70 border border-indigo-200/60"
                        : "bg-blue-50/60 text-blue-900 hover:bg-blue-100/70 border border-blue-200/60"
                      : isActive
                      ? isPoswal
                        ? "bg-amber-50 text-amber-900 border-l-4 border-amber-600 font-black shadow-xs"
                        : isTechnoglobe
                        ? "bg-indigo-50 text-indigo-900 border-l-4 border-indigo-600 font-black shadow-xs"
                        : "bg-blue-50 text-blue-900 border-l-4 border-blue-600 font-black shadow-xs"
                      : "text-slate-600 hover:text-slate-900 hover:bg-slate-50 font-semibold"
                  }`
                }
              >
                <div className="flex items-center space-x-2.5">
                  <Icon className={`w-4 h-4 shrink-0 ${item.isSpecial ? (isPoswal ? 'text-amber-700' : isTechnoglobe ? 'text-indigo-700' : 'text-blue-700') : 'text-slate-500'}`} />
                  <span>{item.label}</span>
                </div>
                {item.isSpecial && (
                  <span className={`text-[9px] px-1.5 py-0.5 rounded-md font-black uppercase tracking-wider ${
                    isPoswal ? 'bg-amber-500 text-slate-950' : isTechnoglobe ? 'bg-indigo-600 text-white' : 'bg-blue-600 text-white'
                  }`}>
                    {item.badgeText || "Core"}
                  </span>
                )}
              </NavLink>
            );
          })}
        </nav>
      </div>

      {/* Footer Info */}
      <div className="pt-3 border-t border-slate-100 space-y-1">
        <div className="text-[10px] text-slate-400 text-center font-mono">
          Franchise System v3.5
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
