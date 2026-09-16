import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { 
  ShieldCheck, BookOpen, User, ExternalLink, RefreshCw, 
  GraduationCap, Sun, Globe, Award, Wand2, Layers, Check, ArrowLeftRight
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { useInstitution } from '../../contexts/InstitutionContext';

export const Navbar: React.FC = () => {
  const { logout, user } = useAuth();
  const { activeInstitution, selectInstitution, isPoddar, isPoswal, isTechnoglobe, institutions } = useInstitution();
  const [showSwitchModal, setShowSwitchModal] = useState(false);
  const [showGuideModal, setShowGuideModal] = useState(false);
  const navigate = useNavigate();

  const handleCycleInstitution = () => {
    if (isPoddar) {
      selectInstitution(2); // Poswal
    } else if (isPoswal) {
      selectInstitution(3); // Technoglobe
    } else {
      selectInstitution(1); // Poddar
    }
  };

  const navBg = isPoswal 
    ? 'bg-[#5B1B1B] border-[#7F1D1D]' 
    : isTechnoglobe 
    ? 'bg-[#0F2942] border-[#1E3A8A]' 
    : 'bg-[#0B2545] border-[#134074]';

  return (
    <header className={`no-print sticky top-0 z-40 text-white border-b shadow-md transition-colors duration-300 ${navBg}`}>
      <div className="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand & Active Organization Identity */}
          <div className="flex items-center space-x-2 sm:space-x-3">
            <Link to="/" className="flex items-center space-x-2 sm:space-x-3 group">
              <div className="h-10 px-2 bg-white rounded-lg flex items-center justify-center shadow-xs group-hover:opacity-95 transition-opacity">
                <img 
                  src={isPoswal ? "/poswal_logo.png" : (isTechnoglobe ? "/technoglobe_logo.png" : "/poddar_logo.png")} 
                  alt={activeInstitution.name} 
                  className="h-8 w-auto object-contain" 
                />
              </div>
              <div className="flex flex-col text-left">
                <div className="flex items-center space-x-1.5">
                  <span className="font-serif font-black text-sm sm:text-base tracking-wider text-white">
                    {activeInstitution.full_name}
                  </span>
                </div>
                <span className="text-[9px] sm:text-[10px] uppercase tracking-widest text-amber-300 font-bold truncate max-w-[280px] sm:max-w-none">
                  {isPoswal ? 'Solar Power & Industrial Training Division' : (isTechnoglobe ? 'Technoglobe - Advanced IT Training & Development' : 'Near SP Office, Bharatpur • poddarcollege.org')}
                </span>
              </div>
            </Link>
          </div>

          {/* Center & Right Navigation Actions */}
          <div className="flex items-center space-x-2 sm:space-x-3">
            {/* Quick 3-way Switch Button */}
            <button
              onClick={handleCycleInstitution}
              className={`inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-xl text-xs font-black transition-all border shadow-md cursor-pointer ${
                isPoswal
                  ? 'bg-amber-500 hover:bg-amber-400 text-slate-950 border-amber-300 ring-2 ring-amber-400/30'
                  : isTechnoglobe
                  ? 'bg-indigo-500 hover:bg-indigo-400 text-white border-indigo-300 ring-2 ring-indigo-400/30'
                  : 'bg-blue-500 hover:bg-blue-400 text-white border-blue-300 ring-2 ring-blue-400/30'
              }`}
              title="Click to cycle between Poddar, Poswal & Technoglobe"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              <span>
                {isPoddar ? 'Poddar 🎓 → Poswal ☀️' : isPoswal ? 'Poswal ☀️ → Techno 🌐' : 'Techno 🌐 → Poddar 🎓'}
              </span>
            </button>

            {/* Switch Portal Modal Button */}
            <button
              onClick={() => setShowSwitchModal(true)}
              className="hidden md:inline-flex items-center space-x-1 px-2.5 py-1.5 rounded-lg bg-white/10 hover:bg-white/20 text-slate-200 text-xs font-semibold border border-white/20 transition-colors cursor-pointer"
              title="View all 3 portal workspaces"
            >
              <ArrowLeftRight className="w-3 h-3" />
              <span>Portals (3)</span>
            </button>

            {/* User Guide */}
            <button
              onClick={() => setShowGuideModal(true)}
              className="inline-flex items-center space-x-1.5 px-2.5 py-1.5 rounded-xl bg-white/10 hover:bg-white/20 text-white text-xs font-bold border border-white/20 transition-all cursor-pointer"
              title="Open Zero-Mistake System Guide"
            >
              <BookOpen className="w-3.5 h-3.5 text-amber-300" />
              <span className="hidden sm:inline">Guide</span>
            </button>

            {/* Public Verify */}
            <Link
              to="/verify"
              className="hidden lg:inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-white/10 hover:bg-white/20 text-amber-200 text-xs font-bold border border-amber-400/30 transition-colors shadow-sm"
            >
              <ShieldCheck className="w-3.5 h-3.5 text-amber-400" />
              <span>Verify</span>
              <ExternalLink className="w-3 h-3 ml-0.5 opacity-70" />
            </Link>

            {/* User Profile and Logout */}
            <div className="flex items-center space-x-2 pl-2 border-l border-white/20">
              <div className="w-8 h-8 rounded-full bg-white/10 border border-white/20 flex items-center justify-center text-slate-200">
                <User className="w-4 h-4 text-amber-300" />
              </div>
              <div className="hidden sm:flex flex-col text-left mr-1">
                <span className="text-xs font-bold text-white">{user?.name || (isPoswal ? "Madhuvan Singh Gurjar" : "Nitin Agarwal")}</span>
                <span className="text-[10px] text-amber-300 font-bold">{isPoswal ? 'Authority' : 'Director / Authority'}</span>
              </div>
              
              <button 
                onClick={() => {
                  logout();
                  navigate('/login');
                }}
                className="text-xs px-2.5 py-1 rounded-lg bg-red-900/60 hover:bg-red-800 text-red-200 border border-red-700/50 transition-colors cursor-pointer"
                title="Sign out"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* 3-Organization Switcher Modal */}
      {showSwitchModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-xs p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-3xl max-w-xl w-full p-6 shadow-2xl text-left animate-in fade-in zoom-in-95 duration-200">
            <div className="flex items-center justify-between pb-4 border-b border-slate-800 mb-4">
              <div>
                <h3 className="text-lg font-bold text-white">Switch Operating Portal</h3>
                <p className="text-xs text-slate-400">Select which isolated organization workspace to manage:</p>
              </div>
              <button
                onClick={() => setShowSwitchModal(false)}
                className="text-slate-400 hover:text-white text-sm px-2 py-1 rounded-lg hover:bg-slate-800 cursor-pointer"
              >
                ✕
              </button>
            </div>

            <div className="space-y-3">
              {/* Poddar Option */}
              <div
                onClick={() => {
                  selectInstitution(1);
                  setShowSwitchModal(false);
                }}
                className={`p-4 rounded-2xl border-2 cursor-pointer transition-all flex items-start justify-between ${
                  isPoddar 
                    ? 'bg-blue-950 border-blue-500 ring-2 ring-blue-500/30' 
                    : 'bg-slate-800/60 border-slate-700 hover:border-slate-500'
                }`}
              >
                <div className="flex items-start space-x-3">
                  <div className="w-11 h-11 rounded-xl bg-white p-1 flex items-center justify-center shrink-0">
                    <img src="/poddar_logo.png" alt="Poddar Logo" className="max-h-full max-w-full object-contain" />
                  </div>
                  <div>
                    <div className="flex items-center space-x-1.5 text-blue-400 text-xs font-bold">
                      <GraduationCap className="w-3.5 h-3.5" />
                      <span>Option 1: Poddar College (PCTM)</span>
                    </div>
                    <div className="text-sm font-bold text-white mt-0.5">PODDAR COLLEGE OF TECHNOLOGY & MANAGEMENT</div>
                    <div className="text-[11px] text-slate-300 mt-0.5">
                      Address: Near SP Office, Bharatpur • Email: nitin_pitm@yahoo.com
                    </div>
                    <div className="text-[10px] text-amber-300 mt-1">
                      Authority: Nitin Agarwal | Web: poddarcollege.org
                    </div>
                  </div>
                </div>
                {isPoddar && <Check className="w-5 h-5 text-blue-400 shrink-0 mt-1" />}
              </div>

              {/* Poswal Option */}
              <div
                onClick={() => {
                  selectInstitution(2);
                  setShowSwitchModal(false);
                }}
                className={`p-4 rounded-2xl border-2 cursor-pointer transition-all flex items-start justify-between ${
                  isPoswal 
                    ? 'bg-amber-950 border-amber-500 ring-2 ring-amber-500/30' 
                    : 'bg-slate-800/60 border-slate-700 hover:border-slate-500'
                }`}
              >
                <div className="flex items-start space-x-3">
                  <div className="w-11 h-11 rounded-xl bg-white p-1 flex items-center justify-center shrink-0">
                    <img src="/poswal_logo.png" alt="Poswal Logo" className="max-h-full max-w-full object-contain" />
                  </div>
                  <div>
                    <div className="flex items-center space-x-1.5 text-amber-400 text-xs font-bold">
                      <Sun className="w-3.5 h-3.5" />
                      <span>Option 2: Poswal Developers</span>
                    </div>
                    <div className="text-sm font-bold text-white mt-0.5">POSWAL DEVELOPERS</div>
                    <div className="text-[11px] text-slate-300 mt-0.5">
                      Solar PV & Industrial Training • GST & MSME Registered
                    </div>
                    <div className="text-[10px] text-amber-300 mt-1">
                      Authority: Madhuvan Singh Gurjar | Mob: 9414694727
                    </div>
                  </div>
                </div>
                {isPoswal && <Check className="w-5 h-5 text-amber-400 shrink-0 mt-1" />}
              </div>

              {/* Technoglobe Option */}
              <div
                onClick={() => {
                  selectInstitution(3);
                  setShowSwitchModal(false);
                }}
                className={`p-4 rounded-2xl border-2 cursor-pointer transition-all flex items-start justify-between ${
                  isTechnoglobe 
                    ? 'bg-indigo-950 border-indigo-500 ring-2 ring-indigo-500/30' 
                    : 'bg-slate-800/60 border-slate-700 hover:border-slate-500'
                }`}
              >
                <div className="flex items-start space-x-3">
                  <div className="w-11 h-11 rounded-xl bg-white p-1 flex items-center justify-center shrink-0">
                    <img src="/technoglobe_logo.png" alt="Technoglobe Logo" className="max-h-full max-w-full object-contain" />
                  </div>
                  <div>
                    <div className="flex items-center space-x-1.5 text-indigo-400 text-xs font-bold">
                      <Globe className="w-3.5 h-3.5" />
                      <span>Option 3: Technoglobe Jaipur</span>
                    </div>
                    <div className="text-sm font-bold text-white mt-0.5">TECHNOGLOBE - ADVANCED IT TRAINING & DEVELOPMENT</div>
                    <div className="text-[11px] text-slate-300 mt-0.5">
                      Plot No. 4, Gopalpura Bypass Road, Jaipur • info@technoglobe.co.in
                    </div>
                    <div className="text-[10px] text-amber-300 mt-1">
                      Authority: Nitin Agarwal | Web: technoglobe.co.in
                    </div>
                  </div>
                </div>
                {isTechnoglobe && <Check className="w-5 h-5 text-indigo-400 shrink-0 mt-1" />}
              </div>
            </div>

            <div className="mt-5 text-right">
              <button
                onClick={() => setShowSwitchModal(false)}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-xl text-xs font-semibold cursor-pointer"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Zero-Mistake Guide Modal */}
      {showGuideModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-xs p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-3xl max-w-2xl w-full p-6 sm:p-8 shadow-2xl text-left animate-in fade-in zoom-in-95 duration-200 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between pb-4 border-b border-slate-800 mb-6">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 rounded-xl bg-amber-400 text-slate-950 flex items-center justify-center font-black text-lg">
                  📖
                </div>
                <div>
                  <h3 className="text-xl font-bold text-white">Zero-Mistake Quick Guide</h3>
                  <p className="text-xs text-slate-400">System operation guide</p>
                </div>
              </div>
              <button
                onClick={() => setShowGuideModal(false)}
                className="text-slate-400 hover:text-white text-base px-2.5 py-1.5 rounded-lg hover:bg-slate-800 cursor-pointer"
              >
                ✕
              </button>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="p-4 rounded-2xl bg-slate-800/80 border border-slate-700">
                <div className="text-amber-400 font-bold text-xs uppercase mb-1">1. Choose Portal</div>
                <p className="text-xs text-slate-300 leading-relaxed">
                  Switch between <b>Poddar College</b> (IT tracks), <b>Poswal Developers</b> (Solar Engineering), and <b>Technoglobe Jaipur</b>. All 3 are completely independent.
                </p>
              </div>

              <div className="p-4 rounded-2xl bg-slate-800/80 border border-slate-700">
                <div className="text-blue-400 font-bold text-xs uppercase mb-1">2. 6-Step Dossier Wizard</div>
                <p className="text-xs text-slate-300 leading-relaxed">
                  Enter student details once. Faculty name is optional (leave empty for Nitin Agarwal authority signature). Review all 15 files in Step 5 before generating.
                </p>
              </div>

              <div className="p-4 rounded-2xl bg-slate-800/80 border border-slate-700">
                <div className="text-emerald-400 font-bold text-xs uppercase mb-1">3. Appreciation Studio</div>
                <p className="text-xs text-slate-300 leading-relaxed">
                  Generate custom certificates of appreciation & excellence with scannable QR verification and authentic signatures/stamps.
                </p>
              </div>

              <div className="p-4 rounded-2xl bg-slate-800/80 border border-slate-700">
                <div className="text-purple-400 font-bold text-xs uppercase mb-1">4. Bulk Attendance Register</div>
                <p className="text-xs text-slate-300 leading-relaxed">
                  Generate and download complete 36-day master batch attendance registers and daily books for 50+ students in 1 click.
                </p>
              </div>
            </div>

            <div className="mt-6 pt-4 border-t border-slate-800 flex justify-end">
              <button
                onClick={() => setShowGuideModal(false)}
                className="px-5 py-2.5 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-xs font-bold cursor-pointer"
              >
                Close Guide
              </button>
            </div>
          </div>
        </div>
      )}
    </header>
  );
};

export default Navbar;
