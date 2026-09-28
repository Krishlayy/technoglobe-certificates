import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, Users, CalendarCheck, Award, ShieldCheck, Settings, 
  History, FileText, GraduationCap, Database, LayoutTemplate, Wand2, Layers, Globe
} from 'lucide-react';
import { useInstitution } from '../../contexts/InstitutionContext';

export const Sidebar: React.FC = () => {
  const { activeInstitution } = useInstitution();

  const navItems = [
    { to: "/", icon: LayoutDashboard, label: "Admin Dashboard", end: true },
    { to: "/wizard", icon: Wand2, label: "15-Doc Dossier Wizard", isSpecial: true, badgeText: "Core" },
    { to: "/appreciation", icon: Award, label: "Appreciation Certificates", isSpecial: true, badgeText: "Studio" },
    { to: "/bulk-attendance", icon: Layers, label: "Bulk Attendance (50+)", isSpecial: true, badgeText: "Register" },
    { to: "/students", icon: Users, label: "Student Directory" },
    { to: "/courses", icon: GraduationCap, label: "IT Curriculums & Syllabi" },
    { to: "/certificates", icon: Award, label: "Certificates & Packages" },
    { to: "/document-editor", icon: FileText, label: "Live Document Editor" },
    { to: "/templates", icon: LayoutTemplate, label: "Document Templates" },
    { to: "/centre-settings", icon: Settings, label: "Center Configuration" },
    { to: "/backup-restore", icon: Database, label: "Backup & System DB" },
    { to: "/audit-logs", icon: History, label: "System Audit Trail" },
  ];

  return (
    <aside className="no-print w-64 bg-white border-r border-slate-200 min-h-[calc(100vh-4rem)] flex flex-col justify-between p-4 shrink-0 shadow-xs">
      <div className="space-y-1">
        {/* Organization Status Card */}
        <div className="p-3.5 rounded-2xl mb-3 border text-left shadow-xs bg-slate-50/90 border-slate-200 text-slate-900 ring-1 ring-slate-300/40">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-1.5 text-[10px] font-black uppercase tracking-wider text-blue-900">
              <Globe className="w-3.5 h-3.5 text-blue-700" />
              <span>Center Campus</span>
            </div>
            <span className="text-[9px] px-2 py-0.5 rounded-full font-black uppercase bg-blue-100 text-blue-900">
              Bharatpur
            </span>
          </div>

          <div className="text-xs font-black text-slate-900 mt-1.5 truncate">
            {activeInstitution.name}
          </div>
          <div className="text-[10px] text-slate-600 truncate mt-0.5">
            Signatory: <b className="text-slate-900">Nitin Agarwal</b> (Director)
          </div>
          <div className="text-[9px] text-slate-500 truncate mt-0.5">
            Near SP Office, Bharatpur (Raj.)
          </div>
        </div>

        <div className="px-3 py-1">
          <h2 className="text-[10px] font-black uppercase tracking-wider text-slate-400">
            Navigation Menu
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
                    isActive
                      ? 'bg-blue-900 text-white shadow-xs'
                      : item.isSpecial
                      ? 'bg-blue-50/70 hover:bg-blue-100/70 text-blue-950 font-black'
                      : 'text-slate-600 hover:bg-slate-100 hover:text-slate-950'
                  }`
                }
              >
                {({ isActive }) => (
                  <>
                    <div className="flex items-center space-x-2.5">
                      <Icon className={`w-4 h-4 shrink-0 ${item.isSpecial ? 'text-blue-700' : 'text-slate-500'}`} />
                      <span>{item.label}</span>
                    </div>
                    {item.badgeText && (
                      <span className={`text-[9px] px-1.5 py-0.5 rounded-md font-black tracking-wider uppercase ${
                        isActive
                          ? 'bg-white/20 text-white'
                          : 'bg-blue-600 text-white'
                      }`}>
                        {item.badgeText}
                      </span>
                    )}
                  </>
                )}
              </NavLink>
            );
          })}
        </nav>
      </div>

      {/* Footer Info */}
      <div className="pt-4 border-t border-slate-100 space-y-2">
        <div className="px-3 py-2 bg-slate-50 rounded-xl border border-slate-200/80">
          <div className="text-[10px] font-black text-slate-700 flex items-center justify-between">
            <span>Security & Verification</span>
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
          </div>
          <p className="text-[9px] text-slate-500 mt-1 leading-relaxed">
            HMAC Cryptographic QR Signing active for all issued credentials.
          </p>
        </div>
      </div>
    </aside>
  );
};
