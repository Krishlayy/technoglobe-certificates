import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ShieldCheck, BookOpen, User, ExternalLink, ArrowLeftRight, Check, Sun, GraduationCap, RefreshCw } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { useInstitution } from '../../contexts/InstitutionContext';

export const Navbar: React.FC = () => {
  const { logout, user } = useAuth();
  const { activeInstitution, selectInstitution, isPoddar, isPoswal, institutions } = useInstitution();
  const [showSwitchModal, setShowSwitchModal] = useState(false);
  const [showGuideModal, setShowGuideModal] = useState(false);
  const navigate = useNavigate();

  const handleQuickToggle = () => {
    if (isPoddar) {
      selectInstitution(2);
    } else {
      selectInstitution(1);
    }
  };

  return (
    <header className={`no-print sticky top-0 z-40 text-white border-b shadow-md transition-colors duration-300 ${
      isPoddar ? 'bg-[#0B2545] border-[#134074]' : 'bg-[#5B1B1B] border-[#7F1D1D]'
    }`}>
      <div className="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand & Active Organization Identity */}
          <div className="flex items-center space-x-2 sm:space-x-3">
            {/* How to Use Guide Button */}
            <button
              onClick={() => setShowGuideModal(true)}
              className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-white/10 hover:bg-white/20 text-white text-xs font-bold border border-white/20 transition-all cursor-pointer shadow-xs"
              title="Open Easy User Guide"
            >
              <BookOpen className="w-3.5 h-3.5 text-amber-300" />
              <span className="hidden sm:inline">User Guide</span>
            </button>
            <Link to="/" className="flex items-center space-x-2 sm:space-x-3 group">
              <div className="h-10 px-2 bg-white rounded-lg flex items-center justify-center shadow-xs group-hover:opacity-95 transition-opacity">
                <img 
                  src={isPoddar ? "/poddar_logo.png" : "/poswal_logo.png"} 
                  alt={activeInstitution.name} 
                  className="h-8 w-auto object-contain" 
                />
              </div>
              <div className="flex flex-col text-left">
                <div className="flex items-center space-x-1.5">
                  <span className="font-serif font-bold text-sm sm:text-base tracking-wider text-white">
                    {activeInstitution.full_name}
                  </span>
                </div>
                <span className="text-[9px] sm:text-[10px] uppercase tracking-widest text-amber-300 font-semibold">
                  {isPoddar ? 'Academic & Technical Degree Certifications' : 'Solar Power & Industrial Training Certifications'}
                </span>
              </div>
            </Link>
          </div>

          {/* Center / Right: 1-Click Institution Quick Switcher Toggle */}
          <div className="flex items-center space-x-2 sm:space-x-3">
            {/* How to Use Guide Button */}
            <button
              onClick={() => setShowGuideModal(true)}
              className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-white/10 hover:bg-white/20 text-white text-xs font-bold border border-white/20 transition-all cursor-pointer shadow-xs"
              title="Open Easy User Guide"
            >
              <BookOpen className="w-3.5 h-3.5 text-amber-300" />
              <span className="hidden sm:inline">User Guide</span>
            </button>
            {/* Always-Visible Quick Switch Button */}
            <button
              onClick={handleQuickToggle}
              className={`inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-xl text-xs font-bold transition-all border shadow-md cursor-pointer ${
                isPoddar
                  ? 'bg-amber-500 hover:bg-amber-400 text-slate-950 border-amber-300 ring-2 ring-amber-400/30'
                  : 'bg-blue-500 hover:bg-blue-400 text-white border-blue-300 ring-2 ring-blue-400/30'
              }`}
              title={isPoddar ? "Click to switch to Poswal Developers Portal" : "Click to switch to Poddar College Portal"}
            >
              <RefreshCw className="w-3.5 h-3.5" />
              <span>
                {isPoddar ? 'Switch to Poswal Devs ☀️' : 'Switch to Poddar College 🎓'}
              </span>
            </button>

            {/* Switch Portal Modal Button (For full details) */}
            <button
              onClick={() => setShowSwitchModal(true)}
              className="hidden md:inline-flex items-center space-x-1 px-2.5 py-1.5 rounded-lg bg-white/10 hover:bg-white/20 text-slate-200 text-xs font-semibold border border-white/20 transition-colors cursor-pointer"
              title="View all institution options"
            >
              <ArrowLeftRight className="w-3 h-3" />
              <span>All Portals</span>
            </button>

            <Link
              to="/verify"
              className="hidden xl:inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-md bg-white/10 hover:bg-white/20 text-amber-200 text-xs font-medium border border-amber-400/30 transition-colors shadow-sm"
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
                <span className="text-xs font-semibold text-white">{user?.name || (isPoddar ? "Nitin Agarwal" : "Madhuvan Singh Gurjar")}</span>
                <span className="text-[10px] text-amber-300 font-medium">Authority</span>
              </div>
              
              <button 
                onClick={() => {
                  logout();
                  navigate('/login');
                }}
                className="text-xs px-2.5 py-1 rounded bg-red-900/60 hover:bg-red-800 text-red-200 border border-red-700/50 transition-colors cursor-pointer"
                title="Sign out of system"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Organization Switcher Modal */}
      {showSwitchModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-xs p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl max-w-lg w-full p-6 shadow-2xl text-left animate-in fade-in zoom-in-95 duration-200">
            <div className="flex items-center justify-between pb-4 border-b border-slate-800 mb-4">
              <div>
                <h3 className="text-lg font-bold text-white">Switch Operating Portal</h3>
                <p className="text-xs text-slate-400">Select which independent organization workspace to manage:</p>
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
                className={`p-4 rounded-xl border-2 cursor-pointer transition-all flex items-start justify-between ${
                  isPoddar 
                    ? 'bg-blue-950 border-blue-500 ring-2 ring-blue-500/30' 
                    : 'bg-slate-800/60 border-slate-700 hover:border-slate-500'
                }`}
              >
                <div className="flex items-start space-x-3">
                  <div className="w-10 h-10 rounded-lg bg-white p-1 flex items-center justify-center shrink-0">
                    <img src="/poddar_logo.png" alt="Poddar Logo" className="max-h-full max-w-full object-contain" />
                  </div>
                  <div>
                    <div className="flex items-center space-x-1.5 text-blue-400 text-xs font-bold">
                      <GraduationCap className="w-3.5 h-3.5" />
                      <span>Option 1: Poddar College</span>
                    </div>
                    <div className="text-sm font-bold text-white mt-0.5">PODDAR COLLEGE OF TECHNOLOGY & MANAGEMENT</div>
                    <div className="text-[11px] text-slate-300 mt-1">
                      Courses: Data Analytics, MERN, AI/ML, Cyber Security, Java, Cloud.
                    </div>
                    <div className="text-[10px] text-slate-400 mt-1">
                      Authority: Nitin Agarwal | Contact: 9414293370
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
                className={`p-4 rounded-xl border-2 cursor-pointer transition-all flex items-start justify-between ${
                  isPoswal 
                    ? 'bg-amber-950 border-amber-500 ring-2 ring-amber-500/30' 
                    : 'bg-slate-800/60 border-slate-700 hover:border-slate-500'
                }`}
              >
                <div className="flex items-start space-x-3">
                  <div className="w-10 h-10 rounded-lg bg-white p-1 flex items-center justify-center shrink-0">
                    <img src="/poswal_logo.png" alt="Poswal Logo" className="max-h-full max-w-full object-contain" />
                  </div>
                  <div>
                    <div className="flex items-center space-x-1.5 text-amber-400 text-xs font-bold">
                      <Sun className="w-3.5 h-3.5" />
                      <span>Option 2: Poswal Developers</span>
                    </div>
                    <div className="text-sm font-bold text-white mt-0.5">POSWAL DEVELOPERS</div>
                    <div className="text-[11px] text-slate-300 mt-1">
                      Courses: Solar PV Installation, Inverter Tech, Panel Mounting, O&M.
                    </div>
                    <div className="text-[10px] text-slate-400 mt-1">
                      Authority: Madhuvan Singh Gurjar | Contact: 9414694727
                    </div>
                  </div>
                </div>
                {isPoswal && <Check className="w-5 h-5 text-amber-400 shrink-0 mt-1" />}
              </div>
            </div>

            <div className="mt-5 text-right">
              <button
                onClick={() => setShowSwitchModal(false)}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg text-xs font-semibold cursor-pointer"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
      {/* Easy User Guide Modal */}
      {showGuideModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-xs p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-3xl max-w-2xl w-full p-6 sm:p-8 shadow-2xl text-left animate-in fade-in zoom-in-95 duration-200 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between pb-4 border-b border-slate-800 mb-6">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 rounded-xl bg-amber-400 text-slate-950 flex items-center justify-center font-bold text-lg">
                  📖
                </div>
                <div>
                  <h3 className="text-xl font-bold text-white">Zero-Mistake Quick Guide</h3>
                  <p className="text-xs text-slate-400">How to operate the system effortlessly in 4 simple steps</p>
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
              {/* Step 1 */}
              <div className="p-4 rounded-2xl bg-slate-800/80 border border-slate-700">
                <div className="flex items-center space-x-2 text-amber-400 font-bold text-xs uppercase tracking-wider mb-1">
                  <span className="w-5 h-5 rounded-full bg-amber-400 text-slate-950 flex items-center justify-center text-[10px] font-black">1</span>
                  <span>Select Institution Portal</span>
                </div>
                <h4 className="text-sm font-bold text-white mb-1">Poddar vs. Poswal</h4>
                <p className="text-xs text-slate-300 leading-relaxed">
                  Use the 1-click switch button in the top navbar to toggle between <b>Poddar College</b> (IT & Computer Science) and <b>Poswal Developers</b> (Solar PV Engineering).
                </p>
              </div>

              {/* Step 2 */}
              <div className="p-4 rounded-2xl bg-slate-800/80 border border-slate-700">
                <div className="flex items-center space-x-2 text-blue-400 font-bold text-xs uppercase tracking-wider mb-1">
                  <span className="w-5 h-5 rounded-full bg-blue-400 text-slate-950 flex items-center justify-center text-[10px] font-black">2</span>
                  <span>5-Step Guided Generator</span>
                </div>
                <h4 className="text-sm font-bold text-white mb-1">Single-Entry Autofill</h4>
                <p className="text-xs text-slate-300 leading-relaxed">
                  Enter student particulars once in <b>Step-by-Step Generator</b>. 36-day attendance, weekly reviews, rubrics, and project documentation are pre-filled automatically.
                </p>
              </div>

              {/* Step 3 */}
              <div className="p-4 rounded-2xl bg-slate-800/80 border border-slate-700">
                <div className="flex items-center space-x-2 text-emerald-400 font-bold text-xs uppercase tracking-wider mb-1">
                  <span className="w-5 h-5 rounded-full bg-emerald-400 text-slate-950 flex items-center justify-center text-[10px] font-black">3</span>
                  <span>Instant Package & Certificate</span>
                </div>
                <h4 className="text-sm font-bold text-white mb-1">15 PDFs in 1-Click ZIP</h4>
                <p className="text-xs text-slate-300 leading-relaxed">
                  Download the complete official 15-document dossier ZIP or print the landscape completion certificate with physical ink stamp box and dual signatures.
                </p>
              </div>

              {/* Step 4 */}
              <div className="p-4 rounded-2xl bg-slate-800/80 border border-slate-700">
                <div className="flex items-center space-x-2 text-purple-400 font-bold text-xs uppercase tracking-wider mb-1">
                  <span className="w-5 h-5 rounded-full bg-purple-400 text-slate-950 flex items-center justify-center text-[10px] font-black">4</span>
                  <span>Instant QR Verification</span>
                </div>
                <h4 className="text-sm font-bold text-white mb-1">Cryptographic Security</h4>
                <p className="text-xs text-slate-300 leading-relaxed">
                  Any smartphone camera scanning the certificate's QR code instantly verifies candidate identity, grades, hours, and issue date with 100% cryptographic authentication.
                </p>
              </div>
            </div>

            <div className="mt-6 pt-4 border-t border-slate-800 flex items-center justify-between">
              <span className="text-[11px] text-slate-400">
                Automated Franchise Documentation System v3.0 • Bharatpur, Rajasthan
              </span>
              <button
                onClick={() => setShowGuideModal(false)}
                className="px-5 py-2.5 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-xs font-bold transition-all cursor-pointer shadow-md"
              >
                Got It, Let's Start!
              </button>
            </div>
          </div>
        </div>
      )}

    </header>
  );
};
